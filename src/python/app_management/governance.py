#!/usr/bin/env python3
"""
App Governance Module for the AI App Store

This module implements the governance framework that manages the app lifecycle
from experimental to production, including validation, compliance, and approval.
"""

import enum
import uuid
import logging
import datetime
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AppStatus(enum.Enum):
    """Enum representing the possible statuses of an AI application"""
    DRAFT = "draft"
    EXPERIMENTAL = "experimental"
    VALIDATION = "validation"
    APPROVED = "approved"
    PRODUCTION = "production"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class ComplianceCheck:
    """Represents a compliance check that must be passed before an app can advance"""
    
    def __init__(self, name: str, description: str, check_type: str):
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.check_type = check_type  # e.g., "bias", "fairness", "security", "privacy"
        self.created_at = datetime.datetime.utcnow()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "check_type": self.check_type,
            "created_at": self.created_at.isoformat()
        }


class ComplianceResult:
    """Represents the result of a compliance check for a specific app version"""
    
    def __init__(self, app_id: str, version: str, check_id: str):
        self.id = str(uuid.uuid4())
        self.app_id = app_id
        self.version = version
        self.check_id = check_id
        self.status = "pending"  # pending, passed, failed
        self.details = {}
        self.created_at = datetime.datetime.utcnow()
        self.updated_at = self.created_at
        
    def update_result(self, status: str, details: Dict[str, Any]) -> None:
        """Update the compliance check result"""
        self.status = status
        self.details = details
        self.updated_at = datetime.datetime.utcnow()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "app_id": self.app_id,
            "version": self.version,
            "check_id": self.check_id,
            "status": self.status,
            "details": self.details,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class ApprovalWorkflow:
    """Represents an approval workflow for transitioning app status"""
    
    def __init__(self, app_id: str, from_status: AppStatus, to_status: AppStatus):
        self.id = str(uuid.uuid4())
        self.app_id = app_id
        self.from_status = from_status
        self.to_status = to_status
        self.steps = []  # List of approval steps
        self.current_step = 0
        self.status = "pending"  # pending, in_progress, completed, rejected
        self.created_at = datetime.datetime.utcnow()
        self.updated_at = self.created_at
        self.completed_at = None
        
    def add_step(self, approver_role: str, description: str) -> None:
        """Add an approval step to the workflow"""
        self.steps.append({
            "step_number": len(self.steps) + 1,
            "approver_role": approver_role,
            "description": description,
            "status": "pending",
            "approved_by": None,
            "approved_at": None,
            "comments": ""
        })
        self.updated_at = datetime.datetime.utcnow()
        
    def approve_current_step(self, user_id: str, comments: str = "") -> bool:
        """Approve the current step in the workflow"""
        if self.current_step >= len(self.steps):
            return False
            
        step = self.steps[self.current_step]
        step["status"] = "approved"
        step["approved_by"] = user_id
        step["approved_at"] = datetime.datetime.utcnow().isoformat()
        step["comments"] = comments
        
        self.current_step += 1
        self.status = "in_progress"
        
        # Check if this was the last step
        if self.current_step >= len(self.steps):
            self.status = "completed"
            self.completed_at = datetime.datetime.utcnow()
            
        self.updated_at = datetime.datetime.utcnow()
        return True
        
    def reject_current_step(self, user_id: str, comments: str) -> bool:
        """Reject the current step in the workflow"""
        if self.current_step >= len(self.steps):
            return False
            
        step = self.steps[self.current_step]
        step["status"] = "rejected"
        step["approved_by"] = user_id
        step["approved_at"] = datetime.datetime.utcnow().isoformat()
        step["comments"] = comments
        
        self.status = "rejected"
        self.completed_at = datetime.datetime.utcnow()
        self.updated_at = self.completed_at
        return True
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "app_id": self.app_id,
            "from_status": self.from_status.value,
            "to_status": self.to_status.value,
            "steps": self.steps,
            "current_step": self.current_step,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


class AppGovernance:
    """Main class for managing app governance and lifecycle"""
    
    def __init__(self):
        self.compliance_checks = {}  # Dict[check_id, ComplianceCheck]
        self.compliance_results = {}  # Dict[result_id, ComplianceResult]
        self.approval_workflows = {}  # Dict[workflow_id, ApprovalWorkflow]
        
        # Define transition requirements
        self.transition_requirements = {
            (AppStatus.DRAFT, AppStatus.EXPERIMENTAL): ["basic_validation"],
            (AppStatus.EXPERIMENTAL, AppStatus.VALIDATION): ["performance_metrics", "bias_check"],
            (AppStatus.VALIDATION, AppStatus.APPROVED): ["security_check", "fairness_check", "documentation"],
            (AppStatus.APPROVED, AppStatus.PRODUCTION): ["deployment_readiness", "operational_approval"]
        }
        
        # Initialize standard compliance checks
        self._initialize_standard_checks()
        
    def _initialize_standard_checks(self) -> None:
        """Initialize the standard compliance checks"""
        standard_checks = [
            ComplianceCheck("Basic Validation", "Validates that the app meets minimal functionality requirements", "validation"),
            ComplianceCheck("Performance Metrics", "Checks the performance metrics of the app", "performance"),
            ComplianceCheck("Bias Check", "Detects potential biases in the AI model", "fairness"),
            ComplianceCheck("Security Check", "Validates the security of the app", "security"),
            ComplianceCheck("Fairness Check", "Comprehensive assessment of fairness across different demographics", "fairness"),
            ComplianceCheck("Documentation Check", "Ensures the app is properly documented", "documentation"),
            ComplianceCheck("Deployment Readiness", "Checks if the app is ready for deployment", "operations"),
            ComplianceCheck("Operational Approval", "Final operational approval before production", "operations")
        ]
        
        for check in standard_checks:
            self.compliance_checks[check.id] = check
    
    def register_compliance_check(self, check: ComplianceCheck) -> str:
        """Register a new compliance check"""
        self.compliance_checks[check.id] = check
        return check.id
    
    def create_compliance_result(self, app_id: str, version: str, check_id: str) -> ComplianceResult:
        """Create a new compliance result"""
        if check_id not in self.compliance_checks:
            raise ValueError(f"Compliance check not found: {check_id}")
            
        result = ComplianceResult(app_id, version, check_id)
        self.compliance_results[result.id] = result
        return result
    
    def update_compliance_result(self, result_id: str, status: str, details: Dict[str, Any]) -> None:
        """Update a compliance result"""
        if result_id not in self.compliance_results:
            raise ValueError(f"Compliance result not found: {result_id}")
            
        result = self.compliance_results[result_id]
        result.update_result(status, details)
        
    def get_app_compliance_status(self, app_id: str, version: str) -> Dict[str, Any]:
        """Get the overall compliance status for an app version"""
        results = []
        
        for result in self.compliance_results.values():
            if result.app_id == app_id and result.version == version:
                check = self.compliance_checks[result.check_id]
                results.append({
                    "check_name": check.name,
                    "check_type": check.check_type,
                    "status": result.status,
                    "details": result.details
                })
                
        return {
            "app_id": app_id,
            "version": version,
            "checks": results,
            "overall_status": "passed" if all(r["status"] == "passed" for r in results) else "failed"
        }
    
    def create_approval_workflow(self, app_id: str, from_status: AppStatus, to_status: AppStatus) -> ApprovalWorkflow:
        """Create a new approval workflow"""
        # Check if this transition is allowed
        key = (from_status, to_status)
        if key not in self.transition_requirements:
            raise ValueError(f"Invalid status transition: {from_status.value} to {to_status.value}")
            
        workflow = ApprovalWorkflow(app_id, from_status, to_status)
        
        # Add standard approval steps based on the transition
        if from_status == AppStatus.DRAFT and to_status == AppStatus.EXPERIMENTAL:
            workflow.add_step("team_lead", "Initial review and approval for experimental use")
        elif from_status == AppStatus.EXPERIMENTAL and to_status == AppStatus.VALIDATION:
            workflow.add_step("data_scientist", "Validation of model performance metrics")
            workflow.add_step("compliance_officer", "Review of potential bias issues")
        elif from_status == AppStatus.VALIDATION and to_status == AppStatus.APPROVED:
            workflow.add_step("security_officer", "Security review and approval")
            workflow.add_step("ethics_committee", "Fairness and ethics review")
            workflow.add_step("department_head", "Final business approval")
        elif from_status == AppStatus.APPROVED and to_status == AppStatus.PRODUCTION:
            workflow.add_step("operations_team", "Deployment readiness assessment")
            workflow.add_step("cto_office", "Final technical approval")
            workflow.add_step("executive_sponsor", "Executive sponsorship approval")
            
        self.approval_workflows[workflow.id] = workflow
        return workflow
    
    def get_approval_workflow(self, workflow_id: str) -> Optional[ApprovalWorkflow]:
        """Get an approval workflow by ID"""
        return self.approval_workflows.get(workflow_id)
    
    def get_app_approval_workflows(self, app_id: str) -> List[Dict[str, Any]]:
        """Get all approval workflows for an app"""
        workflows = []
        
        for workflow in self.approval_workflows.values():
            if workflow.app_id == app_id:
                workflows.append(workflow.to_dict())
                
        return workflows
    
    def approve_workflow_step(self, workflow_id: str, user_id: str, comments: str = "") -> bool:
        """Approve the current step in an approval workflow"""
        if workflow_id not in self.approval_workflows:
            raise ValueError(f"Approval workflow not found: {workflow_id}")
            
        workflow = self.approval_workflows[workflow_id]
        return workflow.approve_current_step(user_id, comments)
    
    def reject_workflow_step(self, workflow_id: str, user_id: str, comments: str) -> bool:
        """Reject the current step in an approval workflow"""
        if workflow_id not in self.approval_workflows:
            raise ValueError(f"Approval workflow not found: {workflow_id}")
            
        workflow = self.approval_workflows[workflow_id]
        return workflow.reject_current_step(user_id, comments)
    
    def can_transition_app_status(self, app_id: str, version: str, 
                                 from_status: AppStatus, to_status: AppStatus) -> Dict[str, Any]:
        """Check if an app can transition from one status to another"""
        # Check if this transition is allowed
        key = (from_status, to_status)
        if key not in self.transition_requirements:
            return {
                "can_transition": False,
                "reason": f"Invalid status transition: {from_status.value} to {to_status.value}"
            }
            
        # Get required compliance checks for this transition
        required_checks = self.transition_requirements[key]
        
        # Get current compliance status
        compliance_status = self.get_app_compliance_status(app_id, version)
        
        # Check if all required checks are passed
        missing_checks = []
        failed_checks = []
        
        for required in required_checks:
            found = False
            for check in compliance_status["checks"]:
                if check["check_name"].lower().replace(" ", "_") == required:
                    found = True
                    if check["status"] != "passed":
                        failed_checks.append(required)
                    break
                    
            if not found:
                missing_checks.append(required)
                
        if missing_checks or failed_checks:
            return {
                "can_transition": False,
                "missing_checks": missing_checks,
                "failed_checks": failed_checks
            }
            
        # Check if there's an approval workflow for this transition
        for workflow in self.approval_workflows.values():
            if (workflow.app_id == app_id and 
                workflow.from_status == from_status and 
                workflow.to_status == to_status and
                workflow.status != "rejected"):
                
                if workflow.status != "completed":
                    return {
                        "can_transition": False,
                        "reason": "Approval workflow in progress",
                        "workflow_id": workflow.id,
                        "workflow_status": workflow.status
                    }
                    
                return {
                    "can_transition": True,
                    "workflow_id": workflow.id
                }
                
        # No existing workflow, but all checks passed, so can create a new workflow
        return {
            "can_transition": True,
            "needs_workflow": True
        }


# Example usage
if __name__ == "__main__":
    # Create governance system
    governance = AppGovernance()
    
    # Create a compliance result
    app_id = "app-123"
    version = "1.0.0"
    
    # Get the ID of the Basic Validation check
    basic_validation_id = None
    for check_id, check in governance.compliance_checks.items():
        if check.name == "Basic Validation":
            basic_validation_id = check_id
            break
    
    if basic_validation_id:
        # Create a compliance result
        result = governance.create_compliance_result(app_id, version, basic_validation_id)
        
        # Update the result
        governance.update_compliance_result(result.id, "passed", {
            "score": 0.95,
            "tests_passed": 42,
            "tests_failed": 2
        })
        
        # Get the compliance status
        status = governance.get_app_compliance_status(app_id, version)
        print(f"Compliance status: {status}")
        
        # Create an approval workflow
        workflow = governance.create_approval_workflow(
            app_id, AppStatus.DRAFT, AppStatus.EXPERIMENTAL)
        
        # Approve the first step
        governance.approve_workflow_step(workflow.id, "user-456", "Looks good!")
        
        # Get the updated workflow
        updated_workflow = governance.get_approval_workflow(workflow.id)
        print(f"Workflow status: {updated_workflow.status}")
        print(f"Current step: {updated_workflow.current_step}")
        
        # Check if can transition
        can_transition = governance.can_transition_app_status(
            app_id, version, AppStatus.DRAFT, AppStatus.EXPERIMENTAL)
        print(f"Can transition: {can_transition}")