"""
Example: MCP integration for external services (GitHub, Azure DevOps)
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src import get_mcp_manager, create_orchestrator


def mcp_integration_examples():
    """Demonstrate MCP integration functionality"""
    
    print("=== Multi-Agent System - MCP Integration Examples ===\n")
    
    # Get MCP manager
    mcp_manager = get_mcp_manager()
    
    print(f"Available MCP clients: {list(mcp_manager.clients.keys())}")
    
    # Create orchestrator with MCP capabilities
    orchestrator = create_orchestrator("MCPOrchestrator")
    
    # Example 1: File operations
    print("\n1. File operations via MCP...")
    
    file_request = """
    Please help me with file operations:
    1. List the contents of the current directory
    2. If there's a README.md file, read its contents
    """
    
    try:
        response = orchestrator(file_request, "mcp_file_session")
        print("✓ File operations completed!")
        print(f"Response: {response[:300]}...")
    except Exception as e:
        print(f"✗ File operations failed: {e}")
    
    # Example 2: GitHub integration (if configured)
    print("\n2. GitHub integration example...")
    
    github_request = """
    If GitHub MCP is available, please:
    1. Show me information about a repository
    2. List any open issues
    Note: This will only work if GitHub MCP server is configured
    """
    
    try:
        response = orchestrator(github_request, "mcp_github_session")
        print("✓ GitHub integration attempted!")
        print(f"Response: {response[:300]}...")
    except Exception as e:
        print(f"✗ GitHub integration failed: {e}")
        print("Note: GitHub MCP server may not be configured")
    
    # Example 3: Combined email and MCP workflow
    print("\n3. Combined email and MCP workflow...")
    
    combined_request = """
    Please help me with this workflow:
    1. Read the project README file to understand the project
    2. Create a project summary email based on the README content
    3. The email should be suitable for sending to stakeholders
    4. Validate the stakeholder email: stakeholder@company.com
    """
    
    try:
        response = orchestrator(combined_request, "mcp_combined_session")
        print("✓ Combined workflow completed!")
        print(f"Response: {response[:300]}...")
    except Exception as e:
        print(f"✗ Combined workflow failed: {e}")
    
    print("\n=== MCP Integration examples completed ===")


def test_direct_mcp_clients():
    """Test direct MCP client interactions"""
    
    print("\n=== Testing Direct MCP Client Interactions ===\n")
    
    mcp_manager = get_mcp_manager()
    
    # Test filesystem client
    filesystem_client = mcp_manager.get_client("filesystem")
    if filesystem_client:
        print("Testing filesystem client...")
        try:
            tools = filesystem_client.list_tools()
            print(f"✓ Filesystem client has {len(tools)} tools available")
        except Exception as e:
            print(f"✗ Filesystem client test failed: {e}")
    else:
        print("✗ Filesystem client not available")
    
    # Test GitHub client (if configured)
    github_client = mcp_manager.get_client("github")
    if github_client:
        print("\nTesting GitHub client...")
        try:
            tools = github_client.list_tools()
            print(f"✓ GitHub client has {len(tools)} tools available")
        except Exception as e:
            print(f"✗ GitHub client test failed: {e}")
    else:
        print("GitHub client not configured (this is expected if not set up)")
    
    # Test Azure DevOps client (if configured)
    ado_client = mcp_manager.get_client("ado")
    if ado_client:
        print("\nTesting Azure DevOps client...")
        try:
            tools = ado_client.list_tools()
            print(f"✓ ADO client has {len(tools)} tools available")
        except Exception as e:
            print(f"✗ ADO client test failed: {e}")
    else:
        print("Azure DevOps client not configured (this is expected if not set up)")


if __name__ == "__main__":
    # Run MCP integration examples
    mcp_integration_examples()
    
    # Test direct MCP clients
    test_direct_mcp_clients()
