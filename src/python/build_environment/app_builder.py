#!/usr/bin/env python3
"""
App Builder Module for the AI App Store Build Environment

This module provides functionality for building and testing AI applications
using the flexible build environment.
"""

import uuid
import logging
import datetime
import json
from typing import Dict, List, Any, Optional, Callable

from .model_configuration import ModelConfiguration, ModelConfigurationManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BuildingBlock:
    """Represents a predefined building block for app development"""
    
    def __init__(self, name: str, block_type: str, description: str):
        self.id = str(uuid.uuid4())
        self.name = name
        self.block_type = block_type
        self.description = description
        self.parameters = {}
        self.code_template = ""
        self.created_at = datetime.datetime.utcnow()
        
    def set_parameter(self, key: str, value: Any) -> None:
        """Set a parameter for the building block"""
        self.parameters[key] = value
        
    def set_code_template(self, code_template: str) -> None:
        """Set the code template for the building block"""
        self.code_template = code_template
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "name": self.name,
            "block_type": self.block_type,
            "description": self.description,
            "parameters": self.parameters,
            "code_template": self.code_template,
            "created_at": self.created_at.isoformat()
        }


class AppComponent:
    """Represents a component in an AI app"""
    
    def __init__(self, name: str, component_type: str):
        self.id = str(uuid.uuid4())
        self.name = name
        self.component_type = component_type
        self.configuration = {}
        self.building_blocks = []  # List of block IDs
        self.custom_code = ""
        self.created_at = datetime.datetime.utcnow()
        self.updated_at = self.created_at
        
    def set_configuration(self, config: Dict[str, Any]) -> None:
        """Set the component configuration"""
        self.configuration = config
        self.updated_at = datetime.datetime.utcnow()
        
    def add_building_block(self, block_id: str) -> None:
        """Add a building block to the component"""
        self.building_blocks.append(block_id)
        self.updated_at = datetime.datetime.utcnow()
        
    def set_custom_code(self, code: str) -> None:
        """Set custom code for the component"""
        self.custom_code = code
        self.updated_at = datetime.datetime.utcnow()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "name": self.name,
            "component_type": self.component_type,
            "configuration": self.configuration,
            "building_blocks": self.building_blocks,
            "custom_code": self.custom_code,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class AppBuild:
    """Represents a build of an AI app"""
    
    def __init__(self, app_id: str, version: str, builder_id: str):
        self.id = str(uuid.uuid4())
        self.app_id = app_id
        self.version = version
        self.builder_id = builder_id
        self.components = {}  # Dict[component_id, AppComponent]
        self.model_configurations = {}  # Dict[config_id, configuration_id]
        self.status = "draft"  # draft, building, success, failed
        self.errors = []
        self.created_at = datetime.datetime.utcnow()
        self.updated_at = self.created_at
        self.build_completed_at = None
        
    def add_component(self, component: AppComponent) -> str:
        """Add a component to the build"""
        self.components[component.id] = component
        self.updated_at = datetime.datetime.utcnow()
        return component.id
        
    def add_model_configuration(self, component_id: str, config_id: str) -> None:
        """Add a model configuration to the build"""
        self.model_configurations[component_id] = config_id
        self.updated_at = datetime.datetime.utcnow()
        
    def start_build(self) -> None:
        """Start the build process"""
        self.status = "building"
        self.updated_at = datetime.datetime.utcnow()
        
    def complete_build(self, success: bool, errors: List[str] = None) -> None:
        """Mark the build as complete"""
        self.status = "success" if success else "failed"
        self.errors = errors or []
        self.build_completed_at = datetime.datetime.utcnow()
        self.updated_at = self.build_completed_at
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "app_id": self.app_id,
            "version": self.version,
            "builder_id": self.builder_id,
            "components": {cid: comp.to_dict() for cid, comp in self.components.items()},
            "model_configurations": self.model_configurations,
            "status": self.status,
            "errors": self.errors,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "build_completed_at": self.build_completed_at.isoformat() if self.build_completed_at else None
        }


class TestResult:
    """Represents the result of testing an AI app"""
    
    def __init__(self, build_id: str, tester_id: str):
        self.id = str(uuid.uuid4())
        self.build_id = build_id
        self.tester_id = tester_id
        self.test_cases = []
        self.overall_result = None  # None, success, failed
        self.started_at = datetime.datetime.utcnow()
        self.completed_at = None
        
    def add_test_case(self, name: str, inputs: Dict[str, Any], expected_outputs: Dict[str, Any]) -> None:
        """Add a test case"""
        self.test_cases.append({
            "name": name,
            "inputs": inputs,
            "expected_outputs": expected_outputs,
            "actual_outputs": None,
            "result": None,  # None, success, failed
            "errors": []
        })
        
    def update_test_case(self, index: int, actual_outputs: Dict[str, Any], 
                         result: str, errors: List[str] = None) -> None:
        """Update a test case with results"""
        if index >= len(self.test_cases):
            raise ValueError(f"Test case index {index} out of range")
            
        test_case = self.test_cases[index]
        test_case["actual_outputs"] = actual_outputs
        test_case["result"] = result
        test_case["errors"] = errors or []
        
    def complete_testing(self) -> None:
        """Mark testing as complete"""
        self.completed_at = datetime.datetime.utcnow()
        
        # Determine overall result
        if all(tc["result"] == "success" for tc in self.test_cases):
            self.overall_result = "success"
        else:
            self.overall_result = "failed"
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "build_id": self.build_id,
            "tester_id": self.tester_id,
            "test_cases": self.test_cases,
            "overall_result": self.overall_result,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


class BuildEnvironmentManager:
    """Main class for managing the app build environment"""
    
    def __init__(self, model_config_manager: ModelConfigurationManager):
        self.building_blocks: Dict[str, BuildingBlock] = {}
        self.builds: Dict[str, AppBuild] = {}
        self.test_results: Dict[str, TestResult] = {}
        self.model_config_manager = model_config_manager
        
        # Register default building blocks
        self._register_default_building_blocks()
        
    def _register_default_building_blocks(self) -> None:
        """Register default building blocks"""
        # Email sending block
        email_block = BuildingBlock(
            "Email Sender", 
            "integration",
            "Send an email notification"
        )
        email_block.set_parameter("to", "recipient@example.com")
        email_block.set_parameter("subject", "Notification from AI App")
        email_block.set_parameter("body", "This is an automated notification.")
        email_block.set_code_template("""
def send_email(to, subject, body):
    # In a real implementation, this would use an email library
    print(f"Sending email to {to}")
    print(f"Subject: {subject}")
    print(f"Body: {body}")
    return {"status": "sent"}
""")
        self.building_blocks[email_block.id] = email_block
        
        # Database query block
        db_block = BuildingBlock(
            "Database Query",
            "data",
            "Execute a database query"
        )
        db_block.set_parameter("query", "SELECT * FROM users WHERE status = 'active'")
        db_block.set_parameter("connection_string", "${DATABASE_CONNECTION}")
        db_block.set_code_template("""
def execute_query(query, connection_string):
    # In a real implementation, this would use a database library
    print(f"Executing query: {query}")
    print(f"Connection: {connection_string}")
    # Simulate query results
    return {"rows": [{"id": 1, "name": "User 1"}, {"id": 2, "name": "User 2"}]}
""")
        self.building_blocks[db_block.id] = db_block
        
        # Text processing block
        text_block = BuildingBlock(
            "Text Processor",
            "processing",
            "Process and analyze text"
        )
        text_block.set_parameter("text", "")
        text_block.set_parameter("operations", ["tokenize", "sentiment"])
        text_block.set_code_template("""
def process_text(text, operations):
    results = {}
    
    if "tokenize" in operations:
        # Simple tokenization by splitting on spaces
        results["tokens"] = text.split()
        
    if "sentiment" in operations:
        # Very simple sentiment analysis (not realistic)
        positive_words = ["good", "great", "excellent", "positive", "happy"]
        negative_words = ["bad", "terrible", "negative", "sad", "unhappy"]
        
        tokens = text.lower().split()
        positive_count = sum(1 for token in tokens if token in positive_words)
        negative_count = sum(1 for token in tokens if token in negative_words)
        
        if positive_count > negative_count:
            results["sentiment"] = "positive"
        elif negative_count > positive_count:
            results["sentiment"] = "negative"
        else:
            results["sentiment"] = "neutral"
    
    return results
""")
        self.building_blocks[text_block.id] = text_block
        
    def register_building_block(self, block: BuildingBlock) -> str:
        """Register a new building block"""
        self.building_blocks[block.id] = block
        return block.id
        
    def get_building_block(self, block_id: str) -> Optional[BuildingBlock]:
        """Get a building block by ID"""
        return self.building_blocks.get(block_id)
        
    def list_building_blocks(self, block_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """List building blocks, optionally filtered by type"""
        results = []
        
        for block in self.building_blocks.values():
            if block_type is None or block.block_type == block_type:
                results.append(block.to_dict())
                
        return results
        
    def create_app_build(self, app_id: str, version: str, builder_id: str) -> AppBuild:
        """Create a new app build"""
        build = AppBuild(app_id, version, builder_id)
        self.builds[build.id] = build
        return build
        
    def get_app_build(self, build_id: str) -> Optional[AppBuild]:
        """Get an app build by ID"""
        return self.builds.get(build_id)
        
    def list_app_builds(self, app_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List app builds, optionally filtered by app ID"""
        results = []
        
        for build in self.builds.values():
            if app_id is None or build.app_id == app_id:
                results.append(build.to_dict())
                
        return results
        
    def create_app_component(self, build_id: str, name: str, component_type: str) -> Optional[str]:
        """Create and add a component to an app build"""
        if build_id not in self.builds:
            return None
            
        build = self.builds[build_id]
        component = AppComponent(name, component_type)
        return build.add_component(component)
        
    def add_model_to_component(self, build_id: str, component_id: str, model_config_id: str) -> bool:
        """Add a model configuration to a component"""
        if build_id not in self.builds:
            return False
            
        build = self.builds[build_id]
        
        if component_id not in build.components:
            return False
            
        if self.model_config_manager.get_configuration(model_config_id) is None:
            return False
            
        build.add_model_configuration(component_id, model_config_id)
        return True
        
    def add_building_block_to_component(self, build_id: str, component_id: str, block_id: str) -> bool:
        """Add a building block to a component"""
        if build_id not in self.builds:
            return False
            
        build = self.builds[build_id]
        
        if component_id not in build.components:
            return False
            
        if block_id not in self.building_blocks:
            return False
            
        component = build.components[component_id]
        component.add_building_block(block_id)
        return True
        
    def set_component_custom_code(self, build_id: str, component_id: str, code: str) -> bool:
        """Set custom code for a component"""
        if build_id not in self.builds:
            return False
            
        build = self.builds[build_id]
        
        if component_id not in build.components:
            return False
            
        component = build.components[component_id]
        component.set_custom_code(code)
        return True
        
    def execute_build(self, build_id: str) -> bool:
        """Execute the build process for an app"""
        if build_id not in self.builds:
            return False
            
        build = self.builds[build_id]
        build.start_build()
        
        try:
            # This would be a more complex process in a real implementation
            # For now, just mark the build as successful
            build.complete_build(True)
            return True
            
        except Exception as e:
            logger.error(f"Build failed: {str(e)}")
            build.complete_build(False, [str(e)])
            return False
            
    def create_test_result(self, build_id: str, tester_id: str) -> Optional[TestResult]:
        """Create a new test result for an app build"""
        if build_id not in self.builds:
            return None
            
        test_result = TestResult(build_id, tester_id)
        self.test_results[test_result.id] = test_result
        return test_result
        
    def get_test_result(self, result_id: str) -> Optional[TestResult]:
        """Get a test result by ID"""
        return self.test_results.get(result_id)
        
    def list_test_results(self, build_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List test results, optionally filtered by build ID"""
        results = []
        
        for test_result in self.test_results.values():
            if build_id is None or test_result.build_id == build_id:
                results.append(test_result.to_dict())
                
        return results
        
    def add_test_case(self, result_id: str, name: str, 
                     inputs: Dict[str, Any], expected_outputs: Dict[str, Any]) -> bool:
        """Add a test case to a test result"""
        if result_id not in self.test_results:
            return False
            
        test_result = self.test_results[result_id]
        test_result.add_test_case(name, inputs, expected_outputs)
        return True
        
    def execute_test(self, result_id: str) -> bool:
        """Execute tests for an app build"""
        if result_id not in self.test_results:
            return False
            
        test_result = self.test_results[result_id]
        build = self.builds.get(test_result.build_id)
        
        if build is None:
            return False
            
        # In a real implementation, this would execute the app with the test inputs
        # For now, just simulate test execution
        for i, test_case in enumerate(test_result.test_cases):
            try:
                # Simulate test execution
                actual_outputs = test_case["expected_outputs"]  # In a real implementation, this would be the actual result
                result = "success"  # Assume success for this example
                test_result.update_test_case(i, actual_outputs, result)
                
            except Exception as e:
                logger.error(f"Test execution failed: {str(e)}")
                test_result.update_test_case(i, {}, "failed", [str(e)])
                
        test_result.complete_testing()
        return True


# Example usage
if __name__ == "__main__":
    # Create model configuration manager
    model_config_manager = ModelConfigurationManager()
    
    # Create build environment manager
    build_manager = BuildEnvironmentManager(model_config_manager)
    
    # List available building blocks
    blocks = build_manager.list_building_blocks()
    print(f"Found {len(blocks)} building blocks:")
    for block in blocks:
        print(f"- {block['name']} ({block['block_type']})")
    
    # Create a new app build
    app_id = "app-123"
    version = "1.0.0"
    builder_id = "user-456"
    
    build = build_manager.create_app_build(app_id, version, builder_id)
    print(f"Created app build: {build.id}")
    
    # Add a component to the build
    component_id = build_manager.create_app_component(build.id, "Text Analyzer", "processor")
    if component_id:
        print(f"Added component: {component_id}")
        
        # Add a model to the component
        model_configs = model_config_manager.list_configurations()
        if model_configs:
            model_config_id = model_configs[0]["id"]
            build_manager.add_model_to_component(build.id, component_id, model_config_id)
            print(f"Added model configuration: {model_config_id}")
            
        # Add a building block to the component
        text_blocks = build_manager.list_building_blocks(block_type="processing")
        if text_blocks:
            block_id = text_blocks[0]["id"]
            build_manager.add_building_block_to_component(build.id, component_id, block_id)
            print(f"Added building block: {block_id}")
            
        # Set custom code for the component
        custom_code = """
def analyze_text(input_text):
    # Call the text processor
    tokens = process_text(input_text, ["tokenize", "sentiment"])
    
    # Add additional analysis
    word_count = len(tokens["tokens"])
    
    return {
        "tokens": tokens["tokens"],
        "sentiment": tokens["sentiment"],
        "word_count": word_count
    }
"""
        build_manager.set_component_custom_code(build.id, component_id, custom_code)
        print("Added custom code to component")
    
    # Execute the build
    build_success = build_manager.execute_build(build.id)
    print(f"Build {'succeeded' if build_success else 'failed'}")
    
    # Create test result
    tester_id = "user-789"
    test_result = build_manager.create_test_result(build.id, tester_id)
    
    if test_result:
        # Add test cases
        build_manager.add_test_case(
            test_result.id,
            "Basic Text Analysis",
            {"input_text": "This is a good example of text analysis."},
            {"sentiment": "positive", "word_count": 8}
        )
        
        build_manager.add_test_case(
            test_result.id,
            "Negative Sentiment Analysis",
            {"input_text": "This is a terrible example of bad text analysis."},
            {"sentiment": "negative", "word_count": 9}
        )
        
        # Execute tests
        test_success = build_manager.execute_test(test_result.id)
        print(f"Tests {'succeeded' if test_success else 'failed'}")
        
        # Get test results
        result = build_manager.get_test_result(test_result.id)
        if result:
            print(f"Overall test result: {result.overall_result}")
            for i, tc in enumerate(result.test_cases):
                print(f"Test {i+1}: {tc['name']} - {tc['result']}")