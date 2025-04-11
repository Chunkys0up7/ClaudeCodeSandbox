#!/usr/bin/env python3
"""
Security and Privacy Module for AI App Store Workspaces

This module provides functionality for security and privacy controls,
including access management, data protection, and compliance monitoring.
"""

import enum
import uuid
import logging
import datetime
import json
import hashlib
import base64
import os
import re
from typing import Dict, List, Any, Optional, Set, Union, Tuple, Callable

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PermissionLevel(enum.Enum):
    """Enum representing permission levels"""
    NONE = "none"
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"
    OWNER = "owner"


class ResourceType(enum.Enum):
    """Enum representing resource types for permissions"""
    WORKSPACE = "workspace"
    CHAT = "chat"
    WORKFLOW = "workflow"
    APP = "app"
    DATA = "data"
    CODE = "code"
    FILE = "file"
    CUSTOM = "custom"


class DataSensitivity(enum.Enum):
    """Enum representing data sensitivity levels"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    PII = "pii"  # Personally Identifiable Information


class Permission:
    """Represents a permission for a resource"""
    
    def __init__(self, resource_type: ResourceType, resource_id: str, 
                user_id: str, level: PermissionLevel):
        self.id = str(uuid.uuid4())
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.user_id = user_id
        self.level = level
        self.granted_by = None
        self.granted_at = datetime.datetime.utcnow()
        self.expires_at = None
        self.conditions = {}
        
    def set_granted_by(self, user_id: str) -> None:
        """Set who granted this permission"""
        self.granted_by = user_id
        
    def set_expiration(self, expires_at: datetime.datetime) -> None:
        """Set an expiration time for the permission"""
        self.expires_at = expires_at
        
    def add_condition(self, name: str, value: Any) -> None:
        """Add a condition to the permission"""
        self.conditions[name] = value
        
    def is_expired(self) -> bool:
        """Check if the permission is expired"""
        if not self.expires_at:
            return False
        return datetime.datetime.utcnow() > self.expires_at
        
    def allows(self, required_level: PermissionLevel) -> bool:
        """Check if this permission allows a required permission level"""
        if self.is_expired():
            return False
            
        # Permission levels have a hierarchy
        level_hierarchy = {
            PermissionLevel.NONE: 0,
            PermissionLevel.READ: 1,
            PermissionLevel.WRITE: 2,
            PermissionLevel.ADMIN: 3,
            PermissionLevel.OWNER: 4
        }
        
        return level_hierarchy[self.level] >= level_hierarchy[required_level]
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "resource_type": self.resource_type.value,
            "resource_id": self.resource_id,
            "user_id": self.user_id,
            "level": self.level.value,
            "granted_by": self.granted_by,
            "granted_at": self.granted_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "conditions": self.conditions
        }


class AccessPolicy:
    """Represents an access policy for resources"""
    
    def __init__(self, name: str, description: str, created_by: str):
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.created_by = created_by
        self.rules = []
        self.created_at = datetime.datetime.utcnow()
        self.updated_at = self.created_at
        
    def add_rule(self, resource_type: ResourceType, resource_pattern: str,
                level: PermissionLevel, user_pattern: str = "*",
                conditions: Optional[Dict[str, Any]] = None) -> str:
        """Add a rule to the policy"""
        rule_id = str(uuid.uuid4())
        
        rule = {
            "id": rule_id,
            "resource_type": resource_type.value,
            "resource_pattern": resource_pattern,
            "user_pattern": user_pattern,
            "level": level.value,
            "conditions": conditions or {},
            "created_at": datetime.datetime.utcnow().isoformat()
        }
        
        self.rules.append(rule)
        self.updated_at = datetime.datetime.utcnow()
        return rule_id
        
    def remove_rule(self, rule_id: str) -> bool:
        """Remove a rule from the policy"""
        for i, rule in enumerate(self.rules):
            if rule["id"] == rule_id:
                self.rules.pop(i)
                self.updated_at = datetime.datetime.utcnow()
                return True
        return False
        
    def matches_resource(self, resource_type: ResourceType, resource_id: str, 
                        user_id: str) -> Tuple[bool, Optional[PermissionLevel], Dict[str, Any]]:
        """Check if a resource matches any rules in this policy"""
        matching_level = None
        matching_conditions = {}
        
        for rule in self.rules:
            # Check resource type
            if rule["resource_type"] != resource_type.value:
                continue
                
            # Check resource pattern
            if not self._matches_pattern(resource_id, rule["resource_pattern"]):
                continue
                
            # Check user pattern
            if not self._matches_pattern(user_id, rule["user_pattern"]):
                continue
                
            # We have a match, remember the permission level
            rule_level = PermissionLevel(rule["level"])
            
            # Use the highest permission level if multiple rules match
            if matching_level is None or self._is_higher_level(rule_level, matching_level):
                matching_level = rule_level
                matching_conditions = rule["conditions"]
                
        return matching_level is not None, matching_level, matching_conditions
        
    def _matches_pattern(self, value: str, pattern: str) -> bool:
        """Check if a value matches a pattern"""
        if pattern == "*":
            return True
            
        # Support simple wildcards with regex
        regex_pattern = "^" + pattern.replace("*", ".*") + "$"
        return bool(re.match(regex_pattern, value))
        
    def _is_higher_level(self, level1: PermissionLevel, level2: PermissionLevel) -> bool:
        """Check if level1 is higher than level2"""
        level_hierarchy = {
            PermissionLevel.NONE: 0,
            PermissionLevel.READ: 1,
            PermissionLevel.WRITE: 2,
            PermissionLevel.ADMIN: 3,
            PermissionLevel.OWNER: 4
        }
        
        return level_hierarchy[level1] > level_hierarchy[level2]
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_by": self.created_by,
            "rules": self.rules,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class DataProtection:
    """Handles data protection and encryption"""
    
    def __init__(self, encryption_key: Optional[str] = None):
        """Initialize with an optional encryption key"""
        # In a real implementation, this would use proper key management
        if encryption_key:
            self.encryption_key = encryption_key
        else:
            # Generate a random key for demo purposes
            self.encryption_key = base64.b64encode(os.urandom(32)).decode('utf-8')
            
    def encrypt_data(self, data: str) -> Dict[str, str]:
        """Encrypt data"""
        if not data:
            return {"encrypted": "", "method": "none"}
            
        # In a real implementation, this would use proper encryption libraries
        # For this demo, we'll use a simple hash-based approach
        
        # Generate a random salt
        salt = os.urandom(16)
        salt_str = base64.b64encode(salt).decode('utf-8')
        
        # Create key material
        key_material = hashlib.sha256((self.encryption_key + salt_str).encode()).digest()
        
        # XOR the data with the key material (not secure, just for demo)
        data_bytes = data.encode('utf-8')
        encrypted_bytes = bytearray()
        
        for i in range(len(data_bytes)):
            key_byte = key_material[i % len(key_material)]
            encrypted_bytes.append(data_bytes[i] ^ key_byte)
            
        encrypted = base64.b64encode(encrypted_bytes).decode('utf-8')
        
        return {
            "encrypted": encrypted,
            "salt": salt_str,
            "method": "xor-sha256"  # Not a real encryption method, just for demo
        }
        
    def decrypt_data(self, encrypted_data: Dict[str, str]) -> Optional[str]:
        """Decrypt data"""
        if not encrypted_data or not encrypted_data.get("encrypted"):
            return ""
            
        if encrypted_data.get("method") == "none":
            return encrypted_data.get("encrypted", "")
            
        try:
            method = encrypted_data.get("method")
            
            if method != "xor-sha256":
                logger.error(f"Unsupported encryption method: {method}")
                return None
                
            salt_str = encrypted_data.get("salt", "")
            
            # Create key material
            key_material = hashlib.sha256((self.encryption_key + salt_str).encode()).digest()
            
            # Decode encrypted data
            encrypted_bytes = base64.b64decode(encrypted_data.get("encrypted", ""))
            
            # XOR to decrypt
            decrypted_bytes = bytearray()
            
            for i in range(len(encrypted_bytes)):
                key_byte = key_material[i % len(key_material)]
                decrypted_bytes.append(encrypted_bytes[i] ^ key_byte)
                
            return decrypted_bytes.decode('utf-8')
            
        except Exception as e:
            logger.error(f"Error decrypting data: {str(e)}")
            return None
            
    def mask_pii(self, text: str) -> str:
        """Mask personally identifiable information in text"""
        if not text:
            return ""
            
        # Mask potential PII
        # Note: In a real implementation, this would use more sophisticated techniques
        
        # Mask email addresses
        text = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '[EMAIL REDACTED]', text)
        
        # Mask phone numbers (simple pattern)
        text = re.sub(r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b', '[PHONE REDACTED]', text)
        
        # Mask SSNs (simple pattern)
        text = re.sub(r'\b\d{3}[-.\s]?\d{2}[-.\s]?\d{4}\b', '[SSN REDACTED]', text)
        
        # Mask credit card numbers (simple pattern)
        text = re.sub(r'\b\d{4}[-.\s]?\d{4}[-.\s]?\d{4}[-.\s]?\d{4}\b', '[CARD REDACTED]', text)
        
        return text
        
    def detect_sensitive_data(self, text: str) -> Dict[str, List[str]]:
        """Detect sensitive data in text"""
        if not text:
            return {"sensitivity": [], "detected": []}
            
        sensitivity = []
        detected = []
        
        # Check for PII
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        phone_pattern = r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b'
        ssn_pattern = r'\b\d{3}[-.\s]?\d{2}[-.\s]?\d{4}\b'
        card_pattern = r'\b\d{4}[-.\s]?\d{4}[-.\s]?\d{4}[-.\s]?\d{4}\b'
        
        if re.search(email_pattern, text):
            sensitivity.append(DataSensitivity.PII.value)
            detected.append("email_address")
            
        if re.search(phone_pattern, text):
            sensitivity.append(DataSensitivity.PII.value)
            detected.append("phone_number")
            
        if re.search(ssn_pattern, text):
            sensitivity.append(DataSensitivity.RESTRICTED.value)
            detected.append("social_security_number")
            
        if re.search(card_pattern, text):
            sensitivity.append(DataSensitivity.RESTRICTED.value)
            detected.append("credit_card_number")
            
        # Check for potentially confidential terms
        confidential_terms = [
            r"\bconfidential\b", 
            r"\bproprietary\b", 
            r"\binternal\suse\sonly\b",
            r"\brestricted\b",
            r"\bnot\sfor\sdistribution\b"
        ]
        
        for term in confidential_terms:
            if re.search(term, text, re.IGNORECASE):
                sensitivity.append(DataSensitivity.CONFIDENTIAL.value)
                detected.append("confidential_terms")
                break
                
        # Return unique sensitivity levels
        return {
            "sensitivity": list(set(sensitivity)),
            "detected": list(set(detected))
        }
        
    def scan_file_content(self, content: str, file_path: str) -> Dict[str, Any]:
        """Scan file content for sensitive data"""
        result = self.detect_sensitive_data(content)
        
        # Additional file-specific checks
        file_ext = os.path.splitext(file_path)[1].lower()
        
        # Check for potential secrets in code files
        if file_ext in ['.py', '.js', '.java', '.cs', '.go', '.rb', '.php']:
            secret_patterns = [
                r'api[_\-]?key[_\-]?=\s*[\'"][^\'"]+[\'"]',
                r'access[_\-]?token[_\-]?=\s*[\'"][^\'"]+[\'"]',
                r'password[_\-]?=\s*[\'"][^\'"]+[\'"]',
                r'secret[_\-]?=\s*[\'"][^\'"]+[\'"]',
                r'BEGIN\s+PRIVATE\s+KEY',
                r'BEGIN\s+RSA\s+PRIVATE\s+KEY'
            ]
            
            for pattern in secret_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    if DataSensitivity.RESTRICTED.value not in result["sensitivity"]:
                        result["sensitivity"].append(DataSensitivity.RESTRICTED.value)
                        
                    result["detected"].append("potential_secret")
                    break
                    
        return result


class AuditLog:
    """Represents an audit log for security-related events"""
    
    def __init__(self):
        self.entries = []
        
    def add_entry(self, event_type: str, user_id: str, resource_type: str,
                resource_id: str, action: str, status: str,
                details: Optional[Dict[str, Any]] = None) -> str:
        """Add an entry to the audit log"""
        entry_id = str(uuid.uuid4())
        
        entry = {
            "id": entry_id,
            "event_type": event_type,
            "user_id": user_id,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "action": action,
            "status": status,  # success, failure, denied
            "details": details or {},
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "ip_address": self._get_placeholder_ip()  # In a real implementation, this would be the actual IP
        }
        
        self.entries.append(entry)
        return entry_id
        
    def _get_placeholder_ip(self) -> str:
        """Get a placeholder IP address"""
        return "127.0.0.1"
        
    def get_entries(self, filters: Optional[Dict[str, Any]] = None,
                  start_time: Optional[datetime.datetime] = None,
                  end_time: Optional[datetime.datetime] = None,
                  limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get audit log entries, optionally filtered"""
        result = []
        
        for entry in self.entries:
            # Apply time filters
            entry_time = datetime.datetime.fromisoformat(entry["timestamp"].replace("Z", "+00:00"))
            
            if start_time and entry_time < start_time:
                continue
                
            if end_time and entry_time > end_time:
                continue
                
            # Apply other filters
            if filters:
                match = True
                for key, value in filters.items():
                    if key in entry and entry[key] != value:
                        match = False
                        break
                        
                if not match:
                    continue
                    
            result.append(entry)
            
        # Apply limit
        if limit is not None and limit > 0:
            result = result[-limit:]
            
        return result
        
    def get_user_activity(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get a summary of user activity"""
        now = datetime.datetime.utcnow()
        start_time = now - datetime.timedelta(days=days)
        
        entries = self.get_entries(
            filters={"user_id": user_id},
            start_time=start_time
        )
        
        # Group by action and resource type
        action_counts = {}
        resource_counts = {}
        status_counts = {"success": 0, "failure": 0, "denied": 0}
        
        for entry in entries:
            action = entry["action"]
            resource_type = entry["resource_type"]
            status = entry["status"]
            
            action_counts[action] = action_counts.get(action, 0) + 1
            resource_counts[resource_type] = resource_counts.get(resource_type, 0) + 1
            status_counts[status] = status_counts.get(status, 0) + 1
            
        return {
            "user_id": user_id,
            "period_days": days,
            "total_activities": len(entries),
            "action_summary": action_counts,
            "resource_summary": resource_counts,
            "status_summary": status_counts
        }


class SecurityManager:
    """Main class for managing workspace security"""
    
    def __init__(self):
        self.permissions: Dict[str, Permission] = {}
        self.policies: Dict[str, AccessPolicy] = {}
        self.data_protection = DataProtection()
        self.audit_log = AuditLog()
        
        # Create default policies
        self._create_default_policies()
        
    def _create_default_policies(self) -> None:
        """Create default access policies"""
        # Default workspace policy
        workspace_policy = AccessPolicy(
            "Default Workspace Policy",
            "Default policy for workspace access",
            "system"
        )
        
        # Owners have full access
        workspace_policy.add_rule(
            ResourceType.WORKSPACE,
            "*",
            PermissionLevel.OWNER,
            user_pattern="*",
            conditions={"is_workspace_owner": True}
        )
        
        # Members have write access
        workspace_policy.add_rule(
            ResourceType.WORKSPACE,
            "*",
            PermissionLevel.WRITE,
            user_pattern="*",
            conditions={"is_workspace_member": True}
        )
        
        self.policies[workspace_policy.id] = workspace_policy
        
    def create_permission(self, resource_type: ResourceType, resource_id: str,
                        user_id: str, level: PermissionLevel,
                        granted_by: str) -> str:
        """Create a permission for a resource"""
        permission = Permission(resource_type, resource_id, user_id, level)
        permission.set_granted_by(granted_by)
        
        self.permissions[permission.id] = permission
        
        # Add audit log entry
        self.audit_log.add_entry(
            "permission_granted",
            granted_by,
            resource_type.value,
            resource_id,
            "grant_permission",
            "success",
            {
                "user_id": user_id,
                "permission_level": level.value,
                "permission_id": permission.id
            }
        )
        
        return permission.id
        
    def update_permission(self, permission_id: str, level: PermissionLevel, 
                        updated_by: str) -> bool:
        """Update a permission level"""
        permission = self.permissions.get(permission_id)
        if not permission:
            # Add audit log entry
            self.audit_log.add_entry(
                "permission_update",
                updated_by,
                "permission",
                permission_id,
                "update_permission",
                "failure",
                {"error": "Permission not found"}
            )
            return False
            
        permission.level = level
        
        # Add audit log entry
        self.audit_log.add_entry(
            "permission_updated",
            updated_by,
            permission.resource_type.value,
            permission.resource_id,
            "update_permission",
            "success",
            {
                "user_id": permission.user_id,
                "permission_level": level.value,
                "permission_id": permission_id
            }
        )
        
        return True
        
    def revoke_permission(self, permission_id: str, revoked_by: str) -> bool:
        """Revoke a permission"""
        permission = self.permissions.get(permission_id)
        if not permission:
            # Add audit log entry
            self.audit_log.add_entry(
                "permission_revoke",
                revoked_by,
                "permission",
                permission_id,
                "revoke_permission",
                "failure",
                {"error": "Permission not found"}
            )
            return False
            
        resource_type = permission.resource_type
        resource_id = permission.resource_id
        user_id = permission.user_id
        
        del self.permissions[permission_id]
        
        # Add audit log entry
        self.audit_log.add_entry(
            "permission_revoked",
            revoked_by,
            resource_type.value,
            resource_id,
            "revoke_permission",
            "success",
            {
                "user_id": user_id,
                "permission_id": permission_id
            }
        )
        
        return True
        
    def create_policy(self, name: str, description: str, created_by: str) -> str:
        """Create an access policy"""
        policy = AccessPolicy(name, description, created_by)
        self.policies[policy.id] = policy
        
        # Add audit log entry
        self.audit_log.add_entry(
            "policy_created",
            created_by,
            "policy",
            policy.id,
            "create_policy",
            "success",
            {"policy_name": name}
        )
        
        return policy.id
        
    def add_policy_rule(self, policy_id: str, resource_type: ResourceType, 
                       resource_pattern: str, level: PermissionLevel,
                       user_pattern: str = "*", conditions: Optional[Dict[str, Any]] = None,
                       added_by: str = "system") -> Optional[str]:
        """Add a rule to a policy"""
        policy = self.policies.get(policy_id)
        if not policy:
            # Add audit log entry
            self.audit_log.add_entry(
                "policy_update",
                added_by,
                "policy",
                policy_id,
                "add_rule",
                "failure",
                {"error": "Policy not found"}
            )
            return None
            
        rule_id = policy.add_rule(
            resource_type, resource_pattern, level, user_pattern, conditions)
            
        # Add audit log entry
        self.audit_log.add_entry(
            "policy_updated",
            added_by,
            "policy",
            policy_id,
            "add_rule",
            "success",
            {
                "rule_id": rule_id,
                "resource_type": resource_type.value,
                "level": level.value
            }
        )
        
        return rule_id
        
    def check_permission(self, user_id: str, resource_type: ResourceType, 
                        resource_id: str, required_level: PermissionLevel,
                        context: Optional[Dict[str, Any]] = None) -> Tuple[bool, str]:
        """Check if a user has the required permission for a resource"""
        context = context or {}
        
        # First check direct permissions
        for permission in self.permissions.values():
            if (permission.user_id == user_id and
                permission.resource_type == resource_type and
                permission.resource_id == resource_id and
                permission.allows(required_level) and
                not permission.is_expired()):
                
                # Add audit log entry
                self.audit_log.add_entry(
                    "permission_check",
                    user_id,
                    resource_type.value,
                    resource_id,
                    "check_permission",
                    "success",
                    {
                        "required_level": required_level.value,
                        "granted_by": "direct_permission",
                        "permission_id": permission.id
                    }
                )
                
                return True, f"Granted by direct permission: {permission.id}"
                
        # Then check policies
        for policy in self.policies.values():
            has_match, level, conditions = policy.matches_resource(
                resource_type, resource_id, user_id)
                
            if has_match and level.allows(required_level):
                # Check conditions
                conditions_met = True
                
                for key, value in conditions.items():
                    if key not in context or context[key] != value:
                        conditions_met = False
                        break
                        
                if conditions_met:
                    # Add audit log entry
                    self.audit_log.add_entry(
                        "permission_check",
                        user_id,
                        resource_type.value,
                        resource_id,
                        "check_permission",
                        "success",
                        {
                            "required_level": required_level.value,
                            "granted_by": "policy",
                            "policy_id": policy.id
                        }
                    )
                    
                    return True, f"Granted by policy: {policy.id}"
                    
        # Permission denied
        # Add audit log entry
        self.audit_log.add_entry(
            "permission_check",
            user_id,
            resource_type.value,
            resource_id,
            "check_permission",
            "denied",
            {"required_level": required_level.value}
        )
        
        return False, "Permission denied"
        
    def encrypt_sensitive_data(self, data: str) -> Dict[str, str]:
        """Encrypt sensitive data"""
        return self.data_protection.encrypt_data(data)
        
    def decrypt_sensitive_data(self, encrypted_data: Dict[str, str]) -> Optional[str]:
        """Decrypt sensitive data"""
        return self.data_protection.decrypt_data(encrypted_data)
        
    def scan_content(self, content: str, file_path: Optional[str] = None) -> Dict[str, Any]:
        """Scan content for sensitive data"""
        if file_path:
            return self.data_protection.scan_file_content(content, file_path)
        else:
            return self.data_protection.detect_sensitive_data(content)
            
    def mask_pii(self, text: str) -> str:
        """Mask personally identifiable information in text"""
        return self.data_protection.mask_pii(text)
        
    def log_security_event(self, event_type: str, user_id: str, 
                          resource_type: str, resource_id: str,
                          action: str, status: str,
                          details: Optional[Dict[str, Any]] = None) -> str:
        """Log a security event"""
        return self.audit_log.add_entry(
            event_type, user_id, resource_type, resource_id, action, status, details)
            
    def get_audit_logs(self, filters: Optional[Dict[str, Any]] = None,
                     start_time: Optional[datetime.datetime] = None,
                     end_time: Optional[datetime.datetime] = None,
                     limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get audit logs with filtering"""
        return self.audit_log.get_entries(filters, start_time, end_time, limit)
        
    def get_user_activity(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get a summary of user activity"""
        return self.audit_log.get_user_activity(user_id, days)
        
    def get_user_permissions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all permissions for a user"""
        user_permissions = []
        
        for permission in self.permissions.values():
            if permission.user_id == user_id and not permission.is_expired():
                user_permissions.append(permission.to_dict())
                
        return user_permissions
        
    def get_resource_permissions(self, resource_type: ResourceType, 
                               resource_id: str) -> List[Dict[str, Any]]:
        """Get all permissions for a resource"""
        resource_permissions = []
        
        for permission in self.permissions.values():
            if (permission.resource_type == resource_type and 
                permission.resource_id == resource_id and
                not permission.is_expired()):
                resource_permissions.append(permission.to_dict())
                
        return resource_permissions


# Example usage
if __name__ == "__main__":
    # Create security manager
    manager = SecurityManager()
    
    # Create a workspace resource
    workspace_id = "workspace-123"
    user_id = "user-456"
    admin_id = "admin-789"
    
    # Create permissions
    permission_id = manager.create_permission(
        ResourceType.WORKSPACE,
        workspace_id,
        user_id,
        PermissionLevel.WRITE,
        admin_id
    )
    print(f"Created permission: {permission_id}")
    
    # Check permission
    has_permission, reason = manager.check_permission(
        user_id,
        ResourceType.WORKSPACE,
        workspace_id,
        PermissionLevel.READ
    )
    print(f"User {user_id} has READ permission: {has_permission} - {reason}")
    
    # Create a policy
    policy_id = manager.create_policy(
        "Project Team Policy",
        "Access policy for project team members",
        admin_id
    )
    print(f"Created policy: {policy_id}")
    
    # Add a rule to the policy
    rule_id = manager.add_policy_rule(
        policy_id,
        ResourceType.WORKSPACE,
        f"{workspace_id}*",  # Pattern matching workspace ID and any sub-resources
        PermissionLevel.READ,
        user_pattern="user-*",  # Pattern matching any user ID starting with "user-"
        added_by=admin_id
    )
    print(f"Added rule: {rule_id}")
    
    # Test data protection features
    sensitive_data = "Customer: John Doe\nEmail: john.doe@example.com\nSSN: 123-45-6789\nCard: 4111-1111-1111-1111"
    print("\nOriginal Data:")
    print(sensitive_data)
    
    # Detect sensitive data
    scan_result = manager.scan_content(sensitive_data)
    print("\nSensitivity scan result:")
    print(f"- Sensitivity levels: {scan_result['sensitivity']}")
    print(f"- Detected items: {scan_result['detected']}")
    
    # Mask PII
    masked_data = manager.mask_pii(sensitive_data)
    print("\nMasked Data:")
    print(masked_data)
    
    # Encrypt sensitive data
    encrypted = manager.encrypt_sensitive_data(sensitive_data)
    print("\nEncrypted Data:")
    print(f"- Method: {encrypted['method']}")
    print(f"- Encrypted: {encrypted['encrypted'][:20]}...")
    
    # Decrypt sensitive data
    decrypted = manager.decrypt_sensitive_data(encrypted)
    print("\nDecryption successful:", decrypted == sensitive_data)
    
    # Get audit logs
    logs = manager.get_audit_logs(limit=5)
    print(f"\nRecent audit logs ({len(logs)}):")
    for log in logs:
        print(f"- {log['timestamp']} | {log['event_type']} | {log['user_id']} | {log['action']} | {log['status']}")
        
    # Get user activity summary
    activity = manager.get_user_activity(user_id, days=7)
    print(f"\nUser activity summary for {user_id}:")
    print(f"- Total activities: {activity['total_activities']}")
    print(f"- Status summary: {activity['status_summary']}")