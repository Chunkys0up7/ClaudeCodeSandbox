#!/usr/bin/env python3
"""
Workflow Engine for the AI App Store

This module provides functionality for creating, managing, and executing
workflows that chain together multiple AI applications.
"""
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkflowStep:
    """Represents a single step in a workflow"""
    
    def __init__(self, 
                 name: str, 
                 component_id: str, 
                 action: str, 
                 input_mapping: Dict[str, str] = None,
                 output_mapping: Dict[str, str] = None):
        """
        Initialize a workflow step
        
        Args:
            name: Human-readable name for the step
            component_id: ID of the component/app to execute
            action: Action to perform on the component
            input_mapping: Maps workflow inputs to component inputs
            output_mapping: Maps component outputs to workflow outputs
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.component_id = component_id
        self.action = action
        self.input_mapping = input_mapping or {}
        self.output_mapping = output_mapping or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "name": self.name,
            "component_id": self.component_id,
            "action": self.action,
            "input_mapping": self.input_mapping,
            "output_mapping": self.output_mapping
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkflowStep':
        """Create from dictionary representation"""
        step = cls(
            name=data["name"],
            component_id=data["component_id"],
            action=data["action"],
            input_mapping=data.get("input_mapping", {}),
            output_mapping=data.get("output_mapping", {})
        )
        step.id = data["id"]
        return step
        

class Workflow:
    """Represents a workflow that chains together multiple applications"""
    
    def __init__(self, name: str, description: str = ""):
        """
        Initialize a workflow
        
        Args:
            name: Name of the workflow
            description: Optional description
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.steps: List[WorkflowStep] = []
        self.created_at = datetime.utcnow()
        self.updated_at = self.created_at
        self.status = "draft"
        
    def add_step(self, step: WorkflowStep) -> None:
        """Add a step to the workflow"""
        self.steps.append(step)
        self.updated_at = datetime.utcnow()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "steps": [step.to_dict() for step in self.steps],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "status": self.status
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Workflow':
        """Create from dictionary representation"""
        workflow = cls(
            name=data["name"],
            description=data.get("description", "")
        )
        workflow.id = data["id"]
        workflow.status = data.get("status", "draft")
        workflow.created_at = datetime.fromisoformat(data["created_at"])
        workflow.updated_at = datetime.fromisoformat(data["updated_at"])
        workflow.steps = [WorkflowStep.from_dict(step) for step in data["steps"]]
        return workflow
    
    def save(self, filepath: str) -> None:
        """Save workflow to file"""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, filepath: str) -> 'Workflow':
        """Load workflow from file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)


class WorkflowExecution:
    """Represents a single execution of a workflow"""
    
    def __init__(self, workflow: Workflow):
        """
        Initialize a workflow execution
        
        Args:
            workflow: The workflow to execute
        """
        self.id = str(uuid.uuid4())
        self.workflow_id = workflow.id
        self.workflow = workflow
        self.started_at = datetime.utcnow()
        self.completed_at = None
        self.status = "running"
        self.results = {}
        self.errors = []
        
    def complete(self, success: bool) -> None:
        """Mark the execution as complete"""
        self.completed_at = datetime.utcnow()
        self.status = "completed" if success else "failed"
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "workflow_id": self.workflow_id,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "status": self.status,
            "results": self.results,
            "errors": self.errors
        }


class WorkflowEngine:
    """Engine for executing workflows"""
    
    def __init__(self):
        """Initialize the workflow engine"""
        self.workflows: Dict[str, Workflow] = {}
        self.executions: Dict[str, WorkflowExecution] = {}
        self.component_registry: Dict[str, Dict[str, Callable]] = {}
        
    def register_workflow(self, workflow: Workflow) -> str:
        """Register a workflow with the engine"""
        self.workflows[workflow.id] = workflow
        logger.info(f"Registered workflow: {workflow.id} - {workflow.name}")
        return workflow.id
    
    def register_component(self, 
                          component_id: str, 
                          actions: Dict[str, Callable]) -> None:
        """
        Register a component with available actions
        
        Args:
            component_id: ID of the component
            actions: Dictionary of action names to functions
        """
        self.component_registry[component_id] = actions
        logger.info(f"Registered component: {component_id} with actions: {list(actions.keys())}")
    
    def execute_workflow(self, 
                        workflow_id: str, 
                        inputs: Dict[str, Any]) -> WorkflowExecution:
        """
        Execute a workflow with the given inputs
        
        Args:
            workflow_id: ID of the workflow to execute
            inputs: Input data for the workflow
            
        Returns:
            The workflow execution object
        """
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow not found: {workflow_id}")
            
        workflow = self.workflows[workflow_id]
        execution = WorkflowExecution(workflow)
        self.executions[execution.id] = execution
        
        logger.info(f"Starting workflow execution: {execution.id} for workflow: {workflow_id}")
        
        try:
            # Execute each step in sequence
            step_results = {}
            for i, step in enumerate(workflow.steps):
                logger.info(f"Executing step {i+1}/{len(workflow.steps)}: {step.name}")
                
                # If component not registered, skip with error
                if step.component_id not in self.component_registry:
                    error_msg = f"Component not registered: {step.component_id}"
                    execution.errors.append({
                        "step": step.id,
                        "error": error_msg
                    })
                    logger.error(error_msg)
                    continue
                    
                component = self.component_registry[step.component_id]
                
                # If action not registered, skip with error
                if step.action not in component:
                    error_msg = f"Action not found: {step.action} for component: {step.component_id}"
                    execution.errors.append({
                        "step": step.id,
                        "error": error_msg
                    })
                    logger.error(error_msg)
                    continue
                
                # Map inputs
                step_inputs = {}
                for target, source in step.input_mapping.items():
                    if source.startswith("$.inputs."):
                        input_key = source[len("$.inputs."):]
                        if input_key in inputs:
                            step_inputs[target] = inputs[input_key]
                    elif source.startswith("$.steps."):
                        parts = source.split(".")
                        if len(parts) >= 3:
                            source_step_id = parts[2]
                            output_key = ".".join(parts[3:])
                            if (source_step_id in step_results and 
                                output_key in step_results[source_step_id]):
                                step_inputs[target] = step_results[source_step_id][output_key]
                
                # Execute action
                try:
                    action_func = component[step.action]
                    result = action_func(**step_inputs)
                    step_results[step.id] = result
                    
                    # Map outputs to workflow results
                    for target, source in step.output_mapping.items():
                        if source in result:
                            execution.results[target] = result[source]
                            
                except Exception as e:
                    error_msg = f"Error executing step {step.id}: {str(e)}"
                    execution.errors.append({
                        "step": step.id,
                        "error": error_msg
                    })
                    logger.error(error_msg, exc_info=True)
            
            # Mark execution as complete
            success = len(execution.errors) == 0
            execution.complete(success)
            
        except Exception as e:
            logger.error(f"Error executing workflow: {str(e)}", exc_info=True)
            execution.errors.append({
                "workflow": workflow_id,
                "error": str(e)
            })
            execution.complete(False)
            
        return execution
    
    def get_execution_status(self, execution_id: str) -> Dict[str, Any]:
        """Get the status of a workflow execution"""
        if execution_id not in self.executions:
            raise ValueError(f"Execution not found: {execution_id}")
            
        execution = self.executions[execution_id]
        return execution.to_dict()


# Example usage
if __name__ == "__main__":
    # Create a simple workflow
    workflow = Workflow("Example Workflow", "A simple example workflow")
    
    # Add steps
    step1 = WorkflowStep(
        name="Parse Input",
        component_id="data_processor",
        action="parse_json",
        input_mapping={"json_data": "$.inputs.data"},
        output_mapping={"parsed_data": "result"}
    )
    workflow.add_step(step1)
    
    step2 = WorkflowStep(
        name="Analyze Data",
        component_id="ai_analyzer",
        action="analyze",
        input_mapping={"data": "$.steps." + step1.id + ".result"},
        output_mapping={"analysis_result": "analysis"}
    )
    workflow.add_step(step2)
    
    # Print workflow definition
    print(json.dumps(workflow.to_dict(), indent=2))