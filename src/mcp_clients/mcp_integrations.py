"""
MCP (Model Context Protocol) clients for external service integrations.
Supports GitHub, Azure DevOps, and other external services through MCP servers.
"""

from typing import Dict, Any, Optional, List
import logging
from mcp import stdio_client, StdioServerParameters
from mcp.client.sse import sse_client
from strands.tools.mcp import MCPClient
from observability import get_observer
from config.settings import get_config


class BaseMCPClient:
    """Base class for MCP client implementations"""
    
    def __init__(self, server_name: str, connection_params: Dict[str, Any]):
        self.server_name = server_name
        self.connection_params = connection_params
        self.observer = get_observer()
        self.logger = logging.getLogger(f"{self.__class__.__name__}.{server_name}")
        self._client = None
    
    def connect(self):
        """Connect to the MCP server"""
        raise NotImplementedError
    
    def disconnect(self):
        """Disconnect from the MCP server"""
        if self._client:
            self._client.__exit__(None, None, None)
            self._client = None
    
    def list_tools(self) -> List[Any]:
        """List available tools from the MCP server"""
        if not self._client:
            self.connect()
        
        try:
            with self.observer.trace_tool_execution("mcp_list_tools", server=self.server_name):
                tools = self._client.list_tools_sync()
                self.observer.log_mcp_interaction(
                    self.server_name, 
                    "list_tools", 
                    "success", 
                    f"Found {len(tools)} tools"
                )
                return tools
        except Exception as e:
            self.observer.log_mcp_interaction(
                self.server_name,
                "list_tools", 
                "error",
                str(e)
            )
            self.logger.error(f"Failed to list tools from {self.server_name}: {e}")
            raise
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the MCP server"""
        if not self._client:
            self.connect()
        
        try:
            with self.observer.trace_tool_execution(
                "mcp_call_tool", 
                server=self.server_name,
                tool_name=tool_name,
                **arguments
            ):
                result = self._client.call_tool_sync(
                    tool_use_id=f"{self.server_name}-{tool_name}",
                    name=tool_name,
                    arguments=arguments
                )
                
                self.observer.log_mcp_interaction(
                    self.server_name,
                    tool_name,
                    "call_success",
                    "Tool executed successfully"
                )
                
                return result
        except Exception as e:
            self.observer.log_mcp_interaction(
                self.server_name,
                tool_name,
                "call_error", 
                str(e)
            )
            self.logger.error(f"Failed to call tool {tool_name} on {self.server_name}: {e}")
            raise


class GitHubMCPClient(BaseMCPClient):
    """MCP client for GitHub integration"""
    
    def __init__(self, connection_params: Optional[Dict[str, Any]] = None):
        params = connection_params or {}
        super().__init__("github", params)
    
    def connect(self):
        """Connect to GitHub MCP server"""
        try:
            if "server_url" in self.connection_params:
                # HTTP-based connection
                self._client = MCPClient(
                    lambda: sse_client(self.connection_params["server_url"])
                )
            else:
                # stdio-based connection (default)
                self._client = MCPClient(lambda: stdio_client(
                    StdioServerParameters(
                        command="uvx",
                        args=["github-mcp-server@latest"]
                    )
                ))
            
            self._client.__enter__()
            self.logger.info(f"Connected to GitHub MCP server")
            
        except Exception as e:
            self.logger.error(f"Failed to connect to GitHub MCP server: {e}")
            raise
    
    def get_repository_info(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get repository information"""
        return self.call_tool("get_repository", {
            "owner": owner,
            "repo": repo
        })
    
    def list_issues(self, owner: str, repo: str, state: str = "open") -> Dict[str, Any]:
        """List repository issues"""
        return self.call_tool("list_issues", {
            "owner": owner,
            "repo": repo,
            "state": state
        })
    
    def create_issue(self, owner: str, repo: str, title: str, body: str, labels: Optional[List[str]] = None) -> Dict[str, Any]:
        """Create a new issue"""
        args = {
            "owner": owner,
            "repo": repo,
            "title": title,
            "body": body
        }
        if labels:
            args["labels"] = labels
        
        return self.call_tool("create_issue", args)
    
    def get_pull_requests(self, owner: str, repo: str, state: str = "open") -> Dict[str, Any]:
        """Get pull requests"""
        return self.call_tool("list_pull_requests", {
            "owner": owner,
            "repo": repo,
            "state": state
        })


class AzureDevOpsMCPClient(BaseMCPClient):
    """MCP client for Azure DevOps integration"""
    
    def __init__(self, connection_params: Optional[Dict[str, Any]] = None):
        params = connection_params or {}
        super().__init__("ado", params)
    
    def connect(self):
        """Connect to Azure DevOps MCP server"""
        try:
            if "server_url" in self.connection_params:
                self._client = MCPClient(
                    lambda: sse_client(self.connection_params["server_url"])
                )
            else:
                # stdio-based connection with custom ADO MCP server
                self._client = MCPClient(lambda: stdio_client(
                    StdioServerParameters(
                        command="python",
                        args=["-m", "ado_mcp_server"]
                    )
                ))
            
            self._client.__enter__()
            self.logger.info(f"Connected to Azure DevOps MCP server")
            
        except Exception as e:
            self.logger.error(f"Failed to connect to Azure DevOps MCP server: {e}")
            raise
    
    def get_work_items(self, project: str, query: str) -> Dict[str, Any]:
        """Get work items using WIQL query"""
        return self.call_tool("query_work_items", {
            "project": project,
            "query": query
        })
    
    def create_work_item(self, project: str, work_item_type: str, title: str, description: str) -> Dict[str, Any]:
        """Create a new work item"""
        return self.call_tool("create_work_item", {
            "project": project,
            "work_item_type": work_item_type,
            "title": title,
            "description": description
        })
    
    def get_repositories(self, project: str) -> Dict[str, Any]:
        """Get repositories in a project"""
        return self.call_tool("list_repositories", {
            "project": project
        })


class FileSystemMCPClient(BaseMCPClient):
    """MCP client for file system operations"""
    
    def __init__(self, connection_params: Optional[Dict[str, Any]] = None):
        params = connection_params or {}
        super().__init__("filesystem", params)
    
    def connect(self):
        """Connect to filesystem MCP server"""
        try:
            self._client = MCPClient(lambda: stdio_client(
                StdioServerParameters(
                    command="uvx",
                    args=["filesystem-mcp-server@latest"]
                )
            ))
            
            self._client.__enter__()
            self.logger.info(f"Connected to filesystem MCP server")
            
        except Exception as e:
            self.logger.error(f"Failed to connect to filesystem MCP server: {e}")
            raise
    
    def read_file(self, file_path: str) -> Dict[str, Any]:
        """Read file content"""
        return self.call_tool("read_file", {
            "path": file_path
        })
    
    def write_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Write content to file"""
        return self.call_tool("write_file", {
            "path": file_path,
            "content": content
        })
    
    def list_directory(self, directory_path: str) -> Dict[str, Any]:
        """List directory contents"""
        return self.call_tool("list_directory", {
            "path": directory_path
        })


class MCPClientManager:
    """Manages multiple MCP clients"""
    
    def __init__(self):
        self.clients: Dict[str, BaseMCPClient] = {}
        self.observer = get_observer()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = get_config()
        
    def register_client(self, name: str, client: BaseMCPClient):
        """Register an MCP client"""
        self.clients[name] = client
        self.logger.info(f"Registered MCP client: {name}")
    
    def get_client(self, name: str) -> Optional[BaseMCPClient]:
        """Get an MCP client by name"""
        return self.clients.get(name)
    
    def initialize_default_clients(self):
        """Initialize default MCP clients based on configuration"""
        
        # GitHub client
        if self.config.mcp_servers.get("github"):
            github_client = GitHubMCPClient({
                "server_url": self.config.mcp_servers["github"]
            })
            self.register_client("github", github_client)
        
        # Azure DevOps client
        if self.config.mcp_servers.get("ado"):
            ado_client = AzureDevOpsMCPClient({
                "server_url": self.config.mcp_servers["ado"]
            })
            self.register_client("ado", ado_client)
        
        # Filesystem client
        filesystem_client = FileSystemMCPClient()
        self.register_client("filesystem", filesystem_client)
    
    def get_all_tools(self) -> List[Any]:
        """Get tools from all connected MCP clients"""
        all_tools = []
        
        for name, client in self.clients.items():
            try:
                tools = client.list_tools()
                all_tools.extend(tools)
                self.logger.info(f"Added {len(tools)} tools from {name} MCP server")
            except Exception as e:
                self.logger.error(f"Failed to get tools from {name}: {e}")
        
        return all_tools
    
    def disconnect_all(self):
        """Disconnect all MCP clients"""
        for name, client in self.clients.items():
            try:
                client.disconnect()
                self.logger.info(f"Disconnected from {name} MCP server")
            except Exception as e:
                self.logger.error(f"Failed to disconnect from {name}: {e}")


# Global MCP client manager
_mcp_manager: Optional[MCPClientManager] = None


def get_mcp_manager() -> MCPClientManager:
    """Get the global MCP client manager"""
    global _mcp_manager
    if _mcp_manager is None:
        _mcp_manager = MCPClientManager()
        _mcp_manager.initialize_default_clients()
    return _mcp_manager


def reset_mcp_manager():
    """Reset the global MCP manager (mainly for testing)"""
    global _mcp_manager
    if _mcp_manager:
        _mcp_manager.disconnect_all()
    _mcp_manager = None
