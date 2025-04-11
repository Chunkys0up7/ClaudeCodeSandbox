#!/usr/bin/env python3
"""
App Integration Module for AI App Store Workspaces

This module provides functionality for integrating various types of apps
and tools into workspaces, including connection to MCP servers, utilities,
agents, and code snippets.
"""

import enum
import uuid
import logging
import datetime
import json
import subprocess
import os
import tempfile
from typing import Dict, List, Any, Optional, Union, Callable

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConnectionType(enum.Enum):
    """Enum representing the types of connections"""
    LOCAL = "local"
    REMOTE = "remote"
    API = "api"
    DATABASE = "database"
    KNOWLEDGE_BASE = "knowledge_base"
    WEB = "web"


class AppSource(enum.Enum):
    """Enum representing the sources of apps"""
    APP_STORE = "app_store"
    MCP_SERVER = "mcp_server"
    LOCAL = "local"
    EXTERNAL = "external"
    CUSTOM = "custom"


class AppDefinition:
    """Represents a definition for an app in the App Store"""
    
    def __init__(self, app_id: str, name: str, app_type: str, source: AppSource):
        self.id = app_id
        self.name = name
        self.app_type = app_type
        self.source = source
        self.description = ""
        self.version = "1.0.0"
        self.author = ""
        self.capabilities = []
        self.requirements = {}
        self.configuration_schema = {}
        self.created_at = datetime.datetime.utcnow()
        self.updated_at = self.created_at
        
    def set_description(self, description: str) -> None:
        """Set the app description"""
        self.description = description
        
    def set_version(self, version: str) -> None:
        """Set the app version"""
        self.version = version
        
    def set_author(self, author: str) -> None:
        """Set the app author"""
        self.author = author
        
    def add_capability(self, capability: str) -> None:
        """Add a capability to the app"""
        if capability not in self.capabilities:
            self.capabilities.append(capability)
            
    def set_requirements(self, requirements: Dict[str, Any]) -> None:
        """Set the app requirements"""
        self.requirements = requirements
        
    def set_configuration_schema(self, schema: Dict[str, Any]) -> None:
        """Set the configuration schema for the app"""
        self.configuration_schema = schema
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "name": self.name,
            "app_type": self.app_type,
            "source": self.source.value,
            "description": self.description,
            "version": self.version,
            "author": self.author,
            "capabilities": self.capabilities,
            "requirements": self.requirements,
            "configuration_schema": self.configuration_schema,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class AppInstance:
    """Represents an instance of an app in a workspace"""
    
    def __init__(self, app_definition: AppDefinition, instance_id: str):
        self.app_definition = app_definition
        self.id = instance_id
        self.configuration = {}
        self.connection_info = {}
        self.status = "inactive"  # inactive, active, error
        self.error_message = None
        self.created_at = datetime.datetime.utcnow()
        self.updated_at = self.created_at
        self.last_used_at = None
        
    def configure(self, configuration: Dict[str, Any]) -> None:
        """Configure the app instance"""
        self.configuration = configuration
        self.updated_at = datetime.datetime.utcnow()
        
    def set_connection_info(self, connection_info: Dict[str, Any]) -> None:
        """Set connection information for the app instance"""
        self.connection_info = connection_info
        self.updated_at = datetime.datetime.utcnow()
        
    def set_status(self, status: str, error_message: Optional[str] = None) -> None:
        """Set the status of the app instance"""
        self.status = status
        self.error_message = error_message
        self.updated_at = datetime.datetime.utcnow()
        
    def record_usage(self) -> None:
        """Record that the app instance was used"""
        self.last_used_at = datetime.datetime.utcnow()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "app": {
                "id": self.app_definition.id,
                "name": self.app_definition.name,
                "app_type": self.app_definition.app_type,
                "source": self.app_definition.source.value,
                "version": self.app_definition.version
            },
            "configuration": self.configuration,
            "status": self.status,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_used_at": self.last_used_at.isoformat() if self.last_used_at else None
        }


class MCPServerConnection:
    """Represents a connection to an MCP server"""
    
    def __init__(self, server_url: str, api_key: Optional[str] = None):
        self.id = str(uuid.uuid4())
        self.server_url = server_url
        self.api_key = api_key
        self.name = server_url.split("//")[-1].split(".")[0]  # Extract a simple name from URL
        self.status = "disconnected"  # disconnected, connected, error
        self.error_message = None
        self.capabilities = []
        self.connected_at = None
        self.created_at = datetime.datetime.utcnow()
        self.updated_at = self.created_at
        
    def connect(self) -> bool:
        """Connect to the MCP server"""
        try:
            # In a real implementation, this would make an API call to the server
            # For this example, we'll simulate a successful connection
            self.status = "connected"
            self.connected_at = datetime.datetime.utcnow()
            self.updated_at = self.connected_at
            
            # Simulate discovering capabilities
            self.capabilities = ["model-inference", "knowledge-base", "web-access"]
            
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to MCP server: {str(e)}")
            self.status = "error"
            self.error_message = str(e)
            self.updated_at = datetime.datetime.utcnow()
            return False
            
    def disconnect(self) -> None:
        """Disconnect from the MCP server"""
        self.status = "disconnected"
        self.connected_at = None
        self.updated_at = datetime.datetime.utcnow()
        
    def invoke_model(self, model_name: str, prompt: str, 
                    parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Invoke a model on the MCP server"""
        if self.status != "connected":
            raise ValueError("Not connected to MCP server")
            
        # In a real implementation, this would make an API call to the server
        # For this example, we'll simulate a model response
        self.updated_at = datetime.datetime.utcnow()
        
        return {
            "model": model_name,
            "response": f"Response to: {prompt}",
            "usage": {
                "prompt_tokens": len(prompt.split()),
                "completion_tokens": 20,
                "total_tokens": len(prompt.split()) + 20
            }
        }
        
    def query_knowledge_base(self, kb_id: str, query: str, 
                           parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Query a knowledge base on the MCP server"""
        if self.status != "connected":
            raise ValueError("Not connected to MCP server")
            
        if "knowledge-base" not in self.capabilities:
            raise ValueError("MCP server does not support knowledge base queries")
            
        # In a real implementation, this would make an API call to the server
        # For this example, we'll simulate a knowledge base response
        self.updated_at = datetime.datetime.utcnow()
        
        return {
            "query": query,
            "results": [
                {"content": f"Knowledge base result 1 for: {query}", "score": 0.92},
                {"content": f"Knowledge base result 2 for: {query}", "score": 0.85},
                {"content": f"Knowledge base result 3 for: {query}", "score": 0.78}
            ]
        }
        
    def web_search(self, query: str, 
                 parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Perform a web search via the MCP server"""
        if self.status != "connected":
            raise ValueError("Not connected to MCP server")
            
        if "web-access" not in self.capabilities:
            raise ValueError("MCP server does not support web access")
            
        # In a real implementation, this would make an API call to the server
        # For this example, we'll simulate a web search response
        self.updated_at = datetime.datetime.utcnow()
        
        return {
            "query": query,
            "results": [
                {"title": f"Web result 1 for {query}", "url": f"https://example.com/1", "snippet": "...content..."},
                {"title": f"Web result 2 for {query}", "url": f"https://example.com/2", "snippet": "...content..."},
                {"title": f"Web result 3 for {query}", "url": f"https://example.com/3", "snippet": "...content..."}
            ]
        }
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "server_url": self.server_url,
            "name": self.name,
            "status": self.status,
            "error_message": self.error_message,
            "capabilities": self.capabilities,
            "connected_at": self.connected_at.isoformat() if self.connected_at else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class CodeSnippet:
    """Represents a code snippet that can be executed"""
    
    def __init__(self, name: str, language: str, code: str, created_by: str):
        self.id = str(uuid.uuid4())
        self.name = name
        self.language = language
        self.code = code
        self.created_by = created_by
        self.description = ""
        self.created_at = datetime.datetime.utcnow()
        self.updated_at = self.created_at
        self.last_executed_at = None
        self.execution_count = 0
        
    def set_description(self, description: str) -> None:
        """Set the snippet description"""
        self.description = description
        self.updated_at = datetime.datetime.utcnow()
        
    def update_code(self, code: str) -> None:
        """Update the snippet code"""
        self.code = code
        self.updated_at = datetime.datetime.utcnow()
        
    def execute(self, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute the code snippet"""
        self.execution_count += 1
        self.last_executed_at = datetime.datetime.utcnow()
        
        try:
            result = None
            
            if self.language == "python":
                result = self._execute_python(parameters)
            elif self.language == "javascript":
                result = self._execute_js(parameters)
            elif self.language == "shell":
                result = self._execute_shell(parameters)
            else:
                return {
                    "status": "error",
                    "error": f"Unsupported language: {self.language}"
                }
                
            return {
                "status": "success",
                "result": result,
                "executed_at": self.last_executed_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error executing {self.language} snippet: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "executed_at": self.last_executed_at.isoformat()
            }
            
    def _execute_python(self, parameters: Optional[Dict[str, Any]]) -> Any:
        """Execute a Python code snippet"""
        # Create a temporary file with the code
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as temp:
            # Prepare code with parameters
            param_code = ""
            if parameters:
                param_code = "parameters = " + json.dumps(parameters) + "\n"
            
            temp.write((param_code + self.code).encode())
            temp_path = temp.name
            
        try:
            # Execute the Python script and capture output
            result = subprocess.run(
                ["python3", temp_path],
                capture_output=True,
                text=True,
                check=True
            )
            
            output = result.stdout.strip()
            
            # Try to parse as JSON if possible
            try:
                return json.loads(output)
            except json.JSONDecodeError:
                return output
                
        finally:
            # Clean up the temporary file
            os.unlink(temp_path)
            
    def _execute_js(self, parameters: Optional[Dict[str, Any]]) -> Any:
        """Execute a JavaScript code snippet"""
        # Create a temporary file with the code
        with tempfile.NamedTemporaryFile(suffix=".js", delete=False) as temp:
            # Prepare code with parameters
            param_code = ""
            if parameters:
                param_code = "const parameters = " + json.dumps(parameters) + ";\n"
            
            temp.write((param_code + self.code).encode())
            temp_path = temp.name
            
        try:
            # Execute the JavaScript script and capture output
            result = subprocess.run(
                ["node", temp_path],
                capture_output=True,
                text=True,
                check=True
            )
            
            output = result.stdout.strip()
            
            # Try to parse as JSON if possible
            try:
                return json.loads(output)
            except json.JSONDecodeError:
                return output
                
        finally:
            # Clean up the temporary file
            os.unlink(temp_path)
            
    def _execute_shell(self, parameters: Optional[Dict[str, Any]]) -> Any:
        """Execute a shell script"""
        # Create a temporary file with the code
        with tempfile.NamedTemporaryFile(suffix=".sh", delete=False) as temp:
            # Add shebang line
            script_content = "#!/bin/bash\n"
            
            # Add parameters as environment variables
            if parameters:
                for key, value in parameters.items():
                    script_content += f"export {key}=\"{value}\"\n"
                    
            script_content += self.code
            
            temp.write(script_content.encode())
            temp_path = temp.name
            
            # Make the script executable
            os.chmod(temp_path, 0o755)
            
        try:
            # Execute the shell script and capture output
            result = subprocess.run(
                [temp_path],
                capture_output=True,
                text=True,
                check=True
            )
            
            return result.stdout.strip()
            
        finally:
            # Clean up the temporary file
            os.unlink(temp_path)
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "name": self.name,
            "language": self.language,
            "description": self.description,
            "code": self.code,
            "created_by": self.created_by,
            "execution_count": self.execution_count,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_executed_at": self.last_executed_at.isoformat() if self.last_executed_at else None
        }


class AgentDefinition:
    """Represents a definition for an agent"""
    
    def __init__(self, name: str, description: str, agent_type: str):
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.agent_type = agent_type
        self.capabilities = []
        self.tools = []
        self.created_at = datetime.datetime.utcnow()
        self.updated_at = self.created_at
        
    def add_capability(self, capability: str) -> None:
        """Add a capability to the agent"""
        if capability not in self.capabilities:
            self.capabilities.append(capability)
            self.updated_at = datetime.datetime.utcnow()
            
    def add_tool(self, tool_id: str, tool_name: str) -> None:
        """Add a tool to the agent"""
        if tool_id not in [t["id"] for t in self.tools]:
            self.tools.append({
                "id": tool_id,
                "name": tool_name
            })
            self.updated_at = datetime.datetime.utcnow()
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "agent_type": self.agent_type,
            "capabilities": self.capabilities,
            "tools": self.tools,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class AgentInstance:
    """Represents an instance of an agent in a workspace"""
    
    def __init__(self, agent_definition: AgentDefinition, instance_id: str):
        self.agent_definition = agent_definition
        self.id = instance_id
        self.configuration = {}
        self.status = "inactive"  # inactive, active, busy, error
        self.error_message = None
        self.memory_id = None
        self.created_at = datetime.datetime.utcnow()
        self.updated_at = self.created_at
        self.last_active_at = None
        
    def configure(self, configuration: Dict[str, Any]) -> None:
        """Configure the agent instance"""
        self.configuration = configuration
        self.updated_at = datetime.datetime.utcnow()
        
    def set_memory_id(self, memory_id: str) -> None:
        """Set the memory ID for the agent"""
        self.memory_id = memory_id
        self.updated_at = datetime.datetime.utcnow()
        
    def set_status(self, status: str, error_message: Optional[str] = None) -> None:
        """Set the status of the agent instance"""
        self.status = status
        self.error_message = error_message
        self.updated_at = datetime.datetime.utcnow()
        
    def run_task(self, task: str, inputs: Optional[Dict[str, Any]] = None,
               callback: Optional[Callable[[str, Dict[str, Any]], None]] = None) -> Dict[str, Any]:
        """Run a task with the agent"""
        if self.status == "busy":
            return {
                "status": "error",
                "error": "Agent is already busy with another task"
            }
            
        # Set status to busy
        previous_status = self.status
        self.status = "busy"
        self.last_active_at = datetime.datetime.utcnow()
        
        try:
            # In a real implementation, this would run the agent's task
            # For this example, we'll simulate a task execution
            
            # Report progress if callback is provided
            if callback:
                callback("started", {"task": task})
                callback("progress", {"progress": 50, "message": "Processing task..."})
                
            # Simulate task execution
            # time.sleep(2)  # Uncomment in real implementation
            
            # Report completion if callback is provided
            if callback:
                callback("completed", {"task": task})
                
            # Restore previous status
            self.status = previous_status
            self.updated_at = datetime.datetime.utcnow()
            
            return {
                "status": "success",
                "result": f"Completed task: {task}",
                "timestamp": datetime.datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error executing agent task: {str(e)}")
            # Set status to error
            self.status = "error"
            self.error_message = str(e)
            self.updated_at = datetime.datetime.utcnow()
            
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.datetime.utcnow().isoformat()
            }
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "agent": {
                "id": self.agent_definition.id,
                "name": self.agent_definition.name,
                "agent_type": self.agent_definition.agent_type
            },
            "configuration": self.configuration,
            "status": self.status,
            "error_message": self.error_message,
            "memory_id": self.memory_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_active_at": self.last_active_at.isoformat() if self.last_active_at else None
        }


class AppIntegrationManager:
    """Main class for managing app integrations in workspaces"""
    
    def __init__(self):
        self.app_definitions: Dict[str, AppDefinition] = {}
        self.app_instances: Dict[str, AppInstance] = {}
        self.mcp_connections: Dict[str, MCPServerConnection] = {}
        self.code_snippets: Dict[str, CodeSnippet] = {}
        self.agent_definitions: Dict[str, AgentDefinition] = {}
        self.agent_instances: Dict[str, AgentInstance] = {}
        
        # Load default app definitions
        self._load_default_apps()
        
    def _load_default_apps(self) -> None:
        """Load default app definitions"""
        # Create a few sample app definitions
        app1 = AppDefinition(
            "app-001", 
            "Text Analysis Tool", 
            "utility", 
            AppSource.APP_STORE
        )
        app1.set_description("Analyzes text for sentiment, entities, and key phrases")
        app1.set_version("1.2.0")
        app1.set_author("AI App Store Team")
        app1.add_capability("text-analysis")
        app1.add_capability("sentiment-analysis")
        app1.add_capability("entity-recognition")
        app1.set_configuration_schema({
            "model": {"type": "string", "default": "default", "description": "Model to use for analysis"},
            "features": {"type": "array", "items": {"type": "string"}, "default": ["sentiment", "entities"]}
        })
        self.app_definitions[app1.id] = app1
        
        app2 = AppDefinition(
            "app-002", 
            "Document Generator", 
            "tool", 
            AppSource.APP_STORE
        )
        app2.set_description("Generates documents from templates and data")
        app2.set_version("1.0.3")
        app2.set_author("Content Team")
        app2.add_capability("document-generation")
        app2.add_capability("pdf-export")
        app2.set_configuration_schema({
            "template_id": {"type": "string", "description": "Template ID to use"},
            "output_format": {"type": "string", "enum": ["docx", "pdf", "html"], "default": "pdf"}
        })
        self.app_definitions[app2.id] = app2
        
        # Create a sample agent definition
        agent1 = AgentDefinition(
            "Research Assistant",
            "Assists with research tasks and information gathering",
            "assistant"
        )
        agent1.add_capability("web-search")
        agent1.add_capability("summarization")
        agent1.add_tool("tool-001", "Web Search")
        agent1.add_tool("tool-002", "Document Summarizer")
        self.agent_definitions[agent1.id] = agent1
        
    def register_app_definition(self, name: str, app_type: str, 
                              source: AppSource, description: str) -> str:
        """Register a new app definition"""
        app_id = f"app-{str(uuid.uuid4())[:8]}"
        app = AppDefinition(app_id, name, app_type, source)
        app.set_description(description)
        
        self.app_definitions[app_id] = app
        return app_id
        
    def get_app_definition(self, app_id: str) -> Optional[AppDefinition]:
        """Get an app definition by ID"""
        return self.app_definitions.get(app_id)
        
    def list_app_definitions(self, app_type: Optional[str] = None, 
                           source: Optional[AppSource] = None) -> List[Dict[str, Any]]:
        """List app definitions, optionally filtered"""
        result = []
        
        for app in self.app_definitions.values():
            if app_type and app.app_type != app_type:
                continue
                
            if source and app.source != source:
                continue
                
            result.append(app.to_dict())
            
        return result
        
    def create_app_instance(self, app_id: str, configuration: Dict[str, Any]) -> Optional[str]:
        """Create an instance of an app in a workspace"""
        app_definition = self.app_definitions.get(app_id)
        if not app_definition:
            return None
            
        instance_id = str(uuid.uuid4())
        instance = AppInstance(app_definition, instance_id)
        instance.configure(configuration)
        
        # Set active status by default
        instance.set_status("active")
        
        self.app_instances[instance_id] = instance
        return instance_id
        
    def get_app_instance(self, instance_id: str) -> Optional[AppInstance]:
        """Get an app instance by ID"""
        return self.app_instances.get(instance_id)
        
    def list_app_instances(self, app_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """List app instances, optionally filtered"""
        result = []
        
        for instance in self.app_instances.values():
            if app_type and instance.app_definition.app_type != app_type:
                continue
                
            result.append(instance.to_dict())
            
        return result
        
    def update_app_instance_configuration(self, instance_id: str, 
                                        configuration: Dict[str, Any]) -> bool:
        """Update an app instance's configuration"""
        instance = self.app_instances.get(instance_id)
        if not instance:
            return False
            
        instance.configure(configuration)
        return True
        
    def connect_to_mcp_server(self, server_url: str, api_key: Optional[str] = None) -> Optional[str]:
        """Connect to an MCP server"""
        connection = MCPServerConnection(server_url, api_key)
        
        # Try to connect
        if not connection.connect():
            return None
            
        self.mcp_connections[connection.id] = connection
        return connection.id
        
    def get_mcp_connection(self, connection_id: str) -> Optional[MCPServerConnection]:
        """Get an MCP server connection by ID"""
        return self.mcp_connections.get(connection_id)
        
    def list_mcp_connections(self) -> List[Dict[str, Any]]:
        """List MCP server connections"""
        return [conn.to_dict() for conn in self.mcp_connections.values()]
        
    def disconnect_from_mcp_server(self, connection_id: str) -> bool:
        """Disconnect from an MCP server"""
        connection = self.mcp_connections.get(connection_id)
        if not connection:
            return False
            
        connection.disconnect()
        return True
        
    def create_code_snippet(self, name: str, language: str, code: str, 
                          created_by: str, description: Optional[str] = None) -> str:
        """Create a code snippet"""
        snippet = CodeSnippet(name, language, code, created_by)
        
        if description:
            snippet.set_description(description)
            
        self.code_snippets[snippet.id] = snippet
        return snippet.id
        
    def get_code_snippet(self, snippet_id: str) -> Optional[CodeSnippet]:
        """Get a code snippet by ID"""
        return self.code_snippets.get(snippet_id)
        
    def list_code_snippets(self, language: Optional[str] = None, 
                         created_by: Optional[str] = None) -> List[Dict[str, Any]]:
        """List code snippets, optionally filtered"""
        result = []
        
        for snippet in self.code_snippets.values():
            if language and snippet.language != language:
                continue
                
            if created_by and snippet.created_by != created_by:
                continue
                
            result.append(snippet.to_dict())
            
        return result
        
    def update_code_snippet(self, snippet_id: str, code: str, 
                          description: Optional[str] = None) -> bool:
        """Update a code snippet"""
        snippet = self.code_snippets.get(snippet_id)
        if not snippet:
            return False
            
        snippet.update_code(code)
        
        if description is not None:
            snippet.set_description(description)
            
        return True
        
    def execute_code_snippet(self, snippet_id: str, 
                           parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a code snippet"""
        snippet = self.code_snippets.get(snippet_id)
        if not snippet:
            return {
                "status": "error",
                "error": f"Snippet not found: {snippet_id}"
            }
            
        return snippet.execute(parameters)
        
    def register_agent_definition(self, name: str, description: str, agent_type: str) -> str:
        """Register a new agent definition"""
        agent = AgentDefinition(name, description, agent_type)
        self.agent_definitions[agent.id] = agent
        return agent.id
        
    def get_agent_definition(self, agent_id: str) -> Optional[AgentDefinition]:
        """Get an agent definition by ID"""
        return self.agent_definitions.get(agent_id)
        
    def list_agent_definitions(self, agent_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """List agent definitions, optionally filtered"""
        result = []
        
        for agent in self.agent_definitions.values():
            if agent_type and agent.agent_type != agent_type:
                continue
                
            result.append(agent.to_dict())
            
        return result
        
    def create_agent_instance(self, agent_id: str, 
                            configuration: Dict[str, Any]) -> Optional[str]:
        """Create an instance of an agent in a workspace"""
        agent_definition = self.agent_definitions.get(agent_id)
        if not agent_definition:
            return None
            
        instance_id = str(uuid.uuid4())
        instance = AgentInstance(agent_definition, instance_id)
        instance.configure(configuration)
        
        # Set inactive status by default
        instance.set_status("inactive")
        
        self.agent_instances[instance_id] = instance
        return instance_id
        
    def get_agent_instance(self, instance_id: str) -> Optional[AgentInstance]:
        """Get an agent instance by ID"""
        return self.agent_instances.get(instance_id)
        
    def list_agent_instances(self, agent_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """List agent instances, optionally filtered"""
        result = []
        
        for instance in self.agent_instances.values():
            if agent_type and instance.agent_definition.agent_type != agent_type:
                continue
                
            result.append(instance.to_dict())
            
        return result
        
    def activate_agent_instance(self, instance_id: str, memory_id: Optional[str] = None) -> bool:
        """Activate an agent instance"""
        instance = self.agent_instances.get(instance_id)
        if not instance:
            return False
            
        instance.set_status("active")
        
        if memory_id:
            instance.set_memory_id(memory_id)
            
        return True
        
    def run_agent_task(self, instance_id: str, task: str, 
                      inputs: Optional[Dict[str, Any]] = None,
                      callback: Optional[Callable[[str, Dict[str, Any]], None]] = None) -> Dict[str, Any]:
        """Run a task with an agent"""
        instance = self.agent_instances.get(instance_id)
        if not instance:
            return {
                "status": "error",
                "error": f"Agent instance not found: {instance_id}"
            }
            
        if instance.status != "active":
            return {
                "status": "error",
                "error": f"Agent instance is not active (status: {instance.status})"
            }
            
        return instance.run_task(task, inputs, callback)


# Example usage
if __name__ == "__main__":
    # Create app integration manager
    manager = AppIntegrationManager()
    
    # List available app definitions
    apps = manager.list_app_definitions()
    print(f"Available apps ({len(apps)}):")
    for app in apps:
        print(f"- {app['name']} ({app['app_type']})")
        
    # Create an app instance
    text_analysis_app_id = None
    for app in apps:
        if app["name"] == "Text Analysis Tool":
            text_analysis_app_id = app["id"]
            break
            
    if text_analysis_app_id:
        instance_id = manager.create_app_instance(
            text_analysis_app_id,
            {"model": "advanced", "features": ["sentiment", "entities", "key_phrases"]}
        )
        print(f"\nCreated app instance: {instance_id}")
        
    # Connect to an MCP server
    connection_id = manager.connect_to_mcp_server("https://mcp.example.com", "api-key-123")
    if connection_id:
        print(f"\nConnected to MCP server: {connection_id}")
        
        # Get the connection
        connection = manager.get_mcp_connection(connection_id)
        if connection:
            # Use the connection
            result = connection.invoke_model(
                "gpt-4",
                "What is the capital of France?",
                {"temperature": 0.7}
            )
            print(f"Model response: {result['response']}")
            
    # Create a code snippet
    snippet_id = manager.create_code_snippet(
        "Data Processor",
        "python",
        """
import json

# Process the input data (assuming it's available in 'parameters')
data = parameters.get('data', [])
result = []

for item in data:
    # Add a processed flag
    item['processed'] = True
    # Calculate a simple metric
    if 'value' in item:
        item['metric'] = item['value'] * 2
    result.append(item)

# Print as JSON for the output
print(json.dumps({"processed_items": result, "count": len(result)}))
""",
        "user-123",
        "Processes data items by adding flags and calculating metrics"
    )
    print(f"\nCreated code snippet: {snippet_id}")
    
    # Execute the code snippet
    execution_result = manager.execute_code_snippet(
        snippet_id,
        {"data": [{"id": 1, "value": 10}, {"id": 2, "value": 20}]}
    )
    print(f"Execution result: {execution_result}")
    
    # List available agent definitions
    agents = manager.list_agent_definitions()
    print(f"\nAvailable agents ({len(agents)}):")
    for agent in agents:
        print(f"- {agent['name']} ({agent['agent_type']})")
        
    # Create an agent instance
    if agents:
        agent_id = agents[0]["id"]
        instance_id = manager.create_agent_instance(
            agent_id,
            {"model": "gpt-4", "max_iterations": 5}
        )
        print(f"\nCreated agent instance: {instance_id}")
        
        # Activate the agent
        manager.activate_agent_instance(instance_id, "memory-456")
        
        # Run a task with the agent
        task_result = manager.run_agent_task(
            instance_id,
            "Research the impact of AI on home lending",
            {"depth": "comprehensive", "format": "summary"}
        )
        print(f"Task result: {task_result}")