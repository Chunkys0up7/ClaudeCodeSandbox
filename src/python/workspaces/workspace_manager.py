#!/usr/bin/env python3
"""
Workspace Manager Module for the AI App Store

This module provides functionality for creating and managing workspaces,
which allow individuals or job families to organize and use various apps
and tools within a consistent environment.
"""

import enum
import uuid
import logging
import datetime
import json
from typing import Dict, List, Any, Optional, Set, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WorkspaceType(enum.Enum):
    """Enum representing the possible types of workspaces"""
    PERSONAL = "personal"
    JOB_FAMILY = "job_family"
    TEAM = "team"
    PROJECT = "project"


class AccessLevel(enum.Enum):
    """Enum representing the possible access levels for workspace members"""
    OWNER = "owner"
    ADMIN = "admin"
    CONTRIBUTOR = "contributor"
    VIEWER = "viewer"


class AppType(enum.Enum):
    """Enum representing the possible types of apps in a workspace"""
    PUBLISHED_APP = "published_app"
    MCP_SERVER = "mcp_server"
    UTILITY = "utility"
    AGENT = "agent"
    TOOL = "tool"
    PYTHON_SNIPPET = "python_snippet"
    CODE_SNIPPET = "code_snippet"


class WorkspaceMember:
    """Represents a member of a workspace"""
    
    def __init__(self, user_id: str, access_level: AccessLevel, added_by: str):
        self.user_id = user_id
        self.access_level = access_level
        self.added_by = added_by
        self.added_at = datetime.datetime.utcnow()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "user_id": self.user_id,
            "access_level": self.access_level.value,
            "added_by": self.added_by,
            "added_at": self.added_at.isoformat()
        }


class WorkspaceApp:
    """Represents an app in a workspace"""
    
    def __init__(self, app_id: str, app_type: AppType, name: str, added_by: str):
        self.id = str(uuid.uuid4())
        self.app_id = app_id
        self.app_type = app_type
        self.name = name
        self.configuration = {}
        self.added_by = added_by
        self.added_at = datetime.datetime.utcnow()
        self.updated_at = self.added_at
        
    def set_configuration(self, config: Dict[str, Any]) -> None:
        """Set the configuration for this app instance"""
        self.configuration = config
        self.updated_at = datetime.datetime.utcnow()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "app_id": self.app_id,
            "app_type": self.app_type.value,
            "name": self.name,
            "configuration": self.configuration,
            "added_by": self.added_by,
            "added_at": self.added_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class Workflow:
    """Represents a workflow within a workspace"""
    
    def __init__(self, name: str, description: str, created_by: str):
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.created_by = created_by
        self.actions = []  # List of actions in the workflow
        self.checkpoints = []  # List of checkpoint IDs
        self.memory = {}  # Memory for context and history
        self.created_at = datetime.datetime.utcnow()
        self.updated_at = self.created_at
        self.last_active_at = self.created_at
        
    def add_action(self, action_type: str, app_id: str, data: Dict[str, Any],
                 user_id: str) -> str:
        """Add an action to the workflow"""
        action_id = str(uuid.uuid4())
        timestamp = datetime.datetime.utcnow()
        
        action = {
            "id": action_id,
            "type": action_type,
            "app_id": app_id,
            "data": data,
            "user_id": user_id,
            "timestamp": timestamp.isoformat(),
            "checkpoint_id": None
        }
        
        self.actions.append(action)
        self.updated_at = timestamp
        self.last_active_at = timestamp
        
        return action_id
        
    def create_checkpoint(self, name: str, action_id: str, 
                         expected_outcomes: Optional[Dict[str, Any]] = None) -> str:
        """Create a checkpoint at a specific action"""
        checkpoint_id = str(uuid.uuid4())
        timestamp = datetime.datetime.utcnow()
        
        checkpoint = {
            "id": checkpoint_id,
            "name": name,
            "action_id": action_id,
            "expected_outcomes": expected_outcomes or {},
            "created_at": timestamp.isoformat()
        }
        
        self.checkpoints.append(checkpoint)
        
        # Mark the action with this checkpoint
        for action in self.actions:
            if action["id"] == action_id:
                action["checkpoint_id"] = checkpoint_id
                break
                
        self.updated_at = timestamp
        
        return checkpoint_id
        
    def get_action_by_id(self, action_id: str) -> Optional[Dict[str, Any]]:
        """Get an action by its ID"""
        for action in self.actions:
            if action["id"] == action_id:
                return action
        return None
        
    def get_checkpoint_by_id(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        """Get a checkpoint by its ID"""
        for checkpoint in self.checkpoints:
            if checkpoint["id"] == checkpoint_id:
                return checkpoint
        return None
        
    def get_actions_until_checkpoint(self, checkpoint_id: str) -> List[Dict[str, Any]]:
        """Get all actions up to and including a specific checkpoint"""
        result = []
        
        # Find the action with this checkpoint
        checkpoint_action_id = None
        for checkpoint in self.checkpoints:
            if checkpoint["id"] == checkpoint_id:
                checkpoint_action_id = checkpoint["action_id"]
                break
                
        if not checkpoint_action_id:
            return result
            
        # Collect all actions up to and including the checkpoint action
        for action in self.actions:
            result.append(action)
            if action["id"] == checkpoint_action_id:
                break
                
        return result
        
    def store_memory(self, key: str, value: Any) -> None:
        """Store a value in the workflow memory"""
        self.memory[key] = value
        self.updated_at = datetime.datetime.utcnow()
        
    def get_memory(self, key: str) -> Optional[Any]:
        """Get a value from the workflow memory"""
        return self.memory.get(key)
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_by": self.created_by,
            "actions": self.actions,
            "checkpoints": self.checkpoints,
            "memory": self.memory,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_active_at": self.last_active_at.isoformat()
        }


class Workspace:
    """Represents a workspace in the AI App Store"""
    
    def __init__(self, name: str, workspace_type: WorkspaceType, created_by: str):
        self.id = str(uuid.uuid4())
        self.name = name
        self.workspace_type = workspace_type
        self.description = ""
        self.created_by = created_by
        self.members: Dict[str, WorkspaceMember] = {}
        self.apps: Dict[str, WorkspaceApp] = {}
        self.workflows: Dict[str, Workflow] = {}
        self.settings = {}
        self.created_at = datetime.datetime.utcnow()
        self.updated_at = self.created_at
        
        # Add creator as owner
        self.add_member(created_by, AccessLevel.OWNER, created_by)
        
    def set_description(self, description: str) -> None:
        """Set the workspace description"""
        self.description = description
        self.updated_at = datetime.datetime.utcnow()
        
    def add_member(self, user_id: str, access_level: AccessLevel, added_by: str) -> None:
        """Add a member to the workspace"""
        member = WorkspaceMember(user_id, access_level, added_by)
        self.members[user_id] = member
        self.updated_at = datetime.datetime.utcnow()
        
    def update_member_access(self, user_id: str, access_level: AccessLevel, updated_by: str) -> bool:
        """Update a member's access level"""
        if user_id not in self.members:
            return False
            
        # Check if the updater has appropriate permissions
        if not self._has_admin_access(updated_by):
            return False
            
        self.members[user_id].access_level = access_level
        self.updated_at = datetime.datetime.utcnow()
        return True
        
    def remove_member(self, user_id: str, removed_by: str) -> bool:
        """Remove a member from the workspace"""
        if user_id not in self.members:
            return False
            
        # Check if the remover has appropriate permissions
        if not self._has_admin_access(removed_by):
            return False
            
        # Cannot remove the last owner
        if (self.members[user_id].access_level == AccessLevel.OWNER and 
            len([m for m in self.members.values() if m.access_level == AccessLevel.OWNER]) <= 1):
            return False
            
        del self.members[user_id]
        self.updated_at = datetime.datetime.utcnow()
        return True
        
    def add_app(self, app_id: str, app_type: AppType, name: str, added_by: str) -> Optional[str]:
        """Add an app to the workspace"""
        # Check if the user has appropriate permissions
        if not self._has_contributor_access(added_by):
            return None
            
        app = WorkspaceApp(app_id, app_type, name, added_by)
        self.apps[app.id] = app
        self.updated_at = datetime.datetime.utcnow()
        return app.id
        
    def configure_app(self, app_instance_id: str, config: Dict[str, Any], updated_by: str) -> bool:
        """Configure an app in the workspace"""
        if app_instance_id not in self.apps:
            return False
            
        # Check if the user has appropriate permissions
        if not self._has_contributor_access(updated_by):
            return False
            
        self.apps[app_instance_id].set_configuration(config)
        self.updated_at = datetime.datetime.utcnow()
        return True
        
    def remove_app(self, app_instance_id: str, removed_by: str) -> bool:
        """Remove an app from the workspace"""
        if app_instance_id not in self.apps:
            return False
            
        # Check if the user has appropriate permissions
        if not self._has_contributor_access(removed_by):
            return False
            
        del self.apps[app_instance_id]
        self.updated_at = datetime.datetime.utcnow()
        return True
        
    def create_workflow(self, name: str, description: str, created_by: str) -> Optional[str]:
        """Create a new workflow in the workspace"""
        # Check if the user has appropriate permissions
        if not self._has_contributor_access(created_by):
            return None
            
        workflow = Workflow(name, description, created_by)
        self.workflows[workflow.id] = workflow
        self.updated_at = datetime.datetime.utcnow()
        return workflow.id
        
    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Get a workflow by ID"""
        return self.workflows.get(workflow_id)
        
    def remove_workflow(self, workflow_id: str, removed_by: str) -> bool:
        """Remove a workflow from the workspace"""
        if workflow_id not in self.workflows:
            return False
            
        # Check if the user has appropriate permissions
        if not self._has_contributor_access(removed_by):
            return False
            
        del self.workflows[workflow_id]
        self.updated_at = datetime.datetime.utcnow()
        return True
        
    def _has_admin_access(self, user_id: str) -> bool:
        """Check if a user has admin access to the workspace"""
        if user_id not in self.members:
            return False
            
        return self.members[user_id].access_level in [AccessLevel.OWNER, AccessLevel.ADMIN]
        
    def _has_contributor_access(self, user_id: str) -> bool:
        """Check if a user has contributor access to the workspace"""
        if user_id not in self.members:
            return False
            
        return self.members[user_id].access_level in [
            AccessLevel.OWNER, AccessLevel.ADMIN, AccessLevel.CONTRIBUTOR
        ]
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "name": self.name,
            "workspace_type": self.workspace_type.value,
            "description": self.description,
            "created_by": self.created_by,
            "members": {uid: member.to_dict() for uid, member in self.members.items()},
            "apps": {app_id: app.to_dict() for app_id, app in self.apps.items()},
            "workflows": {wf_id: wf.to_dict() for wf_id, wf in self.workflows.items()},
            "settings": self.settings,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class WorkspaceLog:
    """Represents a log of actions in a workspace"""
    
    def __init__(self, workspace_id: str):
        self.workspace_id = workspace_id
        self.entries = []
        
    def add_entry(self, user_id: str, action_type: str, details: Dict[str, Any]) -> str:
        """Add a log entry"""
        entry_id = str(uuid.uuid4())
        timestamp = datetime.datetime.utcnow()
        
        entry = {
            "id": entry_id,
            "workspace_id": self.workspace_id,
            "user_id": user_id,
            "action_type": action_type,
            "details": details,
            "timestamp": timestamp.isoformat()
        }
        
        self.entries.append(entry)
        return entry_id
        
    def get_entries(self, start_time: Optional[datetime.datetime] = None,
                  end_time: Optional[datetime.datetime] = None,
                  user_id: Optional[str] = None,
                  action_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get log entries, optionally filtered"""
        result = []
        
        for entry in self.entries:
            entry_time = datetime.datetime.fromisoformat(entry["timestamp"].replace("Z", "+00:00"))
            
            if start_time and entry_time < start_time:
                continue
                
            if end_time and entry_time > end_time:
                continue
                
            if user_id and entry["user_id"] != user_id:
                continue
                
            if action_type and entry["action_type"] != action_type:
                continue
                
            result.append(entry)
            
        return result
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "workspace_id": self.workspace_id,
            "entries": self.entries
        }


class AccessRequest:
    """Represents a request to access a workspace"""
    
    def __init__(self, workspace_id: str, user_id: str, requested_level: AccessLevel, message: str):
        self.id = str(uuid.uuid4())
        self.workspace_id = workspace_id
        self.user_id = user_id
        self.requested_level = requested_level
        self.message = message
        self.status = "pending"  # pending, approved, rejected
        self.reviewed_by = None
        self.review_comments = None
        self.requested_at = datetime.datetime.utcnow()
        self.reviewed_at = None
        
    def approve(self, reviewer_id: str, comments: Optional[str] = None) -> None:
        """Approve the access request"""
        self.status = "approved"
        self.reviewed_by = reviewer_id
        self.review_comments = comments
        self.reviewed_at = datetime.datetime.utcnow()
        
    def reject(self, reviewer_id: str, comments: Optional[str] = None) -> None:
        """Reject the access request"""
        self.status = "rejected"
        self.reviewed_by = reviewer_id
        self.review_comments = comments
        self.reviewed_at = datetime.datetime.utcnow()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "workspace_id": self.workspace_id,
            "user_id": self.user_id,
            "requested_level": self.requested_level.value,
            "message": self.message,
            "status": self.status,
            "reviewed_by": self.reviewed_by,
            "review_comments": self.review_comments,
            "requested_at": self.requested_at.isoformat(),
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None
        }


class WorkspaceManager:
    """Main class for managing workspaces"""
    
    def __init__(self):
        self.workspaces: Dict[str, Workspace] = {}
        self.workspace_logs: Dict[str, WorkspaceLog] = {}
        self.access_requests: Dict[str, AccessRequest] = {}
        
    def create_workspace(self, name: str, workspace_type: WorkspaceType, 
                        created_by: str, description: Optional[str] = None) -> str:
        """Create a new workspace"""
        workspace = Workspace(name, workspace_type, created_by)
        
        if description:
            workspace.set_description(description)
            
        self.workspaces[workspace.id] = workspace
        
        # Create a log for this workspace
        self.workspace_logs[workspace.id] = WorkspaceLog(workspace.id)
        
        # Log the creation
        self._log_action(workspace.id, created_by, "create_workspace", {
            "name": name,
            "workspace_type": workspace_type.value
        })
        
        return workspace.id
        
    def get_workspace(self, workspace_id: str) -> Optional[Workspace]:
        """Get a workspace by ID"""
        return self.workspaces.get(workspace_id)
        
    def list_workspaces(self, user_id: Optional[str] = None, 
                       workspace_type: Optional[WorkspaceType] = None) -> List[Dict[str, Any]]:
        """List workspaces, optionally filtered by user and/or type"""
        result = []
        
        for workspace in self.workspaces.values():
            # If user_id is specified, only include workspaces the user is a member of
            if user_id and user_id not in workspace.members:
                continue
                
            # If workspace_type is specified, only include workspaces of that type
            if workspace_type and workspace.workspace_type != workspace_type:
                continue
                
            # Include basic info without all the details
            result.append({
                "id": workspace.id,
                "name": workspace.name,
                "workspace_type": workspace.workspace_type.value,
                "description": workspace.description,
                "member_count": len(workspace.members),
                "app_count": len(workspace.apps),
                "workflow_count": len(workspace.workflows),
                "created_at": workspace.created_at.isoformat(),
                "updated_at": workspace.updated_at.isoformat()
            })
            
        return result
        
    def update_workspace(self, workspace_id: str, name: Optional[str] = None, 
                        description: Optional[str] = None, updated_by: str = None) -> bool:
        """Update a workspace's basic information"""
        if workspace_id not in self.workspaces:
            return False
            
        workspace = self.workspaces[workspace_id]
        
        # Check if the user has appropriate permissions
        if updated_by and not workspace._has_admin_access(updated_by):
            return False
            
        changes = {}
        
        if name is not None and name != workspace.name:
            workspace.name = name
            changes["name"] = name
            
        if description is not None and description != workspace.description:
            workspace.set_description(description)
            changes["description"] = description
            
        if changes:
            workspace.updated_at = datetime.datetime.utcnow()
            
            # Log the update
            if updated_by:
                self._log_action(workspace_id, updated_by, "update_workspace", changes)
                
        return True
        
    def add_workspace_member(self, workspace_id: str, user_id: str, 
                            access_level: AccessLevel, added_by: str) -> bool:
        """Add a member to a workspace"""
        if workspace_id not in self.workspaces:
            return False
            
        workspace = self.workspaces[workspace_id]
        
        # Check if the user adding has appropriate permissions
        if not workspace._has_admin_access(added_by):
            return False
            
        workspace.add_member(user_id, access_level, added_by)
        
        # Log the action
        self._log_action(workspace_id, added_by, "add_member", {
            "user_id": user_id,
            "access_level": access_level.value
        })
        
        return True
        
    def update_member_access(self, workspace_id: str, user_id: str, 
                           access_level: AccessLevel, updated_by: str) -> bool:
        """Update a member's access level in a workspace"""
        if workspace_id not in self.workspaces:
            return False
            
        workspace = self.workspaces[workspace_id]
        
        # Get the current access level for logging
        current_level = None
        if user_id in workspace.members:
            current_level = workspace.members[user_id].access_level.value
            
        result = workspace.update_member_access(user_id, access_level, updated_by)
        
        if result:
            # Log the action
            self._log_action(workspace_id, updated_by, "update_member_access", {
                "user_id": user_id,
                "previous_access_level": current_level,
                "new_access_level": access_level.value
            })
            
        return result
        
    def remove_workspace_member(self, workspace_id: str, user_id: str, removed_by: str) -> bool:
        """Remove a member from a workspace"""
        if workspace_id not in self.workspaces:
            return False
            
        workspace = self.workspaces[workspace_id]
        
        # Get the current access level for logging
        current_level = None
        if user_id in workspace.members:
            current_level = workspace.members[user_id].access_level.value
            
        result = workspace.remove_member(user_id, removed_by)
        
        if result:
            # Log the action
            self._log_action(workspace_id, removed_by, "remove_member", {
                "user_id": user_id,
                "previous_access_level": current_level
            })
            
        return result
        
    def add_workspace_app(self, workspace_id: str, app_id: str, app_type: AppType, 
                         name: str, added_by: str) -> Optional[str]:
        """Add an app to a workspace"""
        if workspace_id not in self.workspaces:
            return None
            
        workspace = self.workspaces[workspace_id]
        app_instance_id = workspace.add_app(app_id, app_type, name, added_by)
        
        if app_instance_id:
            # Log the action
            self._log_action(workspace_id, added_by, "add_app", {
                "app_id": app_id,
                "app_type": app_type.value,
                "name": name,
                "app_instance_id": app_instance_id
            })
            
        return app_instance_id
        
    def configure_workspace_app(self, workspace_id: str, app_instance_id: str, 
                              config: Dict[str, Any], updated_by: str) -> bool:
        """Configure an app in a workspace"""
        if workspace_id not in self.workspaces:
            return False
            
        workspace = self.workspaces[workspace_id]
        result = workspace.configure_app(app_instance_id, config, updated_by)
        
        if result:
            # Log the action
            self._log_action(workspace_id, updated_by, "configure_app", {
                "app_instance_id": app_instance_id,
                "configuration": config
            })
            
        return result
        
    def remove_workspace_app(self, workspace_id: str, app_instance_id: str, removed_by: str) -> bool:
        """Remove an app from a workspace"""
        if workspace_id not in self.workspaces:
            return False
            
        workspace = self.workspaces[workspace_id]
        
        # Get app details for logging
        app_details = None
        if app_instance_id in workspace.apps:
            app = workspace.apps[app_instance_id]
            app_details = {
                "app_id": app.app_id,
                "app_type": app.app_type.value,
                "name": app.name
            }
            
        result = workspace.remove_app(app_instance_id, removed_by)
        
        if result and app_details:
            # Log the action
            self._log_action(workspace_id, removed_by, "remove_app", {
                "app_instance_id": app_instance_id,
                "app_details": app_details
            })
            
        return result
        
    def create_workflow(self, workspace_id: str, name: str, description: str, 
                       created_by: str) -> Optional[str]:
        """Create a new workflow in a workspace"""
        if workspace_id not in self.workspaces:
            return None
            
        workspace = self.workspaces[workspace_id]
        workflow_id = workspace.create_workflow(name, description, created_by)
        
        if workflow_id:
            # Log the action
            self._log_action(workspace_id, created_by, "create_workflow", {
                "workflow_id": workflow_id,
                "name": name,
                "description": description
            })
            
        return workflow_id
        
    def add_workflow_action(self, workspace_id: str, workflow_id: str, action_type: str,
                          app_id: str, data: Dict[str, Any], user_id: str) -> Optional[str]:
        """Add an action to a workflow"""
        if workspace_id not in self.workspaces:
            return None
            
        workspace = self.workspaces[workspace_id]
        workflow = workspace.get_workflow(workflow_id)
        
        if not workflow:
            return None
            
        # Check if the user has appropriate permissions
        if not workspace._has_contributor_access(user_id):
            return None
            
        action_id = workflow.add_action(action_type, app_id, data, user_id)
        
        # Log the action
        self._log_action(workspace_id, user_id, "add_workflow_action", {
            "workflow_id": workflow_id,
            "action_id": action_id,
            "action_type": action_type,
            "app_id": app_id
        })
        
        return action_id
        
    def create_workflow_checkpoint(self, workspace_id: str, workflow_id: str, name: str,
                                 action_id: str, expected_outcomes: Optional[Dict[str, Any]],
                                 created_by: str) -> Optional[str]:
        """Create a checkpoint in a workflow"""
        if workspace_id not in self.workspaces:
            return None
            
        workspace = self.workspaces[workspace_id]
        workflow = workspace.get_workflow(workflow_id)
        
        if not workflow:
            return None
            
        # Check if the user has appropriate permissions
        if not workspace._has_contributor_access(created_by):
            return None
            
        # Check if the action exists
        if not workflow.get_action_by_id(action_id):
            return None
            
        checkpoint_id = workflow.create_checkpoint(name, action_id, expected_outcomes)
        
        # Log the action
        self._log_action(workspace_id, created_by, "create_workflow_checkpoint", {
            "workflow_id": workflow_id,
            "checkpoint_id": checkpoint_id,
            "name": name,
            "action_id": action_id
        })
        
        return checkpoint_id
        
    def store_workflow_memory(self, workspace_id: str, workflow_id: str, 
                            key: str, value: Any, stored_by: str) -> bool:
        """Store a value in a workflow's memory"""
        if workspace_id not in self.workspaces:
            return False
            
        workspace = self.workspaces[workspace_id]
        workflow = workspace.get_workflow(workflow_id)
        
        if not workflow:
            return False
            
        # Check if the user has appropriate permissions
        if not workspace._has_contributor_access(stored_by):
            return False
            
        workflow.store_memory(key, value)
        
        # Log the action
        self._log_action(workspace_id, stored_by, "store_workflow_memory", {
            "workflow_id": workflow_id,
            "key": key,
            "value_type": type(value).__name__
        })
        
        return True
        
    def get_workflow_memory(self, workspace_id: str, workflow_id: str, 
                          key: str, user_id: str) -> Optional[Any]:
        """Get a value from a workflow's memory"""
        if workspace_id not in self.workspaces:
            return None
            
        workspace = self.workspaces[workspace_id]
        
        # Check if the user has appropriate permissions
        if not workspace._has_contributor_access(user_id):
            return None
            
        workflow = workspace.get_workflow(workflow_id)
        
        if not workflow:
            return None
            
        return workflow.get_memory(key)
        
    def request_workspace_access(self, workspace_id: str, user_id: str, 
                               requested_level: AccessLevel, message: str) -> Optional[str]:
        """Request access to a workspace"""
        if workspace_id not in self.workspaces:
            return None
            
        # Create the request
        request = AccessRequest(workspace_id, user_id, requested_level, message)
        self.access_requests[request.id] = request
        
        # Log the action
        self._log_action(workspace_id, user_id, "request_access", {
            "requested_level": requested_level.value,
            "request_id": request.id
        })
        
        return request.id
        
    def approve_access_request(self, request_id: str, reviewer_id: str, 
                              comments: Optional[str] = None) -> bool:
        """Approve an access request"""
        if request_id not in self.access_requests:
            return False
            
        request = self.access_requests[request_id]
        
        if request.status != "pending":
            return False
            
        # Check if the reviewer has admin access to the workspace
        workspace = self.workspaces.get(request.workspace_id)
        if not workspace or not workspace._has_admin_access(reviewer_id):
            return False
            
        # Approve the request
        request.approve(reviewer_id, comments)
        
        # Add the user to the workspace
        workspace.add_member(request.user_id, request.requested_level, reviewer_id)
        
        # Log the action
        self._log_action(request.workspace_id, reviewer_id, "approve_access_request", {
            "request_id": request_id,
            "user_id": request.user_id,
            "access_level": request.requested_level.value
        })
        
        return True
        
    def reject_access_request(self, request_id: str, reviewer_id: str, 
                            comments: Optional[str] = None) -> bool:
        """Reject an access request"""
        if request_id not in self.access_requests:
            return False
            
        request = self.access_requests[request_id]
        
        if request.status != "pending":
            return False
            
        # Check if the reviewer has admin access to the workspace
        workspace = self.workspaces.get(request.workspace_id)
        if not workspace or not workspace._has_admin_access(reviewer_id):
            return False
            
        # Reject the request
        request.reject(reviewer_id, comments)
        
        # Log the action
        self._log_action(request.workspace_id, reviewer_id, "reject_access_request", {
            "request_id": request_id,
            "user_id": request.user_id
        })
        
        return True
        
    def get_workspace_logs(self, workspace_id: str, user_id: str, 
                         start_time: Optional[datetime.datetime] = None,
                         end_time: Optional[datetime.datetime] = None,
                         action_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get logs for a workspace"""
        if workspace_id not in self.workspaces or workspace_id not in self.workspace_logs:
            return []
            
        workspace = self.workspaces[workspace_id]
        
        # Check if the user has appropriate permissions
        if not workspace._has_contributor_access(user_id):
            return []
            
        log = self.workspace_logs[workspace_id]
        return log.get_entries(start_time, end_time, None, action_type)
        
    def _log_action(self, workspace_id: str, user_id: str, action_type: str, 
                   details: Dict[str, Any]) -> Optional[str]:
        """Internal method to log an action"""
        if workspace_id not in self.workspace_logs:
            return None
            
        log = self.workspace_logs[workspace_id]
        return log.add_entry(user_id, action_type, details)


# Example usage
if __name__ == "__main__":
    # Create workspace manager
    manager = WorkspaceManager()
    
    # Create a personal workspace
    user_id = "user-123"
    workspace_id = manager.create_workspace(
        "My Analytics Workspace",
        WorkspaceType.PERSONAL,
        user_id,
        "Personal workspace for loan analytics"
    )
    print(f"Created workspace: {workspace_id}")
    
    # Add apps to the workspace
    app_instance_id = manager.add_workspace_app(
        workspace_id,
        "app-456",
        AppType.PUBLISHED_APP,
        "Loan Eligibility Predictor",
        user_id
    )
    print(f"Added app: {app_instance_id}")
    
    # Configure the app
    manager.configure_workspace_app(
        workspace_id,
        app_instance_id,
        {"model": "default", "threshold": 0.75},
        user_id
    )
    
    # Create a workflow
    workflow_id = manager.create_workflow(
        workspace_id,
        "Loan Analysis Workflow",
        "Analyze loan applications and predict eligibility",
        user_id
    )
    print(f"Created workflow: {workflow_id}")
    
    # Add actions to the workflow
    action1_id = manager.add_workflow_action(
        workspace_id,
        workflow_id,
        "load_data",
        app_instance_id,
        {"source": "database", "table": "loan_applications"},
        user_id
    )
    print(f"Added action: {action1_id}")
    
    action2_id = manager.add_workflow_action(
        workspace_id,
        workflow_id,
        "analyze",
        app_instance_id,
        {"analysis_type": "eligibility", "params": {"include_reasons": True}},
        user_id
    )
    print(f"Added action: {action2_id}")
    
    # Create a checkpoint
    checkpoint_id = manager.create_workflow_checkpoint(
        workspace_id,
        workflow_id,
        "After Analysis",
        action2_id,
        {"status": "completed", "predictions_count": 100},
        user_id
    )
    print(f"Created checkpoint: {checkpoint_id}")
    
    # Store something in workflow memory
    manager.store_workflow_memory(
        workspace_id,
        workflow_id,
        "analysis_results",
        {"approved": 75, "rejected": 25, "avg_score": 0.68},
        user_id
    )
    
    # Get workspace logs
    logs = manager.get_workspace_logs(workspace_id, user_id)
    print(f"Log entries: {len(logs)}")
    for log in logs:
        print(f"- {log['action_type']} by {log['user_id']} at {log['timestamp']}")