#!/usr/bin/env python3
"""
Client Server Relationship Module for AI App Store Workspaces

This module provides functionality for managing client-server connections,
API integrations, data synchronization, and service orchestration between
workspace clients and backend services.
"""

import uuid
import logging
import datetime
import json
import os
import re
import enum
import time
import threading
import asyncio
import requests
import hashlib
import base64
from typing import Dict, List, Any, Optional, Set, Union, Tuple, Callable, Type
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConnectionStatus(enum.Enum):
    """Enum representing connection status"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"


class AuthType(enum.Enum):
    """Enum representing authentication types"""
    NONE = "none"
    API_KEY = "api_key"
    OAUTH = "oauth"
    JWT = "jwt"
    BASIC = "basic"
    CUSTOM = "custom"


class EndpointType(enum.Enum):
    """Enum representing endpoint types"""
    REST = "rest"
    GRAPHQL = "graphql"
    GRPC = "grpc"
    WEBSOCKET = "websocket"
    CUSTOM = "custom"


class SyncType(enum.Enum):
    """Enum representing data synchronization types"""
    PULL = "pull"
    PUSH = "push"
    BIDIRECTIONAL = "bidirectional"
    EVENT_BASED = "event_based"


class ServiceCredentials:
    """Represents credentials for a service"""
    
    def __init__(self, auth_type: AuthType, credentials: Dict[str, Any] = None):
        self.id = str(uuid.uuid4())
        self.auth_type = auth_type
        self.credentials = credentials or {}
        self.created_at = datetime.datetime.utcnow()
        self.updated_at = self.created_at
        self.expires_at = None
        self.is_valid = True
        
    def set_expiration(self, expires_at: datetime.datetime) -> None:
        """Set credential expiration time"""
        self.expires_at = expires_at
        
    def update_credentials(self, credentials: Dict[str, Any]) -> None:
        """Update credential values"""
        self.credentials.update(credentials)
        self.updated_at = datetime.datetime.utcnow()
        
    def validate(self) -> bool:
        """Validate if credentials are still valid"""
        if not self.is_valid:
            return False
            
        if self.expires_at and datetime.datetime.utcnow() > self.expires_at:
            self.is_valid = False
            return False
            
        return True
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        # Create a safe version without sensitive values
        safe_credentials = {}
        for key, value in self.credentials.items():
            if any(sensitive in key.lower() for sensitive in ['key', 'token', 'password', 'secret']):
                safe_credentials[key] = "********"
            else:
                safe_credentials[key] = value
                
        return {
            "id": self.id,
            "auth_type": self.auth_type.value,
            "credentials": safe_credentials,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "is_valid": self.is_valid
        }


class ServiceEndpoint:
    """Represents an endpoint for a service"""
    
    def __init__(self, name: str, url: str, endpoint_type: EndpointType,
                method: str = "GET", headers: Dict[str, str] = None,
                params: Dict[str, Any] = None):
        self.id = str(uuid.uuid4())
        self.name = name
        self.url = url
        self.endpoint_type = endpoint_type
        self.method = method
        self.headers = headers or {}
        self.params = params or {}
        self.response_mapping = {}
        self.rate_limit = None
        self.timeout = 30  # Default timeout in seconds
        self.retry_config = {
            "max_retries": 3,
            "retry_delay": 1,  # seconds
            "retry_backoff": 2  # multiplier
        }
        
    def add_response_mapping(self, source_path: str, target_path: str) -> None:
        """Add mapping between response fields and target fields"""
        self.response_mapping[source_path] = target_path
        
    def set_rate_limit(self, requests_per_minute: int) -> None:
        """Set rate limit for the endpoint"""
        self.rate_limit = requests_per_minute
        
    def set_timeout(self, timeout_seconds: int) -> None:
        """Set timeout for the endpoint"""
        self.timeout = timeout_seconds
        
    def set_retry_config(self, max_retries: int, retry_delay: int, 
                       retry_backoff: int) -> None:
        """Set retry configuration for the endpoint"""
        self.retry_config = {
            "max_retries": max_retries,
            "retry_delay": retry_delay,
            "retry_backoff": retry_backoff
        }
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "endpoint_type": self.endpoint_type.value,
            "method": self.method,
            "headers": self.headers,
            "params": self.params,
            "response_mapping": self.response_mapping,
            "rate_limit": self.rate_limit,
            "timeout": self.timeout,
            "retry_config": self.retry_config
        }


class ServiceDefinition:
    """Represents a service definition"""
    
    def __init__(self, name: str, base_url: str, description: str = ""):
        self.id = str(uuid.uuid4())
        self.name = name
        self.base_url = base_url
        self.description = description
        self.created_at = datetime.datetime.utcnow()
        self.updated_at = self.created_at
        self.endpoints: Dict[str, ServiceEndpoint] = {}
        self.default_headers = {}
        self.required_auth_type = AuthType.NONE
        
    def add_endpoint(self, endpoint: ServiceEndpoint) -> str:
        """Add an endpoint to the service"""
        self.endpoints[endpoint.id] = endpoint
        self.updated_at = datetime.datetime.utcnow()
        return endpoint.id
        
    def set_default_headers(self, headers: Dict[str, str]) -> None:
        """Set default headers for all endpoints"""
        self.default_headers = headers
        self.updated_at = datetime.datetime.utcnow()
        
    def set_required_auth_type(self, auth_type: AuthType) -> None:
        """Set required authentication type for the service"""
        self.required_auth_type = auth_type
        self.updated_at = datetime.datetime.utcnow()
        
    def validate_url(self) -> bool:
        """Validate the base URL format"""
        try:
            result = urlparse(self.base_url)
            return all([result.scheme, result.netloc])
        except:
            return False
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "name": self.name,
            "base_url": self.base_url,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "endpoint_count": len(self.endpoints),
            "default_headers": self.default_headers,
            "required_auth_type": self.required_auth_type.value
        }


class ServiceConnection:
    """Represents a connection to a service"""
    
    def __init__(self, service_definition_id: str, credentials_id: Optional[str] = None):
        self.id = str(uuid.uuid4())
        self.service_definition_id = service_definition_id
        self.credentials_id = credentials_id
        self.created_at = datetime.datetime.utcnow()
        self.updated_at = self.created_at
        self.status = ConnectionStatus.DISCONNECTED
        self.last_connected = None
        self.last_error = None
        self.connection_meta = {}
        self.request_log = []  # Limited log of recent requests
        self.max_log_entries = 100
        
    def update_status(self, status: ConnectionStatus, error: Optional[str] = None) -> None:
        """Update connection status"""
        self.status = status
        self.updated_at = datetime.datetime.utcnow()
        
        if status == ConnectionStatus.CONNECTED:
            self.last_connected = self.updated_at
            self.last_error = None
        elif status == ConnectionStatus.ERROR:
            self.last_error = error
            
    def log_request(self, endpoint_id: str, request_data: Dict[str, Any], 
                  response_data: Dict[str, Any], status_code: int, 
                  execution_time: float) -> None:
        """Log a request to the service"""
        log_entry = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "endpoint_id": endpoint_id,
            "request_data": self._sanitize_data(request_data),
            "response_status": status_code,
            "execution_time": execution_time,
            "success": 200 <= status_code < 300
        }
        
        # Add summarized response data (limit size)
        response_summary = self._summarize_response(response_data)
        log_entry["response_summary"] = response_summary
        
        self.request_log.append(log_entry)
        
        # Trim log if it's too long
        if len(self.request_log) > self.max_log_entries:
            self.request_log = self.request_log[-self.max_log_entries:]
            
    def _sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive information from request data"""
        if not data:
            return {}
            
        sanitized = {}
        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in ['key', 'token', 'password', 'secret']):
                sanitized[key] = "********"
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_data(value)
            else:
                sanitized[key] = value
                
        return sanitized
        
    def _summarize_response(self, response: Any) -> Dict[str, Any]:
        """Create a summarized version of a response to avoid storing large responses"""
        if not response:
            return {"summary": "Empty response"}
            
        try:
            if isinstance(response, dict):
                # Return first level keys and type/length of values
                summary = {}
                for key, value in response.items():
                    if isinstance(value, dict):
                        summary[key] = f"Object with {len(value)} properties"
                    elif isinstance(value, list):
                        summary[key] = f"Array with {len(value)} items"
                    elif isinstance(value, str) and len(value) > 100:
                        summary[key] = f"String ({len(value)} chars)"
                    else:
                        summary[key] = f"{type(value).__name__}: {str(value)[:100]}"
                return summary
            elif isinstance(response, list):
                return {
                    "type": "Array",
                    "length": len(response),
                    "sample": str(response[0])[:100] if response else "Empty"
                }
            else:
                return {
                    "type": type(response).__name__,
                    "value": str(response)[:100]
                }
        except Exception as e:
            return {"summary_error": str(e)}
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "service_definition_id": self.service_definition_id,
            "credentials_id": self.credentials_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "status": self.status.value,
            "last_connected": self.last_connected.isoformat() if self.last_connected else None,
            "last_error": self.last_error,
            "connection_meta": self.connection_meta,
            "recent_requests": len(self.request_log)
        }


class DataSyncConfig:
    """Configuration for data synchronization between client and server"""
    
    def __init__(self, name: str, source_endpoint_id: str, 
                target_store: str, sync_type: SyncType):
        self.id = str(uuid.uuid4())
        self.name = name
        self.source_endpoint_id = source_endpoint_id
        self.target_store = target_store  # Local storage target
        self.sync_type = sync_type
        self.created_at = datetime.datetime.utcnow()
        self.updated_at = self.created_at
        self.field_mappings = {}
        self.sync_interval_minutes = 60  # Default hourly sync
        self.last_sync = None
        self.filters = {}
        self.transform_scripts = {}
        self.enabled = True
        
    def add_field_mapping(self, source_field: str, target_field: str) -> None:
        """Add mapping between source and target fields"""
        self.field_mappings[source_field] = target_field
        self.updated_at = datetime.datetime.utcnow()
        
    def set_sync_interval(self, interval_minutes: int) -> None:
        """Set synchronization interval in minutes"""
        self.sync_interval_minutes = interval_minutes
        self.updated_at = datetime.datetime.utcnow()
        
    def add_filter(self, field: str, operator: str, value: Any) -> None:
        """Add a filter for data synchronization"""
        if field not in self.filters:
            self.filters[field] = []
            
        self.filters[field].append({
            "operator": operator,  # eq, ne, gt, lt, contains, etc.
            "value": value
        })
        self.updated_at = datetime.datetime.utcnow()
        
    def add_transform_script(self, field: str, script: str) -> None:
        """Add a transformation script for a field"""
        self.transform_scripts[field] = script
        self.updated_at = datetime.datetime.utcnow()
        
    def update_last_sync(self) -> None:
        """Update the last synchronization timestamp"""
        self.last_sync = datetime.datetime.utcnow()
        
    def is_sync_due(self) -> bool:
        """Check if synchronization is due based on interval"""
        if not self.last_sync:
            return True
            
        next_sync = self.last_sync + datetime.timedelta(minutes=self.sync_interval_minutes)
        return datetime.datetime.utcnow() >= next_sync
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "name": self.name,
            "source_endpoint_id": self.source_endpoint_id,
            "target_store": self.target_store,
            "sync_type": self.sync_type.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "field_mappings": self.field_mappings,
            "sync_interval_minutes": self.sync_interval_minutes,
            "last_sync": self.last_sync.isoformat() if self.last_sync else None,
            "filters": self.filters,
            "transform_scripts_count": len(self.transform_scripts),
            "enabled": self.enabled
        }


class ApiRequest:
    """Represents an API request to a service endpoint"""
    
    def __init__(self, connection_id: str, endpoint_id: str, 
                params: Dict[str, Any] = None, data: Dict[str, Any] = None,
                headers: Dict[str, str] = None):
        self.id = str(uuid.uuid4())
        self.connection_id = connection_id
        self.endpoint_id = endpoint_id
        self.params = params or {}
        self.data = data or {}
        self.headers = headers or {}
        self.created_at = datetime.datetime.utcnow()
        self.response = None
        self.status_code = None
        self.execution_time = None
        self.error = None
        
    def set_response(self, response: Any, status_code: int, 
                   execution_time: float) -> None:
        """Set the response from the API request"""
        self.response = response
        self.status_code = status_code
        self.execution_time = execution_time
        
    def set_error(self, error: str) -> None:
        """Set error information"""
        self.error = error
        
    def is_successful(self) -> bool:
        """Check if the request was successful"""
        return self.status_code is not None and 200 <= self.status_code < 300
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "connection_id": self.connection_id,
            "endpoint_id": self.endpoint_id,
            "params": self.params,
            "data": self._sanitize_data(self.data),
            "headers": self._sanitize_headers(self.headers),
            "created_at": self.created_at.isoformat(),
            "status_code": self.status_code,
            "execution_time": self.execution_time,
            "error": self.error,
            "success": self.is_successful()
        }
        
    def _sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive information from request data"""
        if not data:
            return {}
            
        sanitized = {}
        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in ['key', 'token', 'password', 'secret']):
                sanitized[key] = "********"
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_data(value)
            else:
                sanitized[key] = value
                
        return sanitized
        
    def _sanitize_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Remove sensitive information from headers"""
        if not headers:
            return {}
            
        sanitized = {}
        for key, value in headers.items():
            if any(sensitive in key.lower() for sensitive in ['authorization', 'api-key', 'token', 'secret']):
                sanitized[key] = "********"
            else:
                sanitized[key] = value
                
        return sanitized


class ClientServerManager:
    """Main class for managing client-server relationships"""
    
    def __init__(self):
        self.service_definitions: Dict[str, ServiceDefinition] = {}
        self.service_credentials: Dict[str, ServiceCredentials] = {}
        self.service_connections: Dict[str, ServiceConnection] = {}
        self.data_sync_configs: Dict[str, DataSyncConfig] = {}
        self.sync_thread = None
        self.sync_thread_running = False
        self.connection_pool = {}
        self.request_history: List[ApiRequest] = []
        self.max_request_history = 1000
        
    def create_service_definition(self, name: str, base_url: str, 
                                description: str = "") -> str:
        """Create a new service definition"""
        service = ServiceDefinition(name, base_url, description)
        
        if not service.validate_url():
            logger.error(f"Invalid base URL format: {base_url}")
            raise ValueError(f"Invalid base URL format: {base_url}")
            
        self.service_definitions[service.id] = service
        
        logger.info(f"Created service definition: {name} ({service.id})")
        return service.id
        
    def get_service_definition(self, service_id: str) -> Optional[ServiceDefinition]:
        """Get a service definition by ID"""
        return self.service_definitions.get(service_id)
        
    def create_endpoint(self, service_id: str, name: str, url_path: str, 
                      endpoint_type: EndpointType, method: str = "GET",
                      headers: Dict[str, str] = None,
                      params: Dict[str, Any] = None) -> Optional[str]:
        """Create a new endpoint for a service"""
        service = self.get_service_definition(service_id)
        if not service:
            logger.warning(f"Service definition not found: {service_id}")
            return None
            
        # Combine base URL with path
        url = service.base_url
        if not url.endswith('/') and not url_path.startswith('/'):
            url += '/'
        url += url_path.lstrip('/')
        
        # Combine service default headers with endpoint headers
        combined_headers = {}
        combined_headers.update(service.default_headers)
        if headers:
            combined_headers.update(headers)
            
        endpoint = ServiceEndpoint(name, url, endpoint_type, method, combined_headers, params)
        endpoint_id = service.add_endpoint(endpoint)
        
        logger.info(f"Created endpoint: {name} ({endpoint_id}) for service {service.name}")
        return endpoint_id
        
    def get_endpoint(self, service_id: str, endpoint_id: str) -> Optional[ServiceEndpoint]:
        """Get an endpoint by ID"""
        service = self.get_service_definition(service_id)
        if not service:
            return None
            
        return service.endpoints.get(endpoint_id)
        
    def create_credentials(self, auth_type: AuthType, 
                         credentials: Dict[str, Any] = None) -> str:
        """Create service credentials"""
        creds = ServiceCredentials(auth_type, credentials)
        self.service_credentials[creds.id] = creds
        
        logger.info(f"Created service credentials: ({creds.id})")
        return creds.id
        
    def get_credentials(self, credentials_id: str) -> Optional[ServiceCredentials]:
        """Get credentials by ID"""
        return self.service_credentials.get(credentials_id)
        
    def create_service_connection(self, service_id: str, 
                                credentials_id: Optional[str] = None) -> Optional[str]:
        """Create a service connection"""
        if service_id not in self.service_definitions:
            logger.warning(f"Service definition not found: {service_id}")
            return None
            
        # Validate credentials if needed
        service = self.service_definitions[service_id]
        if service.required_auth_type != AuthType.NONE:
            if not credentials_id:
                logger.warning(f"Credentials required for service {service.name}")
                return None
                
            credentials = self.get_credentials(credentials_id)
            if not credentials:
                logger.warning(f"Credentials not found: {credentials_id}")
                return None
                
            if credentials.auth_type != service.required_auth_type:
                logger.warning(f"Invalid auth type: {credentials.auth_type.value}, "
                             f"required: {service.required_auth_type.value}")
                return None
                
            if not credentials.validate():
                logger.warning(f"Invalid credentials: {credentials_id}")
                return None
                
        connection = ServiceConnection(service_id, credentials_id)
        self.service_connections[connection.id] = connection
        
        logger.info(f"Created service connection: ({connection.id}) for service {service.name}")
        return connection.id
        
    def get_connection(self, connection_id: str) -> Optional[ServiceConnection]:
        """Get a connection by ID"""
        return self.service_connections.get(connection_id)
        
    def test_connection(self, connection_id: str) -> Tuple[bool, Optional[str]]:
        """Test a service connection"""
        connection = self.get_connection(connection_id)
        if not connection:
            return False, "Connection not found"
            
        service = self.get_service_definition(connection.service_definition_id)
        if not service:
            return False, "Service definition not found"
            
        # Update status
        connection.update_status(ConnectionStatus.CONNECTING)
        
        try:
            # Simple test to check if service is accessible
            domain = urlparse(service.base_url).netloc
            r = requests.get(f"{service.base_url}", timeout=10)
            
            if r.status_code >= 400:
                connection.update_status(ConnectionStatus.ERROR, 
                                      f"HTTP error: {r.status_code}")
                return False, f"HTTP error: {r.status_code}"
                
            connection.update_status(ConnectionStatus.CONNECTED)
            return True, None
            
        except requests.exceptions.RequestException as e:
            error_message = f"Connection error: {str(e)}"
            connection.update_status(ConnectionStatus.ERROR, error_message)
            return False, error_message
            
    def create_data_sync_config(self, name: str, connection_id: str, 
                              endpoint_id: str, target_store: str,
                              sync_type: SyncType) -> Optional[str]:
        """Create a data synchronization configuration"""
        connection = self.get_connection(connection_id)
        if not connection:
            logger.warning(f"Connection not found: {connection_id}")
            return None
            
        service = self.get_service_definition(connection.service_definition_id)
        if not service:
            logger.warning(f"Service definition not found")
            return None
            
        if endpoint_id not in service.endpoints:
            logger.warning(f"Endpoint not found: {endpoint_id}")
            return None
            
        sync_config = DataSyncConfig(name, endpoint_id, target_store, sync_type)
        self.data_sync_configs[sync_config.id] = sync_config
        
        logger.info(f"Created data sync config: {name} ({sync_config.id})")
        return sync_config.id
        
    def get_sync_config(self, sync_id: str) -> Optional[DataSyncConfig]:
        """Get a sync configuration by ID"""
        return self.data_sync_configs.get(sync_id)
        
    def start_sync_process(self, interval_seconds: int = 60) -> None:
        """Start a background thread to handle data synchronization"""
        if self.sync_thread_running:
            logger.warning("Sync process is already running")
            return
            
        self.sync_thread_running = True
        
        def sync_process():
            while self.sync_thread_running:
                try:
                    self.check_and_execute_syncs()
                    time.sleep(interval_seconds)
                except Exception as e:
                    logger.error(f"Error in sync process: {str(e)}")
                    
        self.sync_thread = threading.Thread(target=sync_process)
        self.sync_thread.daemon = True
        self.sync_thread.start()
        
        logger.info(f"Started sync process with interval: {interval_seconds} seconds")
        
    def stop_sync_process(self) -> None:
        """Stop the sync process thread"""
        self.sync_thread_running = False
        if self.sync_thread:
            self.sync_thread.join(timeout=1.0)
            self.sync_thread = None
            
        logger.info("Stopped sync process")
        
    def check_and_execute_syncs(self) -> List[str]:
        """Check for due syncs and execute them"""
        executed_syncs = []
        
        for sync_id, sync_config in self.data_sync_configs.items():
            if not sync_config.enabled:
                continue
                
            if not sync_config.is_sync_due():
                continue
                
            success = self.execute_sync(sync_id)
            if success:
                executed_syncs.append(sync_id)
                
        return executed_syncs
        
    def execute_sync(self, sync_id: str) -> bool:
        """Execute a data synchronization"""
        sync_config = self.get_sync_config(sync_id)
        if not sync_config:
            logger.warning(f"Sync config not found: {sync_id}")
            return False
            
        # Find the connection for this endpoint
        endpoint_id = sync_config.source_endpoint_id
        connection = None
        
        for conn_id, conn in self.service_connections.items():
            service = self.get_service_definition(conn.service_definition_id)
            if service and endpoint_id in service.endpoints:
                connection = conn
                break
                
        if not connection:
            logger.warning(f"No connection found for endpoint: {endpoint_id}")
            return False
            
        # Execute the API request
        service = self.get_service_definition(connection.service_definition_id)
        endpoint = service.endpoints[endpoint_id]
        
        # Apply filters to params
        params = endpoint.params.copy()
        for field, conditions in sync_config.filters.items():
            for condition in conditions:
                param_name = field
                param_value = condition["value"]
                
                # Handle different operators by transforming to API-specific format
                # This is a simplified example; real implementation would depend on API
                operator = condition["operator"]
                if operator == "eq":
                    params[param_name] = param_value
                elif operator == "gt":
                    params[f"{param_name}_gt"] = param_value
                elif operator == "lt":
                    params[f"{param_name}_lt"] = param_value
                elif operator == "contains":
                    params[f"{param_name}_contains"] = param_value
                    
        # Execute request
        request = ApiRequest(connection.id, endpoint_id, params)
        executed_request = self.execute_request(request)
        
        if not executed_request.is_successful():
            logger.warning(f"Sync request failed: {executed_request.error}")
            return False
            
        # Process and store the result
        try:
            # Apply field mappings and transforms
            processed_data = self._process_sync_data(executed_request.response, sync_config)
            
            # Store the data (in a real implementation, this would use appropriate storage)
            self._store_sync_data(processed_data, sync_config.target_store)
            
            # Update last sync time
            sync_config.update_last_sync()
            
            logger.info(f"Successfully executed sync: {sync_config.name} ({sync_id})")
            return True
            
        except Exception as e:
            logger.error(f"Error processing sync data: {str(e)}")
            return False
            
    def _process_sync_data(self, data: Any, sync_config: DataSyncConfig) -> Any:
        """Process data according to field mappings and transformations"""
        if not data:
            return data
            
        # Handle list of items
        if isinstance(data, list):
            return [self._process_sync_data(item, sync_config) for item in data]
            
        # Handle single item
        if isinstance(data, dict):
            result = {}
            
            for src_field, tgt_field in sync_config.field_mappings.items():
                # Extract value using dot notation (e.g., "user.name")
                value = self._get_nested_value(data, src_field)
                
                if value is not None:
                    # Apply transformation if exists
                    if src_field in sync_config.transform_scripts:
                        try:
                            # In a real implementation, this would execute the transformation
                            # safely (e.g., using a sandboxed environment)
                            # For demo purposes, we'll just pass the value through
                            transformed_value = value
                        except Exception as e:
                            logger.error(f"Error in transform script for {src_field}: {str(e)}")
                            transformed_value = value
                    else:
                        transformed_value = value
                        
                    # Set in result using dot notation
                    self._set_nested_value(result, tgt_field, transformed_value)
                    
            return result
            
        return data
        
    def _get_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """Get a value from a nested dictionary using dot notation"""
        parts = path.split('.')
        current = data
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
                
        return current
        
    def _set_nested_value(self, data: Dict[str, Any], path: str, value: Any) -> None:
        """Set a value in a nested dictionary using dot notation"""
        parts = path.split('.')
        current = data
        
        # Navigate to the right level
        for i, part in enumerate(parts[:-1]):
            if part not in current:
                current[part] = {}
            current = current[part]
            
        # Set the value
        current[parts[-1]] = value
        
    def _store_sync_data(self, data: Any, target_store: str) -> None:
        """Store synchronized data in the target location"""
        # In a real implementation, this would store the data in the appropriate place
        # (e.g., database, file, cache)
        logger.info(f"Storing data in {target_store}: {len(str(data))} bytes")
        
        # For demo purposes, we'll just log it
        if isinstance(data, list):
            logger.info(f"Stored {len(data)} items in {target_store}")
        else:
            logger.info(f"Stored item in {target_store}")
            
    def execute_request(self, request: ApiRequest) -> ApiRequest:
        """Execute an API request"""
        connection = self.get_connection(request.connection_id)
        if not connection:
            request.set_error("Connection not found")
            return request
            
        service = self.get_service_definition(connection.service_definition_id)
        if not service:
            request.set_error("Service definition not found")
            return request
            
        endpoint = service.endpoints.get(request.endpoint_id)
        if not endpoint:
            request.set_error("Endpoint not found")
            return request
            
        # Combine endpoint headers with request headers
        headers = {}
        headers.update(endpoint.headers)
        if request.headers:
            headers.update(request.headers)
            
        # Add authentication if needed
        if connection.credentials_id:
            credentials = self.get_credentials(connection.credentials_id)
            if credentials and credentials.validate():
                self._apply_auth_to_headers(headers, credentials)
                
        # Execute the request
        try:
            start_time = time.time()
            
            # Choose request method based on endpoint definition
            method = endpoint.method.upper()
            url = endpoint.url
            
            if endpoint.endpoint_type == EndpointType.REST:
                if method == "GET":
                    response = requests.get(
                        url, 
                        headers=headers, 
                        params=request.params, 
                        timeout=endpoint.timeout
                    )
                elif method == "POST":
                    response = requests.post(
                        url, 
                        headers=headers, 
                        params=request.params, 
                        json=request.data, 
                        timeout=endpoint.timeout
                    )
                elif method == "PUT":
                    response = requests.put(
                        url, 
                        headers=headers, 
                        params=request.params, 
                        json=request.data, 
                        timeout=endpoint.timeout
                    )
                elif method == "DELETE":
                    response = requests.delete(
                        url, 
                        headers=headers, 
                        params=request.params, 
                        timeout=endpoint.timeout
                    )
                elif method == "PATCH":
                    response = requests.patch(
                        url, 
                        headers=headers, 
                        params=request.params, 
                        json=request.data, 
                        timeout=endpoint.timeout
                    )
                else:
                    request.set_error(f"Unsupported method: {method}")
                    return request
                    
                execution_time = time.time() - start_time
                
                try:
                    # Try to parse JSON response
                    response_data = response.json()
                except:
                    # Fall back to text response
                    response_data = response.text
                    
                request.set_response(response_data, response.status_code, execution_time)
                
                # Log the request
                connection.log_request(
                    request.endpoint_id,
                    request.data,
                    response_data,
                    response.status_code,
                    execution_time
                )
                
                # Check for rate limiting
                if 429 == response.status_code:
                    connection.update_status(ConnectionStatus.RATE_LIMITED)
                elif response.status_code >= 400:
                    connection.update_status(
                        ConnectionStatus.ERROR, 
                        f"HTTP error: {response.status_code}"
                    )
                else:
                    connection.update_status(ConnectionStatus.CONNECTED)
                    
            elif endpoint.endpoint_type == EndpointType.GRAPHQL:
                # Simplified GraphQL handling
                if not request.data.get('query'):
                    request.set_error("Missing 'query' for GraphQL request")
                    return request
                    
                response = requests.post(
                    url,
                    headers=headers,
                    json=request.data,
                    timeout=endpoint.timeout
                )
                
                execution_time = time.time() - start_time
                
                try:
                    response_data = response.json()
                except:
                    response_data = response.text
                    
                request.set_response(response_data, response.status_code, execution_time)
                
                # Log the request
                connection.log_request(
                    request.endpoint_id,
                    request.data,
                    response_data,
                    response.status_code,
                    execution_time
                )
                
            else:
                request.set_error(f"Unsupported endpoint type: {endpoint.endpoint_type.value}")
                
            # Add to request history
            self.request_history.append(request)
            while len(self.request_history) > self.max_request_history:
                self.request_history.pop(0)
                
            return request
            
        except Exception as e:
            error_message = f"Request error: {str(e)}"
            request.set_error(error_message)
            connection.update_status(ConnectionStatus.ERROR, error_message)
            return request
            
    def _apply_auth_to_headers(self, headers: Dict[str, str], 
                             credentials: ServiceCredentials) -> None:
        """Apply authentication to headers based on auth type"""
        if credentials.auth_type == AuthType.API_KEY:
            key_name = credentials.credentials.get("key_name", "X-API-Key")
            key_value = credentials.credentials.get("key_value", "")
            headers[key_name] = key_value
            
        elif credentials.auth_type == AuthType.BASIC:
            username = credentials.credentials.get("username", "")
            password = credentials.credentials.get("password", "")
            auth_string = f"{username}:{password}"
            encoded = base64.b64encode(auth_string.encode()).decode()
            headers["Authorization"] = f"Basic {encoded}"
            
        elif credentials.auth_type == AuthType.BEARER:
            token = credentials.credentials.get("token", "")
            headers["Authorization"] = f"Bearer {token}"
            
        elif credentials.auth_type == AuthType.JWT:
            token = credentials.credentials.get("token", "")
            headers["Authorization"] = f"Bearer {token}"
            
        elif credentials.auth_type == AuthType.OAUTH:
            token = credentials.credentials.get("access_token", "")
            headers["Authorization"] = f"Bearer {token}"
            
    def get_request_history(self, connection_id: Optional[str] = None,
                          limit: int = 100) -> List[Dict[str, Any]]:
        """Get request history, optionally filtered by connection"""
        if connection_id:
            filtered = [
                req.to_dict() for req in self.request_history
                if req.connection_id == connection_id
            ]
            return filtered[-limit:]
        else:
            return [req.to_dict() for req in self.request_history[-limit:]]
            
    def get_sync_status(self) -> Dict[str, Any]:
        """Get status of all data synchronization configs"""
        results = []
        
        for sync_id, sync_config in self.data_sync_configs.items():
            results.append({
                "id": sync_id,
                "name": sync_config.name,
                "enabled": sync_config.enabled,
                "last_sync": sync_config.last_sync.isoformat() if sync_config.last_sync else None,
                "next_sync": (
                    (sync_config.last_sync + datetime.timedelta(minutes=sync_config.sync_interval_minutes)).isoformat()
                    if sync_config.last_sync else datetime.datetime.utcnow().isoformat()
                ),
                "sync_interval_minutes": sync_config.sync_interval_minutes,
                "target_store": sync_config.target_store
            })
            
        return {
            "syncs": results,
            "sync_process_running": self.sync_thread_running,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }


# Example usage
if __name__ == "__main__":
    # Create client-server manager
    manager = ClientServerManager()
    
    # Create a service definition
    service_id = manager.create_service_definition(
        "Weather API",
        "https://api.weatherapi.com/v1",
        "Weather data service"
    )
    print(f"Created service: {service_id}")
    
    # Set required auth type
    service = manager.get_service_definition(service_id)
    service.set_required_auth_type(AuthType.API_KEY)
    
    # Create an endpoint
    endpoint_id = manager.create_endpoint(
        service_id,
        "Current Weather",
        "/current.json",
        EndpointType.REST,
        "GET"
    )
    print(f"Created endpoint: {endpoint_id}")
    
    # Create credentials
    # In a real application, this would be obtained securely
    credentials_id = manager.create_credentials(
        AuthType.API_KEY,
        {
            "key_name": "key",
            "key_value": "your_api_key_here"
        }
    )
    print(f"Created credentials: {credentials_id}")
    
    # Create a connection
    connection_id = manager.create_service_connection(service_id, credentials_id)
    print(f"Created connection: {connection_id}")
    
    # Create a data sync configuration
    sync_id = manager.create_data_sync_config(
        "Hourly Weather Updates",
        connection_id,
        endpoint_id,
        "weather_data",
        SyncType.PULL
    )
    print(f"Created sync config: {sync_id}")
    
    # Add field mappings
    sync_config = manager.get_sync_config(sync_id)
    sync_config.add_field_mapping("current.temp_c", "temperature.celsius")
    sync_config.add_field_mapping("current.temp_f", "temperature.fahrenheit")
    sync_config.add_field_mapping("current.condition.text", "condition")
    
    # Add filter
    sync_config.add_filter("q", "eq", "London")
    
    # Set sync interval
    sync_config.set_sync_interval(60)  # Every hour
    
    # Start sync process
    # manager.start_sync_process(300)  # Check every 5 minutes
    
    # Manual execution
    print("\nExecuting API request:")
    request = ApiRequest(
        connection_id,
        endpoint_id,
        {"q": "London"}
    )
    
    # Note: This would fail without a valid API key
    print("In a real application, this would execute the request with a valid API key")
    
    # Get sync status
    sync_status = manager.get_sync_status()
    print(f"\nSync status: {len(sync_status['syncs'])} configs")
    for sync in sync_status["syncs"]:
        print(f"- {sync['name']}: {'Enabled' if sync['enabled'] else 'Disabled'}")
        print(f"  Last sync: {sync['last_sync'] or 'Never'}")
        print(f"  Interval: {sync['sync_interval_minutes']} minutes")