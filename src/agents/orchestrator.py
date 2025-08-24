"""
Orchestrator agent responsible for managing and coordinating multiple specialized agents.
Uses AI to route requests to appropriate agents and coordinate multi-agent workflows.
"""

from typing import Dict, Any, List, Optional
import json
import logging
from strands import tool
from agents.email_agent import email_agent_tool, create_email_agent
from mcp_clients import get_mcp_manager
from observability import get_observer, make_observable
from providers import get_model_provider
from config.settings import get_config


# Orchestrator System Prompt
ORCHESTRATOR_SYSTEM_PROMPT = """
You are an intelligent Orchestrator Agent responsible for coordinating multiple specialized agents to fulfill user requests.

Your primary responsibilities are:
1. Analyze incoming user requests to understand their intent and requirements
2. Route requests to the most appropriate specialized agent(s)
3. Coordinate multi-agent workflows when requests require multiple capabilities
4. Combine results from multiple agents into coherent responses
5. Handle complex scenarios that require sequential or parallel agent execution
6. Provide clear status updates and explanations of your decision-making process

Available Specialized Agents:
1. Email Agent (email_agent_tool):
   - Email content creation for various purposes
   - Email sending to single/multiple recipients with CC/BCC
   - Email address validation
   - Professional email composition

2. MCP Tools (via MCP clients):
   - GitHub integration (repositories, issues, pull requests)
   - Azure DevOps integration (work items, projects)
   - File system operations (read, write, list files)

Agent Routing Guidelines:
- For email-related requests (composing, sending, validating): Use Email Agent
- For GitHub operations (repos, issues, PRs): Use GitHub MCP tools
- For Azure DevOps operations (work items, projects): Use ADO MCP tools
- For file operations: Use filesystem MCP tools
- For complex requests: Break down into subtasks and coordinate multiple agents

Decision-Making Process:
1. Analyze the user request to identify required capabilities
2. Determine which agent(s) can fulfill the request
3. Plan the execution strategy (sequential vs parallel)
4. Execute the plan using appropriate agents
5. Combine and present results clearly

Communication Guidelines:
- Always explain your routing decisions
- Provide status updates during multi-step operations
- Combine agent outputs into coherent responses
- Handle errors gracefully and provide alternatives
- Ask for clarification when requests are ambiguous

You are the central coordinator - make intelligent decisions about how to best fulfill user requests using available agents and tools.
"""


class OrchestratorAgent:
    """Main orchestrator agent that coordinates specialized agents"""
    
    def __init__(self, name: str = "Orchestrator"):
        self.name = name
        self.config = get_config()
        self.observer = get_observer()
        self.logger = logging.getLogger(f"{self.__class__.__name__}.{name}")
        self.mcp_manager = get_mcp_manager()
        
        # Collect all available tools
        available_tools = [email_agent_tool]
        
        # Add MCP tools if available
        try:
            mcp_tools = self.mcp_manager.get_all_tools()
            available_tools.extend(mcp_tools)
            self.logger.info(f"Added {len(mcp_tools)} MCP tools to orchestrator")
        except Exception as e:
            self.logger.warning(f"Failed to load MCP tools: {e}")
        
        # Create the underlying agent
        provider = get_model_provider(self.config.model)
        
        self.agent = provider.create_agent(
            system_prompt=ORCHESTRATOR_SYSTEM_PROMPT,
            tools=available_tools,
            callback_handler=None  # Suppress intermediate output for cleaner experience
        )
        
        # Make agent observable
        self.observable_agent = make_observable(self.agent, self.name)
        
        # Track active workflows
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
    
    def __call__(self, request: str, session_id: Optional[str] = None, **kwargs) -> str:
        """Process user requests through agent orchestration"""
        
        session_id = session_id or "default"
        
        with self.observer.trace_agent_execution(
            self.name,
            "orchestrate",
            request=request[:100],
            session_id=session_id
        ) as span:
            
            self.observer.log_orchestration_event("request_received", {
                "request": request,
                "session_id": session_id
            })
            
            # Analyze request and route to appropriate agent(s)
            response = self.observable_agent(request, **kwargs)
            
            span.set_attribute("response_generated", True)
            span.set_attribute("response_length", len(str(response)))
            
            self.observer.log_orchestration_event("request_completed", {
                "session_id": session_id,
                "response_length": len(str(response))
            })
            
            return response
    
    def execute_workflow(self, workflow_name: str, steps: List[Dict[str, Any]], session_id: str = "default") -> Dict[str, Any]:
        """Execute a predefined workflow with multiple steps"""
        
        with self.observer.trace_agent_execution(
            self.name,
            "execute_workflow",
            workflow_name=workflow_name,
            steps_count=len(steps)
        ) as span:
            
            workflow_id = f"{session_id}_{workflow_name}"
            self.active_workflows[workflow_id] = {
                "name": workflow_name,
                "steps": steps,
                "status": "running",
                "results": []
            }
            
            self.observer.log_orchestration_event("workflow_started", {
                "workflow_name": workflow_name,
                "workflow_id": workflow_id,
                "steps_count": len(steps)
            })
            
            try:
                results = []
                for i, step in enumerate(steps):
                    self.observer.log_orchestration_event("step_started", {
                        "workflow_id": workflow_id,
                        "step_index": i,
                        "step_type": step.get("type"),
                        "step_description": step.get("description")
                    })
                    
                    # Execute step based on type
                    if step["type"] == "email":
                        result = self._execute_email_step(step)
                    elif step["type"] == "mcp":
                        result = self._execute_mcp_step(step)
                    elif step["type"] == "orchestrate":
                        result = self(step["request"], session_id)
                    else:
                        result = {"error": f"Unknown step type: {step['type']}"}
                    
                    results.append(result)
                    self.active_workflows[workflow_id]["results"] = results
                    
                    self.observer.log_orchestration_event("step_completed", {
                        "workflow_id": workflow_id,
                        "step_index": i,
                        "result": str(result)[:200]
                    })
                
                self.active_workflows[workflow_id]["status"] = "completed"
                
                workflow_result = {
                    "workflow_id": workflow_id,
                    "status": "completed",
                    "results": results
                }
                
                span.set_attribute("workflow_completed", True)
                
                self.observer.log_orchestration_event("workflow_completed", {
                    "workflow_id": workflow_id,
                    "total_steps": len(steps)
                })
                
                return workflow_result
                
            except Exception as e:
                self.active_workflows[workflow_id]["status"] = "failed"
                self.active_workflows[workflow_id]["error"] = str(e)
                
                span.set_attribute("workflow_failed", True)
                span.set_attribute("error", str(e))
                
                self.observer.log_orchestration_event("workflow_failed", {
                    "workflow_id": workflow_id,
                    "error": str(e)
                })
                
                return {
                    "workflow_id": workflow_id,
                    "status": "failed",
                    "error": str(e)
                }
    
    def _execute_email_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an email-related workflow step"""
        try:
            email_agent = create_email_agent()
            request = step.get("request", "")
            return {"result": email_agent(request)}
        except Exception as e:
            return {"error": f"Email step failed: {str(e)}"}
    
    def _execute_mcp_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an MCP-related workflow step"""
        try:
            server_name = step.get("server")
            tool_name = step.get("tool")
            arguments = step.get("arguments", {})
            
            client = self.mcp_manager.get_client(server_name)
            if not client:
                return {"error": f"MCP client '{server_name}' not found"}
            
            result = client.call_tool(tool_name, arguments)
            return {"result": result}
        except Exception as e:
            return {"error": f"MCP step failed: {str(e)}"}
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get the status of an active workflow"""
        return self.active_workflows.get(workflow_id, {"error": "Workflow not found"})
    
    def list_active_workflows(self) -> Dict[str, Dict[str, Any]]:
        """List all active workflows"""
        return self.active_workflows.copy()


# Strands tool wrapper for the orchestrator
@tool
def orchestrator_tool(request: str, session_id: str = "default") -> str:
    """
    Main orchestrator tool that coordinates multiple agents to fulfill complex requests.
    
    Args:
        request: Natural language request that may require multiple agents
        session_id: Session identifier for workflow tracking
        
    Returns:
        JSON string with the orchestrated response
    """
    observer = get_observer()
    
    with observer.trace_tool_execution("orchestrator_tool", request=request[:100]):
        
        observer.log_tool_usage("orchestrator_tool", {
            "request": request,
            "session_id": session_id
        })
        
        # Create orchestrator instance
        orchestrator = OrchestratorAgent()
        
        # Process the request
        result = orchestrator(request, session_id)
        
        observer.log_tool_usage("orchestrator_tool", {
            "request": request[:100],
            "session_id": session_id
        }, {
            "response_length": len(str(result))
        })
        
        return result


def create_orchestrator(name: str = "Orchestrator") -> OrchestratorAgent:
    """Factory function to create an orchestrator agent"""
    return OrchestratorAgent(name)
