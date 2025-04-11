#!/usr/bin/env python3
"""
Memory Manager Module for AI App Store Workspaces

This module provides functionality for managing memory within workspaces,
enabling context retention, history tracking, and efficient retrieval
of past actions and data.
"""

import enum
import uuid
import logging
import datetime
import json
import time
from typing import Dict, List, Any, Optional, Union, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MemoryType(enum.Enum):
    """Enum representing the possible types of memory"""
    CONVERSATION = "conversation"
    ACTION = "action"
    DATA = "data"
    WORKFLOW = "workflow"
    DOCUMENT = "document"
    RESULT = "result"
    CUSTOM = "custom"


class RetentionPolicy:
    """Represents a retention policy for memory items"""
    
    def __init__(self, duration_days: int = 90, max_items: Optional[int] = None):
        self.duration_days = duration_days
        self.max_items = max_items
        
    def should_retain(self, creation_time: datetime.datetime, 
                     current_position: Optional[int] = None,
                     total_items: Optional[int] = None) -> bool:
        """Check if an item should be retained based on this policy"""
        # Check time-based retention
        time_diff = datetime.datetime.utcnow() - creation_time
        if time_diff.days > self.duration_days:
            return False
            
        # Check count-based retention if applicable
        if self.max_items is not None and current_position is not None and total_items is not None:
            if total_items > self.max_items and current_position < (total_items - self.max_items):
                return False
                
        return True
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "duration_days": self.duration_days,
            "max_items": self.max_items
        }


class MemoryItem:
    """Represents a single item in memory"""
    
    def __init__(self, memory_type: MemoryType, content: Any, metadata: Optional[Dict[str, Any]] = None):
        self.id = str(uuid.uuid4())
        self.memory_type = memory_type
        self.content = content
        self.metadata = metadata or {}
        self.created_at = datetime.datetime.utcnow()
        self.accessed_at = self.created_at
        self.access_count = 0
        self.vectorized = False
        self.vector = None  # For vector-based retrieval
        
    def access(self) -> None:
        """Record an access to this memory item"""
        self.accessed_at = datetime.datetime.utcnow()
        self.access_count += 1
        
    def set_vector(self, vector: List[float]) -> None:
        """Set the vector representation of this item"""
        self.vector = vector
        self.vectorized = True
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "memory_type": self.memory_type.value,
            "content": self.content,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "accessed_at": self.accessed_at.isoformat(),
            "access_count": self.access_count,
            "vectorized": self.vectorized
        }


class MemoryBlock:
    """Represents a block of related memory items"""
    
    def __init__(self, name: str, description: Optional[str] = None):
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.items: Dict[str, MemoryItem] = {}
        self.created_at = datetime.datetime.utcnow()
        self.updated_at = self.created_at
        self.retention_policy = RetentionPolicy()
        
    def add_item(self, memory_type: MemoryType, content: Any, 
                metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add an item to this memory block"""
        item = MemoryItem(memory_type, content, metadata)
        self.items[item.id] = item
        self.updated_at = datetime.datetime.utcnow()
        return item.id
        
    def get_item(self, item_id: str) -> Optional[MemoryItem]:
        """Get an item by ID"""
        item = self.items.get(item_id)
        if item:
            item.access()
        return item
        
    def set_retention_policy(self, duration_days: int, max_items: Optional[int] = None) -> None:
        """Set the retention policy for this memory block"""
        self.retention_policy = RetentionPolicy(duration_days, max_items)
        
    def apply_retention_policy(self) -> int:
        """Apply the retention policy and remove expired items"""
        items_to_remove = []
        total_items = len(self.items)
        
        # Sort items by creation time (oldest first)
        sorted_items = sorted(self.items.values(), key=lambda x: x.created_at)
        
        for i, item in enumerate(sorted_items):
            if not self.retention_policy.should_retain(item.created_at, i, total_items):
                items_to_remove.append(item.id)
                
        # Remove expired items
        for item_id in items_to_remove:
            del self.items[item_id]
            
        if items_to_remove:
            self.updated_at = datetime.datetime.utcnow()
            
        return len(items_to_remove)
        
    def query_items(self, memory_type: Optional[MemoryType] = None, 
                   metadata_filters: Optional[Dict[str, Any]] = None,
                   time_range: Optional[Tuple[datetime.datetime, datetime.datetime]] = None) -> List[MemoryItem]:
        """Query items based on filters"""
        results = []
        
        for item in self.items.values():
            # Filter by memory type
            if memory_type and item.memory_type != memory_type:
                continue
                
            # Filter by metadata
            if metadata_filters:
                match = True
                for key, value in metadata_filters.items():
                    if key not in item.metadata or item.metadata[key] != value:
                        match = False
                        break
                        
                if not match:
                    continue
                    
            # Filter by time range
            if time_range:
                start_time, end_time = time_range
                if item.created_at < start_time or item.created_at > end_time:
                    continue
                    
            results.append(item)
            item.access()
            
        return results
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "item_count": len(self.items),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "retention_policy": self.retention_policy.to_dict()
        }


class ConversationMemory:
    """Specialized memory for conversations"""
    
    def __init__(self, name: str):
        self.block = MemoryBlock(name, "Conversation history")
        self.messages = []  # Ordered list of message IDs
        
    def add_message(self, role: str, content: str, 
                   metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add a message to the conversation"""
        full_metadata = metadata or {}
        full_metadata["role"] = role
        
        item_id = self.block.add_item(
            MemoryType.CONVERSATION,
            content,
            full_metadata
        )
        
        self.messages.append(item_id)
        return item_id
        
    def get_messages(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get the conversation messages"""
        result = []
        
        # Get the most recent messages if limit is specified
        message_ids = self.messages
        if limit is not None:
            message_ids = message_ids[-limit:]
            
        for item_id in message_ids:
            item = self.block.get_item(item_id)
            if item:
                result.append({
                    "id": item.id,
                    "role": item.metadata.get("role", "unknown"),
                    "content": item.content,
                    "timestamp": item.created_at.isoformat()
                })
                
        return result
        
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get a summary of the conversation"""
        message_count = len(self.messages)
        
        if message_count == 0:
            return {
                "message_count": 0,
                "started_at": None,
                "last_message_at": None,
                "roles": []
            }
            
        roles = set()
        started_at = None
        last_message_at = None
        
        for item_id in self.messages:
            item = self.block.get_item(item_id)
            if item:
                role = item.metadata.get("role", "unknown")
                roles.add(role)
                
                if started_at is None or item.created_at < started_at:
                    started_at = item.created_at
                    
                if last_message_at is None or item.created_at > last_message_at:
                    last_message_at = item.created_at
                    
        return {
            "message_count": message_count,
            "started_at": started_at.isoformat() if started_at else None,
            "last_message_at": last_message_at.isoformat() if last_message_at else None,
            "roles": list(roles)
        }
        
    def clear(self) -> None:
        """Clear the conversation history"""
        self.messages = []
        self.block = MemoryBlock(self.block.name, self.block.description)


class WorkflowMemory:
    """Specialized memory for workflows"""
    
    def __init__(self, name: str, workflow_id: str):
        self.block = MemoryBlock(name, f"Workflow memory for {workflow_id}")
        self.workflow_id = workflow_id
        self.actions = []  # Ordered list of action IDs
        
    def add_action(self, action_type: str, app_id: str, data: Dict[str, Any],
                 result: Optional[Dict[str, Any]] = None) -> str:
        """Add an action to the workflow memory"""
        metadata = {
            "action_type": action_type,
            "app_id": app_id,
            "workflow_id": self.workflow_id
        }
        
        content = {
            "data": data,
            "result": result
        }
        
        item_id = self.block.add_item(
            MemoryType.ACTION,
            content,
            metadata
        )
        
        self.actions.append(item_id)
        return item_id
        
    def update_action_result(self, action_id: str, result: Dict[str, Any]) -> bool:
        """Update the result of an action"""
        item = self.block.get_item(action_id)
        if not item or item.memory_type != MemoryType.ACTION:
            return False
            
        content = item.content
        content["result"] = result
        item.content = content
        
        return True
        
    def get_actions(self, action_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get the workflow actions"""
        result = []
        
        for item_id in self.actions:
            item = self.block.get_item(item_id)
            if not item:
                continue
                
            if action_type and item.metadata.get("action_type") != action_type:
                continue
                
            result.append({
                "id": item.id,
                "action_type": item.metadata.get("action_type"),
                "app_id": item.metadata.get("app_id"),
                "data": item.content.get("data"),
                "result": item.content.get("result"),
                "timestamp": item.created_at.isoformat()
            })
            
        return result
        
    def get_latest_action(self) -> Optional[Dict[str, Any]]:
        """Get the latest action"""
        if not self.actions:
            return None
            
        item_id = self.actions[-1]
        item = self.block.get_item(item_id)
        
        if not item:
            return None
            
        return {
            "id": item.id,
            "action_type": item.metadata.get("action_type"),
            "app_id": item.metadata.get("app_id"),
            "data": item.content.get("data"),
            "result": item.content.get("result"),
            "timestamp": item.created_at.isoformat()
        }
        
    def store_data(self, key: str, value: Any, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Store data in the workflow memory"""
        full_metadata = metadata or {}
        full_metadata["key"] = key
        full_metadata["workflow_id"] = self.workflow_id
        
        return self.block.add_item(
            MemoryType.DATA,
            value,
            full_metadata
        )
        
    def get_data(self, key: str) -> Optional[Any]:
        """Get data from the workflow memory"""
        for item in self.block.items.values():
            if (item.memory_type == MemoryType.DATA and 
                item.metadata.get("key") == key and 
                item.metadata.get("workflow_id") == self.workflow_id):
                item.access()
                return item.content
                
        return None


class CheckpointManager:
    """Manages checkpoints for workflows"""
    
    def __init__(self):
        self.checkpoints: Dict[str, Dict[str, Any]] = {}
        
    def create_checkpoint(self, workflow_id: str, name: str, 
                         memory_snapshot: Dict[str, Any],
                         expected_outcomes: Optional[Dict[str, Any]] = None) -> str:
        """Create a checkpoint"""
        checkpoint_id = str(uuid.uuid4())
        
        checkpoint = {
            "id": checkpoint_id,
            "workflow_id": workflow_id,
            "name": name,
            "memory_snapshot": memory_snapshot,
            "expected_outcomes": expected_outcomes or {},
            "created_at": datetime.datetime.utcnow().isoformat()
        }
        
        self.checkpoints[checkpoint_id] = checkpoint
        return checkpoint_id
        
    def get_checkpoint(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        """Get a checkpoint by ID"""
        return self.checkpoints.get(checkpoint_id)
        
    def list_checkpoints(self, workflow_id: str) -> List[Dict[str, Any]]:
        """List checkpoints for a workflow"""
        return [
            {
                "id": checkpoint["id"],
                "name": checkpoint["name"],
                "created_at": checkpoint["created_at"],
                "expected_outcomes": checkpoint["expected_outcomes"]
            }
            for checkpoint in self.checkpoints.values()
            if checkpoint["workflow_id"] == workflow_id
        ]
        
    def restore_checkpoint(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        """Restore a memory snapshot from a checkpoint"""
        checkpoint = self.checkpoints.get(checkpoint_id)
        if not checkpoint:
            return None
            
        return checkpoint["memory_snapshot"]


class MemoryManager:
    """Main class for managing workspace memory"""
    
    def __init__(self):
        self.memory_blocks: Dict[str, MemoryBlock] = {}
        self.conversations: Dict[str, ConversationMemory] = {}
        self.workflow_memories: Dict[str, WorkflowMemory] = {}
        self.checkpoint_manager = CheckpointManager()
        
    def create_memory_block(self, name: str, 
                           description: Optional[str] = None) -> str:
        """Create a new memory block"""
        block = MemoryBlock(name, description)
        self.memory_blocks[block.id] = block
        return block.id
        
    def get_memory_block(self, block_id: str) -> Optional[MemoryBlock]:
        """Get a memory block by ID"""
        return self.memory_blocks.get(block_id)
        
    def create_conversation_memory(self, name: str) -> str:
        """Create a new conversation memory"""
        conversation = ConversationMemory(name)
        self.conversations[conversation.block.id] = conversation
        self.memory_blocks[conversation.block.id] = conversation.block
        return conversation.block.id
        
    def get_conversation_memory(self, block_id: str) -> Optional[ConversationMemory]:
        """Get a conversation memory by ID"""
        return self.conversations.get(block_id)
        
    def create_workflow_memory(self, name: str, workflow_id: str) -> str:
        """Create a new workflow memory"""
        workflow_memory = WorkflowMemory(name, workflow_id)
        self.workflow_memories[workflow_memory.block.id] = workflow_memory
        self.memory_blocks[workflow_memory.block.id] = workflow_memory.block
        return workflow_memory.block.id
        
    def get_workflow_memory(self, block_id: str) -> Optional[WorkflowMemory]:
        """Get a workflow memory by ID"""
        return self.workflow_memories.get(block_id)
        
    def add_memory_item(self, block_id: str, memory_type: MemoryType, 
                       content: Any, metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Add an item to a memory block"""
        block = self.memory_blocks.get(block_id)
        if not block:
            return None
            
        return block.add_item(memory_type, content, metadata)
        
    def get_memory_item(self, block_id: str, item_id: str) -> Optional[MemoryItem]:
        """Get a memory item"""
        block = self.memory_blocks.get(block_id)
        if not block:
            return None
            
        return block.get_item(item_id)
        
    def query_memory(self, block_id: str, memory_type: Optional[MemoryType] = None,
                    metadata_filters: Optional[Dict[str, Any]] = None,
                    time_range: Optional[Tuple[datetime.datetime, datetime.datetime]] = None) -> List[Dict[str, Any]]:
        """Query memory items"""
        block = self.memory_blocks.get(block_id)
        if not block:
            return []
            
        items = block.query_items(memory_type, metadata_filters, time_range)
        return [item.to_dict() for item in items]
        
    def create_checkpoint(self, workflow_id: str, name: str, 
                         expected_outcomes: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Create a checkpoint for a workflow"""
        # Find the workflow memory
        workflow_memory = None
        for wm in self.workflow_memories.values():
            if wm.workflow_id == workflow_id:
                workflow_memory = wm
                break
                
        if not workflow_memory:
            return None
            
        # Create a snapshot of the workflow memory
        memory_snapshot = {
            "actions": workflow_memory.get_actions(),
            "data": {}
        }
        
        # Capture all stored data
        for item in workflow_memory.block.items.values():
            if item.memory_type == MemoryType.DATA:
                key = item.metadata.get("key")
                if key:
                    memory_snapshot["data"][key] = item.content
                    
        return self.checkpoint_manager.create_checkpoint(
            workflow_id, name, memory_snapshot, expected_outcomes)
        
    def restore_checkpoint(self, checkpoint_id: str, target_workflow_id: str) -> bool:
        """Restore a workflow from a checkpoint"""
        snapshot = self.checkpoint_manager.restore_checkpoint(checkpoint_id)
        if not snapshot:
            return False
            
        # Find the target workflow memory
        target_memory = None
        for wm in self.workflow_memories.values():
            if wm.workflow_id == target_workflow_id:
                target_memory = wm
                break
                
        if not target_memory:
            return False
            
        # Clear existing memory and restore from snapshot
        target_memory.actions = []
        
        # Create a new memory block
        old_block_id = target_memory.block.id
        old_block_name = target_memory.block.name
        target_memory.block = MemoryBlock(old_block_name, f"Restored workflow memory for {target_workflow_id}")
        
        # Update dictionaries with the new block
        self.memory_blocks[target_memory.block.id] = target_memory.block
        self.workflow_memories[target_memory.block.id] = target_memory
        del self.memory_blocks[old_block_id]
        del self.workflow_memories[old_block_id]
        
        # Restore actions
        for action in snapshot["actions"]:
            item_id = target_memory.add_action(
                action["action_type"],
                action["app_id"],
                action["data"],
                action["result"]
            )
            
        # Restore data
        for key, value in snapshot["data"].items():
            target_memory.store_data(key, value)
            
        return True
        
    def apply_retention_policies(self) -> Dict[str, int]:
        """Apply retention policies to all memory blocks"""
        result = {}
        
        for block_id, block in self.memory_blocks.items():
            removed_count = block.apply_retention_policy()
            if removed_count > 0:
                result[block_id] = removed_count
                
        return result


# Example usage
if __name__ == "__main__":
    # Create memory manager
    manager = MemoryManager()
    
    # Create a conversation memory
    conversation_id = manager.create_conversation_memory("Customer Support Conversation")
    conversation = manager.get_conversation_memory(conversation_id)
    
    if conversation:
        # Add messages to the conversation
        conversation.add_message("user", "I need help with my loan application.")
        conversation.add_message("assistant", "I'd be happy to help. What's the issue you're experiencing?")
        conversation.add_message("user", "I submitted it last week but haven't heard back.")
        
        # Get conversation history
        messages = conversation.get_messages()
        print("Conversation:")
        for msg in messages:
            print(f"[{msg['role']}] {msg['content']}")
            
        # Get conversation summary
        summary = conversation.get_conversation_summary()
        print(f"\nMessage count: {summary['message_count']}")
        print(f"Started: {summary['started_at']}")
        print(f"Last message: {summary['last_message_at']}")
        
    # Create a workflow memory
    workflow_id = "workflow-789"
    workflow_memory_id = manager.create_workflow_memory("Loan Processing Workflow", workflow_id)
    workflow_memory = manager.get_workflow_memory(workflow_memory_id)
    
    if workflow_memory:
        # Add actions to the workflow
        action1_id = workflow_memory.add_action(
            "load_application",
            "app-123",
            {"application_id": "APP-456"}
        )
        
        # Update with a result
        workflow_memory.update_action_result(
            action1_id,
            {"status": "success", "data": {"applicant": "John Doe", "amount": 250000}}
        )
        
        action2_id = workflow_memory.add_action(
            "verify_identity",
            "app-789",
            {"applicant_id": "CUST-101", "method": "document_verification"}
        )
        
        workflow_memory.update_action_result(
            action2_id,
            {"status": "success", "verified": True, "confidence": 0.95}
        )
        
        # Store data in workflow memory
        workflow_memory.store_data("verification_result", {"verified": True, "method": "document"})
        workflow_memory.store_data("credit_score", 720)
        
        # Create a checkpoint
        checkpoint_id = manager.create_checkpoint(
            workflow_id,
            "After Identity Verification",
            {"verified": True, "proceed_to": "risk_assessment"}
        )
        print(f"\nCreated checkpoint: {checkpoint_id}")
        
        # Get workflow actions
        actions = workflow_memory.get_actions()
        print("\nWorkflow actions:")
        for action in actions:
            print(f"- {action['action_type']} using {action['app_id']}: {action['result']['status']}")
            
        # Get stored data
        credit_score = workflow_memory.get_data("credit_score")
        print(f"\nStored credit score: {credit_score}")
        
        # List checkpoints
        checkpoints = manager.checkpoint_manager.list_checkpoints(workflow_id)
        print("\nCheckpoints:")
        for cp in checkpoints:
            print(f"- {cp['name']} ({cp['id']})")
            
        # Simulate restoring from a checkpoint
        print("\nRestoring from checkpoint...")
        success = manager.restore_checkpoint(checkpoint_id, workflow_id)
        print(f"Restore {'succeeded' if success else 'failed'}")
        
        if success:
            actions = workflow_memory.get_actions()
            print("\nActions after restore:")
            for action in actions:
                print(f"- {action['action_type']} using {action['app_id']}")
                
            credit_score = workflow_memory.get_data("credit_score")
            print(f"\nCredit score after restore: {credit_score}")