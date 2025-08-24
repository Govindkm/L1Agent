"""
Observability system for monitoring agent behavior, traces, metrics, and logs.
Integrates with OpenTelemetry for comprehensive observability.
"""

import logging
import structlog
from typing import Dict, Any, Optional, List
from datetime import datetime
from contextlib import contextmanager
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
import json


class AgentObserver:
    """Main observability class for agent monitoring"""
    
    def __init__(self, service_name: str = "multi-agent-email-system"):
        self.service_name = service_name
        self.tracer = None
        self.meter = None
        self.logger = None
        self._setup_logging()
        self._setup_tracing()
        self._setup_metrics()
    
    def _setup_logging(self):
        """Setup structured logging"""
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        
        self.logger = structlog.get_logger()
    
    def _setup_tracing(self):
        """Setup distributed tracing with OpenTelemetry"""
        resource = Resource.create({SERVICE_NAME: self.service_name})
        trace.set_tracer_provider(TracerProvider(resource=resource))
        
        # Setup Jaeger exporter if endpoint is available
        try:
            from config.settings import get_config
            config = get_config()
            
            if config.observability.jaeger_endpoint:
                jaeger_exporter = JaegerExporter(
                    agent_host_name=config.observability.jaeger_endpoint.split("://")[1].split(":")[0],
                    agent_port=int(config.observability.jaeger_endpoint.split(":")[-1]),
                )
                span_processor = BatchSpanProcessor(jaeger_exporter)
                trace.get_tracer_provider().add_span_processor(span_processor)
        except Exception as e:
            self.logger.warning("Failed to setup Jaeger exporter", error=str(e))
        
        self.tracer = trace.get_tracer(self.service_name)
    
    def _setup_metrics(self):
        """Setup metrics collection"""
        resource = Resource.create({SERVICE_NAME: self.service_name})
        metrics.set_meter_provider(MeterProvider(resource=resource))
        self.meter = metrics.get_meter(self.service_name)
        
        # Create metrics instruments
        self.agent_invocation_counter = self.meter.create_counter(
            name="agent_invocations_total",
            description="Total number of agent invocations",
            unit="1"
        )
        
        self.agent_duration_histogram = self.meter.create_histogram(
            name="agent_duration_seconds",
            description="Agent execution duration in seconds",
            unit="s"
        )
        
        self.tool_invocation_counter = self.meter.create_counter(
            name="tool_invocations_total",
            description="Total number of tool invocations",
            unit="1"
        )
        
        self.email_sent_counter = self.meter.create_counter(
            name="emails_sent_total",
            description="Total number of emails sent",
            unit="1"
        )
        
        self.error_counter = self.meter.create_counter(
            name="errors_total",
            description="Total number of errors",
            unit="1"
        )
    
    @contextmanager
    def trace_agent_execution(self, agent_name: str, operation: str, **attributes):
        """Context manager for tracing agent execution"""
        with self.tracer.start_as_current_span(f"{agent_name}.{operation}") as span:
            span.set_attributes({
                "agent.name": agent_name,
                "agent.operation": operation,
                "timestamp": datetime.now().isoformat(),
                **attributes
            })
            
            start_time = datetime.now()
            try:
                yield span
                span.set_attribute("status", "success")
                self.agent_invocation_counter.add(1, {"agent_name": agent_name, "status": "success"})
            except Exception as e:
                span.set_attribute("status", "error")
                span.set_attribute("error.message", str(e))
                span.set_attribute("error.type", type(e).__name__)
                self.agent_invocation_counter.add(1, {"agent_name": agent_name, "status": "error"})
                self.error_counter.add(1, {"error_type": type(e).__name__})
                raise
            finally:
                duration = (datetime.now() - start_time).total_seconds()
                span.set_attribute("duration_seconds", duration)
                self.agent_duration_histogram.record(duration, {"agent_name": agent_name})
    
    @contextmanager
    def trace_tool_execution(self, tool_name: str, **attributes):
        """Context manager for tracing tool execution"""
        with self.tracer.start_as_current_span(f"tool.{tool_name}") as span:
            span.set_attributes({
                "tool.name": tool_name,
                "timestamp": datetime.now().isoformat(),
                **attributes
            })
            
            try:
                yield span
                span.set_attribute("status", "success")
                self.tool_invocation_counter.add(1, {"tool_name": tool_name, "status": "success"})
            except Exception as e:
                span.set_attribute("status", "error")
                span.set_attribute("error.message", str(e))
                span.set_attribute("error.type", type(e).__name__)
                self.tool_invocation_counter.add(1, {"tool_name": tool_name, "status": "error"})
                self.error_counter.add(1, {"error_type": type(e).__name__})
                raise
    
    def log_agent_thought(self, agent_name: str, thought: str, context: Optional[Dict[str, Any]] = None):
        """Log agent thinking process for observability"""
        self.logger.info(
            "agent_thought",
            agent_name=agent_name,
            thought=thought,
            context=context or {},
            timestamp=datetime.now().isoformat()
        )
    
    def log_agent_decision(self, agent_name: str, decision: str, reasoning: str, context: Optional[Dict[str, Any]] = None):
        """Log agent decision making"""
        self.logger.info(
            "agent_decision",
            agent_name=agent_name,
            decision=decision,
            reasoning=reasoning,
            context=context or {},
            timestamp=datetime.now().isoformat()
        )
    
    def log_tool_usage(self, tool_name: str, input_data: Dict[str, Any], output_data: Optional[Dict[str, Any]] = None):
        """Log tool usage for debugging and analysis"""
        self.logger.info(
            "tool_usage",
            tool_name=tool_name,
            input_data=input_data,
            output_data=output_data,
            timestamp=datetime.now().isoformat()
        )
    
    def log_email_event(self, event_type: str, recipient: str, subject: str, status: str, metadata: Optional[Dict[str, Any]] = None):
        """Log email events"""
        self.logger.info(
            "email_event",
            event_type=event_type,
            recipient=recipient,
            subject=subject,
            status=status,
            metadata=metadata or {},
            timestamp=datetime.now().isoformat()
        )
        
        if event_type == "sent" and status == "success":
            self.email_sent_counter.add(1, {"status": "success"})
        elif event_type == "sent" and status == "error":
            self.email_sent_counter.add(1, {"status": "error"})
    
    def log_mcp_interaction(self, server_name: str, tool_name: str, action: str, result: Optional[str] = None):
        """Log MCP server interactions"""
        self.logger.info(
            "mcp_interaction",
            server_name=server_name,
            tool_name=tool_name,
            action=action,
            result=result,
            timestamp=datetime.now().isoformat()
        )
    
    def log_orchestration_event(self, event_type: str, details: Dict[str, Any]):
        """Log orchestration events"""
        self.logger.info(
            "orchestration_event",
            event_type=event_type,
            details=details,
            timestamp=datetime.now().isoformat()
        )
    
    def create_agent_context(self, agent_name: str, session_id: str, user_request: str) -> Dict[str, Any]:
        """Create context for agent execution"""
        return {
            "agent_name": agent_name,
            "session_id": session_id,
            "user_request": user_request,
            "timestamp": datetime.now().isoformat()
        }


# Global observer instance
_observer: Optional[AgentObserver] = None


def get_observer() -> AgentObserver:
    """Get the global observer instance"""
    global _observer
    if _observer is None:
        _observer = AgentObserver()
    return _observer


def reset_observer():
    """Reset the global observer (mainly for testing)"""
    global _observer
    _observer = None


class ObservableAgent:
    """Wrapper for agents that adds automatic observability"""
    
    def __init__(self, agent, name: str, observer: Optional[AgentObserver] = None):
        self.agent = agent
        self.name = name
        self.observer = observer or get_observer()
    
    def __call__(self, request: str, **kwargs) -> str:
        """Execute agent with observability"""
        with self.observer.trace_agent_execution(
            self.name,
            "execute",
            request=request,
            **kwargs
        ) as span:
            self.observer.log_agent_thought(
                self.name,
                f"Processing request: {request[:100]}...",
                {"full_request": request}
            )
            
            result = self.agent(request, **kwargs)
            
            span.set_attribute("response_length", len(str(result)))
            self.observer.log_agent_thought(
                self.name,
                f"Generated response with length: {len(str(result))}",
                {"response_preview": str(result)[:200]}
            )
            
            return result


def make_observable(agent, name: str) -> ObservableAgent:
    """Make an agent observable"""
    return ObservableAgent(agent, name)
