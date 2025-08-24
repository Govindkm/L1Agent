"""
Example: Orchestrator agent coordinating multiple operations
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src import create_orchestrator, get_observer


def orchestrator_examples():
    """Demonstrate orchestrator functionality"""
    
    # Initialize observer for tracking
    observer = get_observer()
    
    # Create orchestrator
    orchestrator = create_orchestrator("ExampleOrchestrator")
    
    print("=== Multi-Agent System - Orchestrator Examples ===\n")
    
    # Example 1: Complex email workflow
    print("1. Complex email workflow coordination...")
    
    complex_request = """
    I need to organize a project kickoff meeting. Please:
    1. Create a professional meeting invitation email
    2. The meeting is for "Project Phoenix Kickoff"
    3. Recipients should be: team-lead@company.com, developer1@company.com
    4. Include agenda: project overview, timeline, team introductions
    5. Validate all email addresses before sending
    """
    
    try:
        response = orchestrator(complex_request, "workflow_1")
        print("✓ Complex workflow completed successfully!")
        print(f"Response: {response[:300]}...\n")
    except Exception as e:
        print(f"✗ Failed to complete workflow: {e}\n")
    
    # Example 2: Multi-step operation
    print("2. Multi-step email operation...")
    
    multistep_request = """
    Help me with this email scenario:
    1. First validate these emails: john@test.com, invalid-email, sarah@company.com
    2. Then create a project update email for the valid recipients
    3. The update should be about "Q1 Development Progress" 
    4. Include information about completed features and upcoming milestones
    5. Use a professional but approachable tone
    """
    
    try:
        response = orchestrator(multistep_request, "workflow_2")
        print("✓ Multi-step operation completed!")
        print(f"Response: {response[:300]}...\n")
    except Exception as e:
        print(f"✗ Failed to complete multi-step operation: {e}\n")
    
    # Example 3: Decision making and routing
    print("3. Testing orchestrator's decision making...")
    
    decision_request = """
    I want to send a thank you email to our client after the successful project delivery.
    The client's email is client@company.com and the project was "Website Redesign".
    Please create appropriate content and validate the email address.
    """
    
    try:
        response = orchestrator(decision_request, "workflow_3")
        print("✓ Decision making and routing successful!")
        print(f"Response: {response[:300]}...\n")
    except Exception as e:
        print(f"✗ Failed to complete decision making: {e}\n")
    
    print("=== Orchestrator examples completed ===")


def test_workflow_execution():
    """Test predefined workflow execution"""
    
    orchestrator = create_orchestrator("WorkflowOrchestrator")
    
    print("=== Testing Workflow Execution ===\n")
    
    # Define a workflow
    workflow_steps = [
        {
            "type": "email",
            "request": "Validate email: test@example.com",
            "description": "Validate recipient email"
        },
        {
            "type": "email", 
            "request": "Create a welcome email for new team member joining the development team",
            "description": "Create welcome email content"
        }
    ]
    
    try:
        result = orchestrator.execute_workflow("welcome_workflow", workflow_steps, "test_session")
        print("✓ Workflow executed successfully!")
        print(f"Result: {result}")
    except Exception as e:
        print(f"✗ Workflow execution failed: {e}")


if __name__ == "__main__":
    # Run orchestrator examples
    orchestrator_examples()
    
    # Test workflow execution
    print("\n" + "="*50)
    test_workflow_execution()
