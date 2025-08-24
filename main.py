"""
Main application entry point for the Multi-Agent Email System.
Provides CLI and programmatic interfaces for interacting with the system.
"""

import os
import sys
import asyncio
import logging
from typing import Optional, Dict, Any
import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.syntax import Syntax
import json
from dotenv import load_dotenv

# Load environment variables BEFORE importing our modules
load_dotenv()

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src import (
    create_orchestrator,
    create_email_agent,
    get_observer,
    get_config,
    get_mcp_manager
)


class MultiAgentEmailSystem:
    """Main system class that coordinates all components"""
    
    def __init__(self):
        self.console = Console()
        self.observer = get_observer()
        self.config = get_config()
        self.mcp_manager = get_mcp_manager()
        
        # Initialize agents
        self.orchestrator = create_orchestrator("MainOrchestrator")
        self.email_agent = create_email_agent("EmailAgent")
        
        # Setup logging
        logging.basicConfig(
            level=getattr(logging, self.config.observability.log_level.value),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.config.observability.log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("Multi-Agent Email System initialized")
    
    def process_request(self, request: str, session_id: str = "cli") -> Dict[str, Any]:
        """Process a user request through the orchestrator"""
        
        self.console.print(f"\n[bold blue]Processing request:[/bold blue] {request}")
        
        try:
            # Use orchestrator to handle the request
            response = self.orchestrator(request, session_id)
            
            result = {
                "status": "success",
                "request": request,
                "response": response,
                "session_id": session_id
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to process request: {e}")
            return {
                "status": "error",
                "request": request,
                "error": str(e),
                "session_id": session_id
            }
    
    def interactive_mode(self):
        """Start interactive CLI mode"""
        
        self.console.print(Panel.fit(
            "[bold green]Multi-Agent Email System[/bold green]\n"
            "Type your requests in natural language.\n"
            "Examples:\n"
            "• 'Send a meeting request email to john@company.com about project review'\n"
            "• 'Create a follow-up email for the client meeting'\n"
            "• 'Check GitHub issues for my-repo'\n"
            "\nType 'help' for more commands or 'quit' to exit.",
            title="Welcome"
        ))
        
        session_id = "interactive"
        
        while True:
            try:
                user_input = Prompt.ask("\n[bold cyan]Enter your request[/bold cyan]")
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    self.console.print("[yellow]Goodbye![/yellow]")
                    break
                
                elif user_input.lower() in ['help', 'h']:
                    self._show_help()
                    continue
                
                elif user_input.lower() in ['status', 'info']:
                    self._show_status()
                    continue
                
                elif user_input.lower().startswith('config'):
                    self._show_config()
                    continue
                
                elif user_input.strip() == '':
                    continue
                
                # Process the request
                result = self.process_request(user_input, session_id)
                
                # Display result
                if result["status"] == "success":
                    self.console.print(f"\n[bold green]Response:[/bold green]")
                    self.console.print(Panel(result["response"], title="Agent Response"))
                else:
                    self.console.print(f"\n[bold red]Error:[/bold red] {result['error']}")
                
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Goodbye![/yellow]")
                break
            except Exception as e:
                self.console.print(f"\n[bold red]Unexpected error:[/bold red] {str(e)}")
    
    def _show_help(self):
        """Show help information"""
        help_text = """
[bold]Available Commands:[/bold]

[cyan]Email Operations:[/cyan]
• Send emails: "Send an email to user@example.com about meeting"
• Create content: "Create a project update email for the team"
• Validate emails: "Check if these emails are valid: user1@test.com, user2@test.com"

[cyan]Multi-recipient emails:[/cyan]
• "Send meeting invite to team@company.com with CC to manager@company.com"
• "Send project update to client@company.com and partner@company.com"

[cyan]MCP Operations (if configured):[/cyan]
• GitHub: "Show me issues in my-repo" 
• Azure DevOps: "List work items in project-name"
• Files: "Read contents of file.txt"

[cyan]System Commands:[/cyan]
• help, h - Show this help
• status, info - Show system status  
• config - Show configuration
• quit, exit, q - Exit the system

[cyan]Tips:[/cyan]
• Be specific about recipients and email content
• Use natural language - the system will understand context
• The orchestrator will route your request to appropriate agents
"""
        self.console.print(Panel(help_text, title="Help"))
    
    def _show_status(self):
        """Show system status"""
        status = {
            "Model Provider": self.config.model.provider.value,
            "Model": self.config.model.model,
            "Email Configured": bool(self.config.email.username),
            "Observability": self.config.observability.enable_tracing,
            "MCP Clients": len(self.mcp_manager.clients)
        }
        
        status_text = "\n".join([f"{key}: {value}" for key, value in status.items()])
        self.console.print(Panel(status_text, title="System Status"))
    
    def _show_config(self):
        """Show system configuration (sanitized)"""
        config_info = {
            "model": {
                "provider": self.config.model.provider.value,
                "model": self.config.model.model,
                "temperature": self.config.model.temperature,
                "max_tokens": self.config.model.max_tokens
            },
            "email": {
                "smtp_server": self.config.email.smtp_server,
                "smtp_port": self.config.email.smtp_port,
                "username": self.config.email.username,
                "configured": bool(self.config.email.password)
            },
            "observability": {
                "log_level": self.config.observability.log_level.value,
                "log_file": self.config.observability.log_file,
                "enable_tracing": self.config.observability.enable_tracing
            }
        }
        
        config_json = json.dumps(config_info, indent=2)
        syntax = Syntax(config_json, "json", theme="monokai", line_numbers=False)
        self.console.print(Panel(syntax, title="Configuration"))


# CLI Interface
@click.group()
def cli():
    """Multi-Agent Email System CLI"""
    pass


@cli.command()
@click.option('--request', '-r', help='Request to process')
@click.option('--session-id', '-s', default='cli', help='Session ID for tracking')
def process(request, session_id):
    """Process a single request"""
    system = MultiAgentEmailSystem()
    
    if not request:
        request = Prompt.ask("Enter your request")
    
    result = system.process_request(request, session_id)
    
    console = Console()
    if result["status"] == "success":
        console.print(f"[bold green]Success![/bold green]")
        console.print(Panel(result["response"], title="Response"))
    else:
        console.print(f"[bold red]Error:[/bold red] {result['error']}")


@cli.command()
def interactive():
    """Start interactive mode"""
    system = MultiAgentEmailSystem()
    system.interactive_mode()


@cli.command()
def demo():
    """Run demonstration scenarios"""
    system = MultiAgentEmailSystem()
    console = Console()
    
    demos = [
        "Create a meeting request email for a project review meeting",
        "Send a follow-up email about the client presentation",
        "Validate these email addresses: test@example.com, invalid-email, user@company.com"
    ]
    
    console.print(Panel.fit(
        "[bold green]Multi-Agent Email System Demo[/bold green]\n"
        "Running demonstration scenarios...",
        title="Demo Mode"
    ))
    
    for i, demo_request in enumerate(demos, 1):
        console.print(f"\n[bold blue]Demo {i}:[/bold blue] {demo_request}")
        result = system.process_request(demo_request, f"demo_{i}")
        
        if result["status"] == "success":
            console.print("[green]✓ Success[/green]")
            # Handle both string and AgentResult responses
            response_text = result["response"]
            if hasattr(response_text, 'content'):
                response_text = str(response_text.content)
            elif not isinstance(response_text, str):
                response_text = str(response_text)
            
            preview = response_text[:200] + "..." if len(response_text) > 200 else response_text
            console.print(Panel(preview, title="Response Preview"))
        else:
            console.print(f"[red]✗ Error: {result['error']}[/red]")


@cli.command()
def status():
    """Show system status"""
    system = MultiAgentEmailSystem()
    system._show_status()


if __name__ == "__main__":
    cli()
