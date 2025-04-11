#!/usr/bin/env python3
"""
Automation Module for AI App Store Workspaces

This module provides functionality for automating tasks, including
web browser automation for web applications and system automation.
"""

import enum
import uuid
import logging
import datetime
import json
import time
import subprocess
import os
import tempfile
from typing import Dict, List, Any, Optional, Union, Callable, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AutomationType(enum.Enum):
    """Enum representing types of automation"""
    BROWSER = "browser"
    SYSTEM = "system"
    API = "api"
    DATABASE = "database"
    CUSTOM = "custom"


class BrowserAction(enum.Enum):
    """Enum representing browser automation actions"""
    NAVIGATE = "navigate"
    CLICK = "click"
    TYPE = "type"
    SELECT = "select"
    EXTRACT = "extract"
    WAIT = "wait"
    SCREENSHOT = "screenshot"
    EXECUTE_SCRIPT = "execute_script"
    CUSTOM = "custom"


class AutomationTask:
    """Represents an automation task"""
    
    def __init__(self, name: str, automation_type: AutomationType, created_by: str):
        self.id = str(uuid.uuid4())
        self.name = name
        self.automation_type = automation_type
        self.created_by = created_by
        self.steps = []
        self.schedule = None
        self.created_at = datetime.datetime.utcnow()
        self.updated_at = self.created_at
        self.last_run_at = None
        self.last_run_status = None
        self.last_run_result = None
        
    def add_step(self, step_type: str, parameters: Dict[str, Any]) -> None:
        """Add a step to the task"""
        step = {
            "id": str(uuid.uuid4()),
            "type": step_type,
            "parameters": parameters,
            "order": len(self.steps) + 1
        }
        self.steps.append(step)
        self.updated_at = datetime.datetime.utcnow()
        
    def set_schedule(self, schedule: Dict[str, Any]) -> None:
        """Set the schedule for the task"""
        self.schedule = schedule
        self.updated_at = datetime.datetime.utcnow()
        
    def update_last_run(self, status: str, result: Dict[str, Any]) -> None:
        """Update information about the last run"""
        self.last_run_at = datetime.datetime.utcnow()
        self.last_run_status = status
        self.last_run_result = result
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "name": self.name,
            "automation_type": self.automation_type.value,
            "created_by": self.created_by,
            "steps": self.steps,
            "schedule": self.schedule,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_run_at": self.last_run_at.isoformat() if self.last_run_at else None,
            "last_run_status": self.last_run_status,
            "last_run_result": self.last_run_result
        }


class AutomationSession:
    """Represents a running automation session"""
    
    def __init__(self, task_id: str, initiated_by: str):
        self.id = str(uuid.uuid4())
        self.task_id = task_id
        self.initiated_by = initiated_by
        self.status = "initializing"  # initializing, running, completed, failed, aborted
        self.current_step = 0
        self.logs = []
        self.result = None
        self.error = None
        self.started_at = datetime.datetime.utcnow()
        self.completed_at = None
        
    def start(self) -> None:
        """Mark the session as started"""
        self.status = "running"
        self.add_log("Session started")
        
    def complete(self, result: Dict[str, Any]) -> None:
        """Mark the session as completed"""
        self.status = "completed"
        self.result = result
        self.completed_at = datetime.datetime.utcnow()
        self.add_log("Session completed")
        
    def fail(self, error: str) -> None:
        """Mark the session as failed"""
        self.status = "failed"
        self.error = error
        self.completed_at = datetime.datetime.utcnow()
        self.add_log(f"Session failed: {error}")
        
    def abort(self) -> None:
        """Mark the session as aborted"""
        self.status = "aborted"
        self.completed_at = datetime.datetime.utcnow()
        self.add_log("Session aborted")
        
    def update_current_step(self, step_number: int) -> None:
        """Update the current step"""
        self.current_step = step_number
        self.add_log(f"Executing step {step_number}")
        
    def add_log(self, message: str) -> None:
        """Add a log message"""
        self.logs.append({
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "message": message
        })
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "task_id": self.task_id,
            "initiated_by": self.initiated_by,
            "status": self.status,
            "current_step": self.current_step,
            "logs": self.logs,
            "result": self.result,
            "error": self.error,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


class SeleniumBrowserAutomation:
    """Browser automation implementation using Selenium"""
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.driver = None
        self.initialized = False
        
    def initialize(self) -> bool:
        """Initialize the browser driver"""
        try:
            # This is a stub implementation for demonstration purposes
            # In a real implementation, this would initialize a Selenium WebDriver
            logger.info("Initializing Selenium browser automation")
            
            # Simulate initialization time
            time.sleep(1)
            
            self.initialized = True
            return True
            
        except Exception as e:
            logger.error(f"Error initializing browser automation: {str(e)}")
            return False
            
    def close(self) -> None:
        """Close the browser driver"""
        if self.initialized:
            logger.info("Closing browser automation")
            self.initialized = False
            
    def execute_action(self, action: BrowserAction, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a browser action"""
        if not self.initialized:
            raise ValueError("Browser automation not initialized")
            
        logger.info(f"Executing browser action: {action.value}")
        
        # This is a stub implementation for demonstration purposes
        # In a real implementation, this would execute Selenium commands
        
        if action == BrowserAction.NAVIGATE:
            url = parameters.get("url")
            if not url:
                raise ValueError("URL is required for navigate action")
                
            logger.info(f"Navigating to {url}")
            return {"status": "success", "action": "navigate", "url": url}
            
        elif action == BrowserAction.CLICK:
            selector = parameters.get("selector")
            if not selector:
                raise ValueError("Selector is required for click action")
                
            logger.info(f"Clicking element with selector: {selector}")
            return {"status": "success", "action": "click", "selector": selector}
            
        elif action == BrowserAction.TYPE:
            selector = parameters.get("selector")
            text = parameters.get("text")
            if not selector or text is None:
                raise ValueError("Selector and text are required for type action")
                
            logger.info(f"Typing '{text}' into element with selector: {selector}")
            return {"status": "success", "action": "type", "selector": selector, "text": text}
            
        elif action == BrowserAction.SELECT:
            selector = parameters.get("selector")
            value = parameters.get("value")
            if not selector or value is None:
                raise ValueError("Selector and value are required for select action")
                
            logger.info(f"Selecting value '{value}' in element with selector: {selector}")
            return {"status": "success", "action": "select", "selector": selector, "value": value}
            
        elif action == BrowserAction.EXTRACT:
            selector = parameters.get("selector")
            if not selector:
                raise ValueError("Selector is required for extract action")
                
            logger.info(f"Extracting data from element with selector: {selector}")
            # Simulate extracted data
            return {
                "status": "success", 
                "action": "extract", 
                "selector": selector,
                "data": "Simulated extracted data"
            }
            
        elif action == BrowserAction.WAIT:
            seconds = parameters.get("seconds", 1)
            condition = parameters.get("condition")
            
            if condition:
                logger.info(f"Waiting for condition: {condition}")
            else:
                logger.info(f"Waiting for {seconds} seconds")
                time.sleep(seconds)
                
            return {"status": "success", "action": "wait", "seconds": seconds}
            
        elif action == BrowserAction.SCREENSHOT:
            logger.info("Taking screenshot")
            # Simulate taking a screenshot
            return {
                "status": "success", 
                "action": "screenshot", 
                "image_data": "base64_encoded_image_data_would_be_here"
            }
            
        elif action == BrowserAction.EXECUTE_SCRIPT:
            script = parameters.get("script")
            if not script:
                raise ValueError("Script is required for execute_script action")
                
            logger.info("Executing JavaScript")
            return {"status": "success", "action": "execute_script"}
            
        else:
            raise ValueError(f"Unsupported browser action: {action}")


class EncompassAutomation:
    """Specialized automation for Encompass mortgage software"""
    
    def __init__(self):
        self.browser = SeleniumBrowserAutomation()
        self.logged_in = False
        
    def initialize(self) -> bool:
        """Initialize the automation"""
        return self.browser.initialize()
        
    def close(self) -> None:
        """Close the automation"""
        self.browser.close()
        self.logged_in = False
        
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Login to Encompass"""
        if not username or not password:
            raise ValueError("Username and password are required")
            
        # Navigate to login page
        self.browser.execute_action(BrowserAction.NAVIGATE, {"url": "https://encompass.example.com/login"})
        
        # Type username
        self.browser.execute_action(BrowserAction.TYPE, {"selector": "#username", "text": username})
        
        # Type password
        self.browser.execute_action(BrowserAction.TYPE, {"selector": "#password", "text": password})
        
        # Click login button
        self.browser.execute_action(BrowserAction.CLICK, {"selector": "#login-button"})
        
        # Wait for login to complete
        self.browser.execute_action(BrowserAction.WAIT, {"seconds": 2})
        
        # In a real implementation, this would check if login was successful
        self.logged_in = True
        
        return {"status": "success", "logged_in": True}
        
    def search_loan(self, loan_number: str) -> Dict[str, Any]:
        """Search for a loan by number"""
        if not self.logged_in:
            raise ValueError("Not logged in to Encompass")
            
        if not loan_number:
            raise ValueError("Loan number is required")
            
        # Navigate to loan search
        self.browser.execute_action(BrowserAction.NAVIGATE, {"url": "https://encompass.example.com/loans/search"})
        
        # Enter loan number
        self.browser.execute_action(BrowserAction.TYPE, {"selector": "#loan-search", "text": loan_number})
        
        # Click search button
        self.browser.execute_action(BrowserAction.CLICK, {"selector": "#search-button"})
        
        # Wait for results
        self.browser.execute_action(BrowserAction.WAIT, {"seconds": 1})
        
        # Click on the loan
        self.browser.execute_action(BrowserAction.CLICK, {"selector": f"#loan-{loan_number}"})
        
        # Wait for loan to load
        self.browser.execute_action(BrowserAction.WAIT, {"seconds": 2})
        
        return {"status": "success", "loan_loaded": True, "loan_number": loan_number}
        
    def get_loan_data(self) -> Dict[str, Any]:
        """Extract data from the current loan"""
        if not self.logged_in:
            raise ValueError("Not logged in to Encompass")
            
        # Extract borrower information
        borrower_data = self.browser.execute_action(
            BrowserAction.EXTRACT, 
            {"selector": "#borrower-info"}
        )
        
        # Extract loan information
        loan_data = self.browser.execute_action(
            BrowserAction.EXTRACT, 
            {"selector": "#loan-details"}
        )
        
        # Extract property information
        property_data = self.browser.execute_action(
            BrowserAction.EXTRACT, 
            {"selector": "#property-info"}
        )
        
        # Simulate combined data
        return {
            "status": "success",
            "borrower": {
                "name": "John Doe",
                "phone": "555-123-4567",
                "email": "john.doe@example.com"
            },
            "loan": {
                "number": "L-12345",
                "amount": 250000,
                "term": 30,
                "rate": 4.5
            },
            "property": {
                "address": "123 Main St, Anytown, USA",
                "type": "Single Family",
                "value": 300000
            }
        }
        
    def update_loan_status(self, status: str) -> Dict[str, Any]:
        """Update the status of the current loan"""
        if not self.logged_in:
            raise ValueError("Not logged in to Encompass")
            
        if not status:
            raise ValueError("Status is required")
            
        # Navigate to status section
        self.browser.execute_action(BrowserAction.CLICK, {"selector": "#status-tab"})
        
        # Select new status
        self.browser.execute_action(BrowserAction.SELECT, {"selector": "#status-select", "value": status})
        
        # Save changes
        self.browser.execute_action(BrowserAction.CLICK, {"selector": "#save-button"})
        
        # Wait for save to complete
        self.browser.execute_action(BrowserAction.WAIT, {"seconds": 1})
        
        return {"status": "success", "loan_status_updated": True, "new_status": status}


class SystemAutomation:
    """System automation for executing commands and scripts"""
    
    def execute_command(self, command: str, timeout: Optional[int] = None) -> Dict[str, Any]:
        """Execute a system command"""
        try:
            # Execute the command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return {
                "status": "success" if result.returncode == 0 else "error",
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
        except subprocess.TimeoutExpired:
            return {
                "status": "timeout",
                "error": f"Command timed out after {timeout} seconds"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
            
    def execute_script(self, script_content: str, script_type: str, 
                     parameters: Optional[Dict[str, Any]] = None,
                     timeout: Optional[int] = None) -> Dict[str, Any]:
        """Execute a script"""
        try:
            # Create a temporary script file
            if script_type == "python":
                ext = ".py"
                interpreter = "python"
            elif script_type == "shell":
                ext = ".sh"
                interpreter = "bash"
            else:
                return {
                    "status": "error",
                    "error": f"Unsupported script type: {script_type}"
                }
                
            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as temp:
                # Write the script content
                temp.write(script_content.encode())
                temp_path = temp.name
                
            # Make the script executable if it's a shell script
            if script_type == "shell":
                os.chmod(temp_path, 0o755)
                
            # Prepare command
            cmd = [interpreter, temp_path]
            
            # Add parameters if provided
            if parameters:
                # Convert parameters to environment variables
                env = os.environ.copy()
                for key, value in parameters.items():
                    env[key] = str(value)
                    
                # Execute with environment variables
                result = subprocess.run(
                    cmd,
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
            else:
                # Execute without parameters
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
                
            # Clean up the temporary file
            os.unlink(temp_path)
            
            return {
                "status": "success" if result.returncode == 0 else "error",
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
        except subprocess.TimeoutExpired:
            # Clean up the temporary file
            os.unlink(temp_path)
            
            return {
                "status": "timeout",
                "error": f"Script execution timed out after {timeout} seconds"
            }
            
        except Exception as e:
            # Clean up the temporary file if it exists
            if 'temp_path' in locals():
                os.unlink(temp_path)
                
            return {
                "status": "error",
                "error": str(e)
            }


class AutomationManager:
    """Main class for managing automations"""
    
    def __init__(self):
        self.tasks: Dict[str, AutomationTask] = {}
        self.sessions: Dict[str, AutomationSession] = {}
        self.browser_automation = SeleniumBrowserAutomation()
        self.encompass_automation = EncompassAutomation()
        self.system_automation = SystemAutomation()
        
    def create_task(self, name: str, automation_type: AutomationType, created_by: str) -> str:
        """Create a new automation task"""
        task = AutomationTask(name, automation_type, created_by)
        self.tasks[task.id] = task
        return task.id
        
    def get_task(self, task_id: str) -> Optional[AutomationTask]:
        """Get a task by ID"""
        return self.tasks.get(task_id)
        
    def list_tasks(self, created_by: Optional[str] = None) -> List[Dict[str, Any]]:
        """List tasks, optionally filtered by creator"""
        result = []
        
        for task in self.tasks.values():
            if created_by and task.created_by != created_by:
                continue
                
            result.append(task.to_dict())
            
        return result
        
    def add_browser_step(self, task_id: str, action: BrowserAction, 
                        parameters: Dict[str, Any]) -> bool:
        """Add a browser automation step to a task"""
        task = self.tasks.get(task_id)
        if not task or task.automation_type != AutomationType.BROWSER:
            return False
            
        task.add_step(action.value, parameters)
        return True
        
    def add_system_step(self, task_id: str, command: str, 
                       parameters: Optional[Dict[str, Any]] = None) -> bool:
        """Add a system automation step to a task"""
        task = self.tasks.get(task_id)
        if not task or task.automation_type != AutomationType.SYSTEM:
            return False
            
        task.add_step("command", {
            "command": command,
            "parameters": parameters or {}
        })
        return True
        
    def add_encompass_step(self, task_id: str, action: str, 
                          parameters: Dict[str, Any]) -> bool:
        """Add an Encompass automation step to a task"""
        task = self.tasks.get(task_id)
        if not task or task.automation_type != AutomationType.BROWSER:
            return False
            
        task.add_step("encompass_" + action, parameters)
        return True
        
    def set_task_schedule(self, task_id: str, schedule: Dict[str, Any]) -> bool:
        """Set the schedule for a task"""
        task = self.tasks.get(task_id)
        if not task:
            return False
            
        task.set_schedule(schedule)
        return True
        
    def execute_task(self, task_id: str, initiated_by: str) -> Optional[str]:
        """Execute a task"""
        task = self.tasks.get(task_id)
        if not task:
            return None
            
        session = AutomationSession(task_id, initiated_by)
        self.sessions[session.id] = session
        
        # Start execution in a separate thread or process in a real implementation
        # For this example, we'll execute synchronously
        try:
            session.start()
            
            if task.automation_type == AutomationType.BROWSER:
                result = self._execute_browser_task(task, session)
            elif task.automation_type == AutomationType.SYSTEM:
                result = self._execute_system_task(task, session)
            else:
                session.fail(f"Unsupported automation type: {task.automation_type}")
                return session.id
                
            session.complete(result)
            task.update_last_run("success", result)
            
        except Exception as e:
            logger.error(f"Error executing task: {str(e)}")
            session.fail(str(e))
            task.update_last_run("error", {"error": str(e)})
            
        return session.id
        
    def _execute_browser_task(self, task: AutomationTask, session: AutomationSession) -> Dict[str, Any]:
        """Execute a browser automation task"""
        try:
            # Initialize browser
            self.browser_automation.initialize()
            
            results = []
            
            # Execute each step
            for i, step in enumerate(task.steps):
                step_num = i + 1
                session.update_current_step(step_num)
                
                # Extract step information
                step_type = step["type"]
                parameters = step["parameters"]
                
                # Check if it's an Encompass-specific step
                if step_type.startswith("encompass_"):
                    encompass_action = step_type[len("encompass_"):]
                    
                    # Initialize Encompass if not already done
                    if not hasattr(self, "_encompass_initialized") or not self._encompass_initialized:
                        self.encompass_automation.initialize()
                        self._encompass_initialized = True
                        
                    # Execute Encompass action
                    if encompass_action == "login":
                        result = self.encompass_automation.login(
                            parameters.get("username"),
                            parameters.get("password")
                        )
                    elif encompass_action == "search_loan":
                        result = self.encompass_automation.search_loan(
                            parameters.get("loan_number")
                        )
                    elif encompass_action == "get_loan_data":
                        result = self.encompass_automation.get_loan_data()
                    elif encompass_action == "update_loan_status":
                        result = self.encompass_automation.update_loan_status(
                            parameters.get("status")
                        )
                    else:
                        result = {"status": "error", "error": f"Unsupported Encompass action: {encompass_action}"}
                        
                else:
                    # Regular browser action
                    try:
                        action = BrowserAction(step_type)
                        result = self.browser_automation.execute_action(action, parameters)
                    except ValueError:
                        result = {"status": "error", "error": f"Unsupported browser action: {step_type}"}
                        
                # Add result to the list
                results.append({
                    "step": step_num,
                    "type": step_type,
                    "result": result
                })
                
                # Check if the step failed
                if result.get("status") == "error":
                    session.add_log(f"Step {step_num} failed: {result.get('error')}")
                    break
                    
            # Close browser
            self.browser_automation.close()
            
            # Close Encompass if it was initialized
            if hasattr(self, "_encompass_initialized") and self._encompass_initialized:
                self.encompass_automation.close()
                self._encompass_initialized = False
                
            return {"steps": results}
            
        finally:
            # Make sure to close browser and Encompass
            self.browser_automation.close()
            
            if hasattr(self, "_encompass_initialized") and self._encompass_initialized:
                self.encompass_automation.close()
                self._encompass_initialized = False
                
    def _execute_system_task(self, task: AutomationTask, session: AutomationSession) -> Dict[str, Any]:
        """Execute a system automation task"""
        results = []
        
        # Execute each step
        for i, step in enumerate(task.steps):
            step_num = i + 1
            session.update_current_step(step_num)
            
            # Extract step information
            step_type = step["type"]
            parameters = step["parameters"]
            
            if step_type == "command":
                # Execute command
                command = parameters.get("command")
                command_params = parameters.get("parameters", {})
                timeout = command_params.get("timeout")
                
                result = self.system_automation.execute_command(command, timeout)
                
            elif step_type == "script":
                # Execute script
                script_content = parameters.get("content")
                script_type = parameters.get("type", "python")
                script_params = parameters.get("parameters", {})
                timeout = parameters.get("timeout")
                
                result = self.system_automation.execute_script(
                    script_content, script_type, script_params, timeout)
                
            else:
                result = {"status": "error", "error": f"Unsupported system step type: {step_type}"}
                
            # Add result to the list
            results.append({
                "step": step_num,
                "type": step_type,
                "result": result
            })
            
            # Check if the step failed
            if result.get("status") in ["error", "timeout"]:
                session.add_log(f"Step {step_num} failed: {result.get('error')}")
                break
                
        return {"steps": results}
        
    def get_session(self, session_id: str) -> Optional[AutomationSession]:
        """Get a session by ID"""
        return self.sessions.get(session_id)
        
    def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a session"""
        session = self.sessions.get(session_id)
        if not session:
            return None
            
        return session.to_dict()
        
    def abort_session(self, session_id: str) -> bool:
        """Abort a running session"""
        session = self.sessions.get(session_id)
        if not session or session.status != "running":
            return False
            
        session.abort()
        
        # In a real implementation, this would also stop the automation
        # For this example, we'll assume it's stopped
        
        return True


# Example usage
if __name__ == "__main__":
    # Create automation manager
    manager = AutomationManager()
    
    # Create a browser automation task
    task_id = manager.create_task(
        "Sample Web Form Automation",
        AutomationType.BROWSER,
        "user-123"
    )
    print(f"Created task: {task_id}")
    
    # Add steps
    manager.add_browser_step(
        task_id,
        BrowserAction.NAVIGATE,
        {"url": "https://example.com/form"}
    )
    
    manager.add_browser_step(
        task_id,
        BrowserAction.TYPE,
        {"selector": "#name", "text": "John Doe"}
    )
    
    manager.add_browser_step(
        task_id,
        BrowserAction.TYPE,
        {"selector": "#email", "text": "john.doe@example.com"}
    )
    
    manager.add_browser_step(
        task_id,
        BrowserAction.CLICK,
        {"selector": "#submit-button"}
    )
    
    manager.add_browser_step(
        task_id,
        BrowserAction.WAIT,
        {"seconds": 2}
    )
    
    manager.add_browser_step(
        task_id,
        BrowserAction.EXTRACT,
        {"selector": "#confirmation-message"}
    )
    
    # Execute the task
    session_id = manager.execute_task(task_id, "user-123")
    print(f"Started session: {session_id}")
    
    # Get session status
    session = manager.get_session_status(session_id)
    print(f"Session status: {session['status']}")
    print(f"Steps completed: {session['current_step']}")
    
    # Create an Encompass automation task
    task_id = manager.create_task(
        "Encompass Loan Status Update",
        AutomationType.BROWSER,
        "user-456"
    )
    
    # Add Encompass-specific steps
    manager.add_encompass_step(
        task_id,
        "login",
        {"username": "user@example.com", "password": "password123"}
    )
    
    manager.add_encompass_step(
        task_id,
        "search_loan",
        {"loan_number": "L-12345"}
    )
    
    manager.add_encompass_step(
        task_id,
        "update_loan_status",
        {"status": "Approved"}
    )
    
    # Create a system automation task
    sys_task_id = manager.create_task(
        "System Backup",
        AutomationType.SYSTEM,
        "user-789"
    )
    
    # Add system steps
    manager.add_system_step(
        sys_task_id,
        "echo 'Starting backup process'"
    )
    
    manager.add_system_step(
        sys_task_id,
        "mkdir -p ~/backups/$(date +%Y-%m-%d)"
    )
    
    # Schedule the task
    manager.set_task_schedule(
        sys_task_id,
        {
            "frequency": "daily",
            "time": "03:00",
            "days": ["Monday", "Wednesday", "Friday"]
        }
    )
    
    # List all tasks
    tasks = manager.list_tasks()
    print(f"\nAll tasks ({len(tasks)}):")
    for task in tasks:
        print(f"- {task['name']} ({task['automation_type']})")
        print(f"  Steps: {len(task['steps'])}")
        if task['schedule']:
            print(f"  Schedule: {task['schedule']['frequency']} at {task['schedule']['time']}")