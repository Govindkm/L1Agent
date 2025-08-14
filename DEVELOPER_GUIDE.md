# Developer Guide: Advanced Agent Patterns 🔧

This guide covers advanced patterns and real-world scenarios for building sophisticated agents with the L1Agent library.

## 🎯 Table of Contents

- [Agent Lifecycle Patterns](#agent-lifecycle-patterns)
- [State Management Patterns](#state-management-patterns)
- [Communication Patterns](#communication-patterns)
- [Error Handling Strategies](#error-handling-strategies)
- [Performance Optimization](#performance-optimization)
- [Testing Strategies](#testing-strategies)
- [Production Deployment](#production-deployment)
- [Real-World Examples](#real-world-examples)

## 🔄 Agent Lifecycle Patterns

### 1. Stateful Agents

Agents that maintain state across multiple interactions:

```python
class StatefulAgent(BaseAgent):
    def __init__(self):
        super().__init__("StatefulAgent")
        self.conversation_history = []
        self.user_preferences = {}
    
    def process(self, state: MultiAgentState) -> Command:
        register_agent(state, "stateful_agent", "working")
        
        # Get or initialize session data
        session_id = get_custom_data(state, "session_id", "default")
        session_data = get_custom_data(state, f"session_{session_id}", {})
        
        # Update conversation history
        current_message = state["messages"][-1].content
        session_data.setdefault("history", []).append(current_message)
        
        # Process with context
        response = self.process_with_context(current_message, session_data)
        
        # Save session state
        set_custom_data(state, f"session_{session_id}", session_data)
        
        return Command(goto="__end__", update={"messages": [response]})
```

### 2. Pipeline Agents

Agents that process data through multiple stages:

```python
class PipelineAgent(BaseAgent):
    def process(self, state: MultiAgentState) -> Command:
        register_agent(state, "pipeline_agent", "working")
        
        data = state["messages"][-1].content
        
        # Stage 1: Preprocessing
        log_execution_step(state, "pipeline_agent", "preprocessing")
        processed_data = self.preprocess(data)
        
        # Stage 2: Analysis
        log_execution_step(state, "pipeline_agent", "analysis")
        analysis_result = self.analyze(processed_data)
        
        # Stage 3: Post-processing
        log_execution_step(state, "pipeline_agent", "postprocessing")
        final_result = self.postprocess(analysis_result)
        
        update_agent_status(state, "pipeline_agent", "completed", 
                          result=final_result)
        
        return Command(goto="__end__", update={"messages": [final_result]})
    
    def preprocess(self, data):
        """Stage 1: Clean and normalize data"""
        return data.strip().lower()
    
    def analyze(self, data):
        """Stage 2: Perform main analysis"""
        model = get_model()
        return model.invoke(f"Analyze this: {data}")
    
    def postprocess(self, result):
        """Stage 3: Format and validate output"""
        from langchain_core.messages import AIMessage
        return AIMessage(content=f"Analysis: {result.content}")
```

### 3. Collaborative Agents

Agents that work together on complex tasks:

```python
class CoordinatorAgent(BaseAgent):
    def process(self, state: MultiAgentState) -> Command:
        register_agent(state, "coordinator", "working")
        
        task = state["messages"][-1].content
        
        # Determine subtasks
        subtasks = self.decompose_task(task)
        
        # Assign to specialist agents
        results = {}
        for subtask_id, subtask in enumerate(subtasks):
            specialist = self.select_specialist(subtask)
            result = self.delegate_to_agent(state, specialist, subtask)
            results[subtask_id] = result
        
        # Synthesize results
        final_result = self.synthesize_results(results)
        
        update_agent_status(state, "coordinator", "completed", 
                          result=final_result)
        
        return Command(goto="__end__", update={"messages": [final_result]})
```

## 📊 State Management Patterns

### 1. Hierarchical State

Organize complex state data hierarchically:

```python
class HierarchicalStateAgent(BaseAgent):
    def process(self, state: MultiAgentState) -> Command:
        # Initialize hierarchical structure
        workspace = get_custom_data(state, "workspace", {
            "projects": {},
            "users": {},
            "tasks": {}
        })
        
        # Work with nested data
        project_id = "proj_123"
        if project_id not in workspace["projects"]:
            workspace["projects"][project_id] = {
                "name": "New Project",
                "tasks": [],
                "status": "active"
            }
        
        # Update nested state
        workspace["projects"][project_id]["tasks"].append({
            "id": "task_456",
            "description": "Process user request",
            "status": "in_progress"
        })
        
        # Save back to state
        set_custom_data(state, "workspace", workspace)
        
        return Command(goto="__end__")
```

### 2. State Versioning

Track state changes over time:

```python
class VersionedStateAgent(BaseAgent):
    def process(self, state: MultiAgentState) -> Command:
        # Get current version
        version = get_custom_data(state, "state_version", 0)
        
        # Create state snapshot
        snapshot = {
            "version": version + 1,
            "timestamp": datetime.now().isoformat(),
            "agent": "versioned_agent",
            "changes": "Processed user request",
            "data": state["messages"][-1].content
        }
        
        # Save version history
        history = get_custom_data(state, "state_history", [])
        history.append(snapshot)
        
        set_custom_data(state, "state_history", history)
        set_custom_data(state, "state_version", version + 1)
        
        return Command(goto="__end__")
```

### 3. State Validation

Ensure state consistency:

```python
class ValidatedStateAgent(BaseAgent):
    def process(self, state: MultiAgentState) -> Command:
        # Validate current state
        if not self.validate_state(state):
            self.repair_state(state)
        
        # Process with confidence
        result = self.safe_process(state)
        
        # Validate result state
        if not self.validate_state(state):
            raise ValueError("State corruption detected")
        
        return result
    
    def validate_state(self, state: MultiAgentState) -> bool:
        """Validate state consistency"""
        required_keys = ["messages", "agent_data_json", "tool_data_json"]
        return all(key in state for key in required_keys)
    
    def repair_state(self, state: MultiAgentState):
        """Repair corrupted state"""
        if "agent_data_json" not in state:
            state["agent_data_json"] = "{}"
        if "tool_data_json" not in state:
            state["tool_data_json"] = "{}"
```

## 🗣️ Communication Patterns

### 1. Agent-to-Agent Communication

Direct communication between agents:

```python
class CommunicatingAgent(BaseAgent):
    def process(self, state: MultiAgentState) -> Command:
        # Send message to another agent
        self.send_message_to_agent(state, "data_agent", {
            "request": "fetch_user_data",
            "user_id": "12345"
        })
        
        # Wait for response (in a real system, this might be async)
        response = self.wait_for_response(state, "data_agent")
        
        # Process response
        result = self.process_agent_response(response)
        
        return Command(goto="__end__", update={"messages": [result]})
    
    def send_message_to_agent(self, state, target_agent, message):
        """Send structured message to another agent"""
        messages = get_custom_data(state, "agent_messages", {})
        if target_agent not in messages:
            messages[target_agent] = []
        
        messages[target_agent].append({
            "from": self.name,
            "timestamp": datetime.now().isoformat(),
            "message": message
        })
        
        set_custom_data(state, "agent_messages", messages)
```

### 2. Event-Driven Communication

Agents that respond to events:

```python
class EventDrivenAgent(BaseAgent):
    def process(self, state: MultiAgentState) -> Command:
        # Check for events
        events = get_custom_data(state, "events", [])
        
        for event in events:
            if self.should_handle_event(event):
                self.handle_event(state, event)
        
        # Emit new event
        self.emit_event(state, {
            "type": "agent_completed",
            "agent": self.name,
            "timestamp": datetime.now().isoformat()
        })
        
        return Command(goto="__end__")
    
    def should_handle_event(self, event):
        """Determine if this agent should handle the event"""
        return event.get("type") in ["user_request", "data_updated"]
    
    def emit_event(self, state, event):
        """Emit an event for other agents"""
        events = get_custom_data(state, "events", [])
        events.append(event)
        set_custom_data(state, "events", events)
```

### 3. Pub/Sub Pattern

Publish-subscribe communication:

```python
class PublisherAgent(BaseAgent):
    def process(self, state: MultiAgentState) -> Command:
        # Publish data
        self.publish(state, "user_data_channel", {
            "user_id": "12345",
            "action": "login",
            "timestamp": datetime.now().isoformat()
        })
        
        return Command(goto="__end__")
    
    def publish(self, state, channel, data):
        """Publish data to a channel"""
        channels = get_custom_data(state, "channels", {})
        if channel not in channels:
            channels[channel] = []
        
        channels[channel].append({
            "publisher": self.name,
            "data": data,
            "timestamp": datetime.now().isoformat()
        })
        
        set_custom_data(state, "channels", channels)

class SubscriberAgent(BaseAgent):
    def process(self, state: MultiAgentState) -> Command:
        # Subscribe and process messages
        messages = self.get_messages(state, "user_data_channel")
        
        for message in messages:
            self.process_message(message)
        
        return Command(goto="__end__")
    
    def get_messages(self, state, channel):
        """Get messages from a channel"""
        channels = get_custom_data(state, "channels", {})
        return channels.get(channel, [])
```

## ⚠️ Error Handling Strategies

### 1. Graceful Degradation

Handle errors while maintaining functionality:

```python
class ResilientAgent(BaseAgent):
    def process(self, state: MultiAgentState) -> Command:
        register_agent(state, "resilient_agent", "working")
        
        try:
            # Primary processing path
            result = self.primary_process(state)
            
        except ModelNotAvailableError:
            # Fallback to simpler model
            self.log_thinking("Primary model unavailable", "Using fallback model")
            result = self.fallback_process(state)
            
        except NetworkError:
            # Use cached response
            self.log_thinking("Network error", "Using cached response")
            result = self.get_cached_response(state)
            
        except Exception as e:
            # Last resort: informative error message
            self.log_thinking(f"Unexpected error: {e}", "Providing helpful error message")
            result = self.create_error_response(str(e))
        
        update_agent_status(state, "resilient_agent", "completed", result=result)
        return Command(goto="__end__", update={"messages": [result]})
```

### 2. Circuit Breaker Pattern

Prevent cascade failures:

```python
class CircuitBreakerAgent(BaseAgent):
    def __init__(self):
        super().__init__("CircuitBreakerAgent")
        self.failure_count = 0
        self.failure_threshold = 5
        self.timeout_duration = 60  # seconds
        self.last_failure_time = 0
    
    def process(self, state: MultiAgentState) -> Command:
        if self.is_circuit_open():
            return self.handle_circuit_open(state)
        
        try:
            result = self.risky_operation(state)
            self.on_success()
            return result
            
        except Exception as e:
            self.on_failure()
            if self.should_open_circuit():
                return self.handle_circuit_open(state)
            raise
    
    def is_circuit_open(self):
        if self.failure_count >= self.failure_threshold:
            time_since_failure = time.time() - self.last_failure_time
            return time_since_failure < self.timeout_duration
        return False
    
    def on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
    
    def on_success(self):
        self.failure_count = 0
```

### 3. Retry with Backoff

Intelligent retry strategies:

```python
class RetryAgent(BaseAgent):
    def process(self, state: MultiAgentState) -> Command:
        max_retries = 3
        base_delay = 1.0
        
        for attempt in range(max_retries + 1):
            try:
                result = self.unreliable_operation(state)
                
                update_agent_status(state, "retry_agent", "completed", 
                                  result=result)
                return Command(goto="__end__", update={"messages": [result]})
                
            except RetriableError as e:
                if attempt == max_retries:
                    # Final attempt failed
                    self.log_thinking(f"All {max_retries + 1} attempts failed", 
                                    "Returning error response")
                    update_agent_status(state, "retry_agent", "failed", error=str(e))
                    raise
                
                # Calculate backoff delay
                delay = base_delay * (2 ** attempt)
                self.log_thinking(f"Attempt {attempt + 1} failed: {e}", 
                                f"Retrying in {delay} seconds")
                
                log_execution_step(state, "retry_agent", f"retry_attempt_{attempt + 1}", 
                                 {"error": str(e), "delay": delay})
                
                time.sleep(delay)
```

## 🚀 Performance Optimization

### 1. Caching Strategies

Implement intelligent caching:

```python
class CachedAgent(BaseAgent):
    def __init__(self):
        super().__init__("CachedAgent")
        self.cache_ttl = 300  # 5 minutes
    
    def process(self, state: MultiAgentState) -> Command:
        user_input = state["messages"][-1].content
        cache_key = self.generate_cache_key(user_input)
        
        # Check cache
        cached_result = self.get_from_cache(state, cache_key)
        if cached_result:
            self.log_thinking("Found cached result", "Returning cached response")
            return Command(goto="__end__", update={"messages": [cached_result]})
        
        # Process and cache
        result = self.expensive_operation(user_input)
        self.save_to_cache(state, cache_key, result)
        
        return Command(goto="__end__", update={"messages": [result]})
    
    def get_from_cache(self, state, key):
        cache = get_custom_data(state, "cache", {})
        entry = cache.get(key)
        
        if entry and not self.is_expired(entry):
            return entry["result"]
        return None
    
    def save_to_cache(self, state, key, result):
        cache = get_custom_data(state, "cache", {})
        cache[key] = {
            "result": result,
            "timestamp": time.time()
        }
        set_custom_data(state, "cache", cache)
    
    def is_expired(self, entry):
        return time.time() - entry["timestamp"] > self.cache_ttl
```

### 2. Async Processing

Handle long-running operations:

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

class AsyncAgent(BaseAgent):
    def __init__(self):
        super().__init__("AsyncAgent")
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    def process(self, state: MultiAgentState) -> Command:
        register_agent(state, "async_agent", "working")
        
        # Start background tasks
        task_ids = []
        for task_data in self.get_tasks(state):
            task_id = self.start_background_task(state, task_data)
            task_ids.append(task_id)
        
        # Return immediately with task tracking
        set_custom_data(state, "background_tasks", task_ids)
        
        update_agent_status(state, "async_agent", "completed", 
                          action="started_background_tasks")
        
        return Command(goto="__end__", update={
            "messages": [AIMessage(content="Tasks started in background")]
        })
    
    def start_background_task(self, state, task_data):
        """Start a background task and return task ID"""
        import uuid
        task_id = str(uuid.uuid4())
        
        # In a real implementation, this would use proper async handling
        future = self.executor.submit(self.process_task, task_data)
        
        # Store task reference
        tasks = get_custom_data(state, "active_tasks", {})
        tasks[task_id] = {
            "status": "running",
            "future": future,
            "started": time.time()
        }
        set_custom_data(state, "active_tasks", tasks)
        
        return task_id
```

### 3. Resource Management

Manage computational resources:

```python
class ResourceManagedAgent(BaseAgent):
    def __init__(self):
        super().__init__("ResourceManagedAgent")
        self.max_memory_mb = 512
        self.max_processing_time = 30
    
    def process(self, state: MultiAgentState) -> Command:
        # Check resource availability
        if not self.check_resources():
            return self.handle_resource_shortage(state)
        
        # Monitor resource usage during processing
        with self.resource_monitor() as monitor:
            result = self.resource_intensive_operation(state)
            
            # Log resource usage
            log_execution_step(state, "resource_agent", "resource_usage", {
                "memory_used_mb": monitor.memory_used,
                "processing_time_s": monitor.processing_time
            })
        
        return Command(goto="__end__", update={"messages": [result]})
    
    def check_resources(self):
        """Check if sufficient resources are available"""
        import psutil
        
        memory_available = psutil.virtual_memory().available / 1024 / 1024
        return memory_available > self.max_memory_mb
    
    def resource_monitor(self):
        """Context manager for monitoring resource usage"""
        import psutil
        import time
        
        class ResourceMonitor:
            def __enter__(self):
                self.start_time = time.time()
                self.start_memory = psutil.Process().memory_info().rss / 1024 / 1024
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                self.processing_time = time.time() - self.start_time
                end_memory = psutil.Process().memory_info().rss / 1024 / 1024
                self.memory_used = end_memory - self.start_memory
        
        return ResourceMonitor()
```

## 🧪 Testing Strategies

### 1. Unit Testing Agents

```python
import unittest
from unittest.mock import Mock, patch

class TestMyAgent(unittest.TestCase):
    def setUp(self):
        self.agent = MyAgent()
        self.test_state = {
            "messages": [HumanMessage(content="test input")],
            "agent_data_json": "{}",
            "tool_data_json": "{}",
            "execution_history": [],
            "task_status": "active"
        }
    
    def test_successful_processing(self):
        """Test normal processing flow"""
        with patch('config.model_config.get_model') as mock_model:
            mock_model.return_value.invoke.return_value.content = "test response"
            
            result = self.agent.process(self.test_state)
            
            self.assertEqual(result.goto, "__end__")
            self.assertIn("messages", result.update)
            self.assertEqual(result.update["messages"][0].content, "test response")
    
    def test_error_handling(self):
        """Test error handling"""
        with patch('config.model_config.get_model') as mock_model:
            mock_model.return_value.invoke.side_effect = Exception("Test error")
            
            result = self.agent.process(self.test_state)
            
            self.assertEqual(result.goto, "__end__")
            self.assertIn("error", result.update["messages"][0].content.lower())
    
    def test_state_tracking(self):
        """Test state tracking functionality"""
        with patch('config.model_config.get_model') as mock_model:
            mock_model.return_value.invoke.return_value.content = "success"
            
            self.agent.process(self.test_state)
            
            # Verify agent was registered
            from utils.state import get_execution_summary
            summary = get_execution_summary(self.test_state)
            self.assertIn("my_agent", summary["agents"])
```

### 2. Integration Testing

```python
class TestAgentIntegration(unittest.TestCase):
    def test_full_system_flow(self):
        """Test complete system integration"""
        from system import MultiAgentSystem
        from config.model_config import configure_ollama_model
        
        # Setup
        configure_ollama_model("llama3:latest")
        system = MultiAgentSystem()
        
        # Test request
        result = system.process_request("Calculate 5 + 3")
        
        # Verify result
        self.assertIsNotNone(result)
        self.assertIn("messages", result)
        
        # Check that calculator agent was used
        summary = get_execution_summary(result)
        self.assertTrue(any("calculator" in agent.lower() 
                          for agent in summary.get("agents", {})))
```

### 3. Mock Testing

```python
class TestWithMocks(unittest.TestCase):
    def test_agent_with_external_service(self):
        """Test agent that calls external services"""
        
        with patch('requests.get') as mock_get:
            # Mock external API response
            mock_response = Mock()
            mock_response.json.return_value = {"result": "mocked data"}
            mock_get.return_value = mock_response
            
            agent = ExternalServiceAgent()
            result = agent.process(self.test_state)
            
            # Verify external service was called
            mock_get.assert_called_once()
            self.assertIn("mocked data", str(result.update))
```

## 🚀 Production Deployment

### 1. Configuration Management

```python
# config/production.py
import os
from dataclasses import dataclass

@dataclass
class ProductionConfig:
    # Model configuration
    model_provider: str = os.getenv("MODEL_PROVIDER", "ollama")
    model_name: str = os.getenv("MODEL_NAME", "llama3:latest")
    
    # Performance settings
    max_concurrent_agents: int = int(os.getenv("MAX_CONCURRENT_AGENTS", "10"))
    cache_ttl_seconds: int = int(os.getenv("CACHE_TTL", "300"))
    
    # Monitoring
    enable_metrics: bool = os.getenv("ENABLE_METRICS", "true").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Resource limits
    max_memory_mb: int = int(os.getenv("MAX_MEMORY_MB", "1024"))
    max_processing_time_s: int = int(os.getenv("MAX_PROCESSING_TIME", "60"))

# Usage
config = ProductionConfig()
configure_ollama_model(config.model_name)
setup_logging(log_level=config.log_level)
```

### 2. Health Checks

```python
class HealthCheckAgent(BaseAgent):
    def health_check(self) -> dict:
        """Perform comprehensive health check"""
        checks = {
            "model_available": self.check_model(),
            "memory_usage": self.check_memory(),
            "disk_space": self.check_disk(),
            "response_time": self.check_response_time()
        }
        
        return {
            "status": "healthy" if all(checks.values()) else "unhealthy",
            "checks": checks,
            "timestamp": datetime.now().isoformat()
        }
    
    def check_model(self) -> bool:
        try:
            model = get_model()
            test_response = model.invoke("health check")
            return bool(test_response.content)
        except:
            return False
```

### 3. Monitoring and Metrics

```python
class MetricsAgent(BaseAgent):
    def __init__(self):
        super().__init__("MetricsAgent")
        self.metrics = {
            "requests_processed": 0,
            "errors_occurred": 0,
            "average_response_time": 0.0
        }
    
    def process(self, state: MultiAgentState) -> Command:
        start_time = time.time()
        
        try:
            result = self.main_process(state)
            self.metrics["requests_processed"] += 1
            
        except Exception as e:
            self.metrics["errors_occurred"] += 1
            raise
        
        finally:
            # Update response time metric
            response_time = time.time() - start_time
            self.update_average_response_time(response_time)
            
            # Log metrics
            log_execution_step(state, "metrics_agent", "metrics_update", 
                             self.metrics.copy())
        
        return result
    
    def update_average_response_time(self, new_time):
        """Update rolling average response time"""
        alpha = 0.1  # Smoothing factor
        self.metrics["average_response_time"] = (
            alpha * new_time + 
            (1 - alpha) * self.metrics["average_response_time"]
        )
```

## 🌟 Real-World Examples

### 1. Customer Service Agent

```python
class CustomerServiceAgent(BaseAgent):
    def __init__(self):
        super().__init__("CustomerServiceAgent")
        self.knowledge_base = self.load_knowledge_base()
    
    def process(self, state: MultiAgentState) -> Command:
        register_agent(state, "customer_service", "working")
        
        # Extract customer intent
        customer_query = state["messages"][-1].content
        intent = self.classify_intent(customer_query)
        
        log_execution_step(state, "customer_service", "intent_classification", 
                         {"intent": intent, "query": customer_query})
        
        # Route based on intent
        if intent == "technical_support":
            response = self.handle_technical_support(customer_query)
        elif intent == "billing_inquiry":
            response = self.handle_billing_inquiry(customer_query)
        elif intent == "general_information":
            response = self.handle_general_information(customer_query)
        else:
            response = self.escalate_to_human(customer_query)
        
        update_agent_status(state, "customer_service", "completed", 
                          result=response, action=f"handled_{intent}")
        
        return Command(goto="__end__", update={"messages": [response]})
    
    def classify_intent(self, query):
        """Classify customer intent using AI"""
        model = get_model()
        classification_prompt = f"""
        Classify this customer query into one of these categories:
        - technical_support
        - billing_inquiry  
        - general_information
        - escalate_to_human
        
        Query: {query}
        
        Respond with just the category name.
        """
        
        response = model.invoke(classification_prompt)
        return response.content.strip().lower()
```

### 2. Data Analysis Agent

```python
class DataAnalysisAgent(BaseAgent):
    def process(self, state: MultiAgentState) -> Command:
        register_agent(state, "data_analysis", "working")
        
        # Get data request
        request = self.parse_data_request(state["messages"][-1].content)
        
        # Fetch data
        register_tool(state, "data_fetcher")
        raw_data = self.fetch_data(request)
        update_tool_data(state, "data_fetcher", result=f"Fetched {len(raw_data)} records")
        
        # Analyze data
        register_tool(state, "data_analyzer")
        analysis = self.analyze_data(raw_data, request["analysis_type"])
        update_tool_data(state, "data_analyzer", result=analysis["summary"])
        
        # Generate visualization
        register_tool(state, "chart_generator")
        chart = self.generate_chart(analysis, request.get("chart_type", "bar"))
        update_tool_data(state, "chart_generator", result="Chart generated")
        
        # Create report
        report = self.create_report(analysis, chart)
        
        update_agent_status(state, "data_analysis", "completed", result=report)
        
        return Command(goto="__end__", update={"messages": [report]})
    
    def fetch_data(self, request):
        """Simulate data fetching"""
        # In real implementation, this would connect to databases, APIs, etc.
        return [{"id": i, "value": i * 2} for i in range(100)]
    
    def analyze_data(self, data, analysis_type):
        """Perform statistical analysis"""
        if analysis_type == "summary":
            return {
                "count": len(data),
                "mean": sum(item["value"] for item in data) / len(data),
                "summary": f"Analyzed {len(data)} data points"
            }
        # Add more analysis types as needed
```

### 3. Content Generation Agent

```python
class ContentGenerationAgent(BaseAgent):
    def process(self, state: MultiAgentState) -> Command:
        register_agent(state, "content_generation", "working")
        
        # Parse content request
        request = self.parse_content_request(state["messages"][-1].content)
        
        # Generate outline
        log_execution_step(state, "content_generation", "outline_generation")
        outline = self.generate_outline(request)
        
        # Generate sections
        sections = []
        for section_title in outline:
            log_execution_step(state, "content_generation", "section_generation", 
                             {"section": section_title})
            section_content = self.generate_section(section_title, request)
            sections.append({
                "title": section_title,
                "content": section_content
            })
        
        # Compile final content
        final_content = self.compile_content(request["title"], sections)
        
        # Quality check
        register_tool(state, "quality_checker")
        quality_score = self.check_quality(final_content)
        update_tool_data(state, "quality_checker", result=f"Quality score: {quality_score}")
        
        if quality_score < 0.8:
            # Revise content
            log_execution_step(state, "content_generation", "content_revision")
            final_content = self.revise_content(final_content, quality_score)
        
        update_agent_status(state, "content_generation", "completed", 
                          result=final_content)
        
        return Command(goto="__end__", update={"messages": [final_content]})
```

---

This developer guide provides the patterns and strategies needed to build sophisticated, production-ready agents with the L1Agent library. Each pattern can be adapted and combined to meet specific requirements.
