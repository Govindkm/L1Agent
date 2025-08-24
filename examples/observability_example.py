"""
Example: Observability and monitoring demonstration
Shows how the system tracks agent behavior and provides insights
"""

import os
import sys
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src import (
    create_orchestrator, 
    create_email_agent, 
    get_observer, 
    make_observable
)


def observability_examples():
    """Demonstrate observability features"""
    
    print("=== Multi-Agent System - Observability Examples ===\n")
    
    # Get observer instance
    observer = get_observer()
    
    # Create agents
    orchestrator = create_orchestrator("ObservabilityOrchestrator")
    email_agent = create_email_agent("ObservabilityEmailAgent")
    
    print("1. Agent execution with tracing...")
    
    # Example 1: Traced execution
    with observer.trace_agent_execution(
        "example_agent",
        "demonstrate_tracing",
        example_param="test_value"
    ) as span:
        
        print("   - Starting traced operation...")
        observer.log_agent_thought(
            "example_agent",
            "Beginning demonstration of observability features",
            {"operation": "demo", "step": 1}
        )
        
        # Simulate some work
        time.sleep(0.1)
        
        observer.log_agent_decision(
            "example_agent",
            "continue_demo",
            "All systems operational, proceeding with demo",
            {"confidence": 0.95}
        )
        
        span.set_attribute("demo_completed", True)
        print("   ✓ Traced operation completed!")
    
    # Example 2: Tool usage tracking
    print("\n2. Tool usage tracking...")
    
    tool_request = """
    Create a simple email to demonstrate tool usage tracking:
    - Recipient: demo@example.com
    - Topic: Observability Demo
    - Purpose: Testing the monitoring system
    """
    
    # This will automatically be traced due to the observable agent wrapper
    response = email_agent(tool_request)
    print("   ✓ Tool usage tracked automatically!")
    
    # Example 3: Orchestration tracking
    print("\n3. Orchestration event tracking...")
    
    complex_request = """
    Please coordinate this multi-step task:
    1. Validate email: test@observability-demo.com
    2. Create a monitoring status email
    3. Explain what observability features are being demonstrated
    """
    
    response = orchestrator(complex_request, "observability_demo")
    print("   ✓ Orchestration events tracked!")
    
    # Example 4: Error handling and tracking
    print("\n4. Error tracking demonstration...")
    
    try:
        error_request = "Send email to invalid-email-format without @ symbol"
        response = email_agent(error_request)
    except Exception as e:
        print(f"   ✓ Error tracked: {type(e).__name__}")
    
    # Example 5: Custom observability
    print("\n5. Custom observability logging...")
    
    # Log custom events
    observer.log_email_event(
        "demo_event",
        "demo@example.com", 
        "Observability Demo Email",
        "simulated",
        {"demo": True, "timestamp": time.time()}
    )
    
    observer.log_mcp_interaction(
        "demo_server",
        "demo_tool",
        "simulated_action",
        "Demonstration of MCP interaction logging"
    )
    
    observer.log_orchestration_event(
        "demo_orchestration",
        {
            "event_type": "custom_demo",
            "description": "Demonstrating custom orchestration logging",
            "participants": ["email_agent", "orchestrator"],
            "success": True
        }
    )
    
    print("   ✓ Custom events logged!")
    
    print("\n=== Observability examples completed ===")
    print(f"Check the log file: {observer.logger}")


def demonstrate_metrics():
    """Demonstrate metrics collection"""
    
    print("\n=== Metrics Collection Demo ===\n")
    
    observer = get_observer()
    
    # Simulate multiple operations to generate metrics
    email_agent = create_email_agent("MetricsEmailAgent")
    
    requests = [
        "Create a welcome email for new team member",
        "Validate email: metrics@demo.com",
        "Create a project update email",
        "Send thank you email (simulated)"
    ]
    
    print("Generating metrics data...")
    
    for i, request in enumerate(requests, 1):
        print(f"   Processing request {i}/{len(requests)}")
        
        try:
            with observer.trace_agent_execution(
                "metrics_demo_agent",
                f"request_{i}",
                request_id=i
            ):
                # Simulate processing
                time.sleep(0.05)
                response = email_agent(request)
                
                # Log metrics
                observer.agent_invocation_counter.add(1, {
                    "agent_name": "metrics_demo_agent",
                    "status": "success"
                })
                
        except Exception as e:
            observer.error_counter.add(1, {
                "error_type": type(e).__name__
            })
    
    print("✓ Metrics data generated!")
    print("   Note: In a real deployment, metrics would be exported to monitoring systems")


def show_logging_output():
    """Show current logging configuration and recent entries"""
    
    print("\n=== Logging Configuration ===\n")
    
    observer = get_observer()
    
    print("Structured logging is enabled with the following processors:")
    print("   - Log level filtering")
    print("   - Timestamp addition")
    print("   - JSON formatting")
    print("   - Exception info capture")
    
    # Log some sample entries
    logger = observer.logger
    
    logger.info("observability_demo_started", demo_type="comprehensive")
    logger.debug("debug_information", detail="This is a debug message")
    logger.warning("demo_warning", message="This is a demonstration warning")
    
    print("\n✓ Sample log entries generated")
    print("   Check the configured log file for structured output")


if __name__ == "__main__":
    # Run observability examples
    observability_examples()
    
    # Demonstrate metrics
    demonstrate_metrics()
    
    # Show logging configuration
    show_logging_output()
    
    print("\n" + "="*60)
    print("Observability demonstration completed!")
    print("Key features demonstrated:")
    print("   ✓ Distributed tracing")
    print("   ✓ Metrics collection")
    print("   ✓ Structured logging")
    print("   ✓ Agent behavior tracking")
    print("   ✓ Error monitoring")
    print("   ✓ Custom event logging")
