#!/usr/bin/env python3
"""
Developer Tools Module for AI App Store Workspaces

This module provides development tools for code generation, codebase understanding,
writing and editing code, and Git operations for version control.
"""

import enum
import uuid
import logging
import datetime
import os
import subprocess
import tempfile
import json
import difflib
from typing import Dict, List, Any, Optional, Union, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CodeLanguage(enum.Enum):
    """Enum representing supported programming languages"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CPP = "cpp"
    CSHARP = "csharp"
    GO = "go"
    RUST = "rust"
    SQL = "sql"
    HTML = "html"
    CSS = "css"
    SHELL = "shell"
    OTHER = "other"


class ToolType(enum.Enum):
    """Enum representing types of developer tools"""
    CODE_GENERATION = "code_generation"
    CODE_UNDERSTANDING = "code_understanding"
    CODE_EDITING = "code_editing"
    GIT_OPERATIONS = "git_operations"
    PROJECT_MANAGEMENT = "project_management"
    TESTING = "testing"
    DEBUGGING = "debugging"
    CUSTOM = "custom"


class CodeSnippet:
    """Represents a code snippet"""
    
    def __init__(self, code: str, language: CodeLanguage, description: str = ""):
        self.id = str(uuid.uuid4())
        self.code = code
        self.language = language
        self.description = description
        self.created_at = datetime.datetime.utcnow()
        self.metadata = {}
        
    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to the code snippet"""
        self.metadata[key] = value
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "code": self.code,
            "language": self.language.value,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata
        }


class CodeEdit:
    """Represents an edit to a code file"""
    
    def __init__(self, file_path: str):
        self.id = str(uuid.uuid4())
        self.file_path = file_path
        self.edits = []  # List of edit operations
        self.created_at = datetime.datetime.utcnow()
        
    def add_insertion(self, position: int, content: str) -> None:
        """Add an insertion edit"""
        self.edits.append({
            "type": "insertion",
            "position": position,
            "content": content
        })
        
    def add_deletion(self, start: int, end: int) -> None:
        """Add a deletion edit"""
        self.edits.append({
            "type": "deletion",
            "start": start,
            "end": end
        })
        
    def add_replacement(self, start: int, end: int, content: str) -> None:
        """Add a replacement edit"""
        self.edits.append({
            "type": "replacement",
            "start": start,
            "end": end,
            "content": content
        })
        
    def apply(self, original_content: str) -> str:
        """Apply the edits to the original content"""
        # Sort edits in reverse order to avoid position changes
        sorted_edits = sorted(self.edits, key=lambda e: e.get("position", e.get("start", 0)), reverse=True)
        
        content = original_content
        
        for edit in sorted_edits:
            if edit["type"] == "insertion":
                position = edit["position"]
                content = content[:position] + edit["content"] + content[position:]
            elif edit["type"] == "deletion":
                start, end = edit["start"], edit["end"]
                content = content[:start] + content[end:]
            elif edit["type"] == "replacement":
                start, end = edit["start"], edit["end"]
                content = content[:start] + edit["content"] + content[end:]
                
        return content
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "file_path": self.file_path,
            "edits": self.edits,
            "created_at": self.created_at.isoformat()
        }


class GitOperation:
    """Represents a Git operation"""
    
    def __init__(self, operation_type: str, repository_path: str):
        self.id = str(uuid.uuid4())
        self.operation_type = operation_type
        self.repository_path = repository_path
        self.params = {}
        self.created_at = datetime.datetime.utcnow()
        self.status = "pending"  # pending, success, failure
        self.result = None
        self.error = None
        
    def set_params(self, params: Dict[str, Any]) -> None:
        """Set parameters for the Git operation"""
        self.params = params
        
    def execute(self) -> bool:
        """Execute the Git operation"""
        try:
            if self.operation_type == "commit":
                return self._execute_commit()
            elif self.operation_type == "push":
                return self._execute_push()
            elif self.operation_type == "pull":
                return self._execute_pull()
            elif self.operation_type == "checkout":
                return self._execute_checkout()
            elif self.operation_type == "branch":
                return self._execute_branch()
            elif self.operation_type == "status":
                return self._execute_status()
            elif self.operation_type == "log":
                return self._execute_log()
            else:
                self.status = "failure"
                self.error = f"Unsupported Git operation: {self.operation_type}"
                return False
        except Exception as e:
            self.status = "failure"
            self.error = str(e)
            logger.error(f"Error executing Git operation: {str(e)}")
            return False
            
    def _execute_commit(self) -> bool:
        """Execute a Git commit operation"""
        if "message" not in self.params:
            self.error = "Commit message is required"
            self.status = "failure"
            return False
            
        try:
            # Change to repository directory
            cwd = os.getcwd()
            os.chdir(self.repository_path)
            
            # Add files if specified
            if "files" in self.params:
                files = self.params["files"]
                if isinstance(files, list):
                    files_str = " ".join(files)
                else:
                    files_str = files
                    
                add_result = subprocess.run(
                    ["git", "add", *files_str.split()],
                    capture_output=True,
                    text=True
                )
                
                if add_result.returncode != 0:
                    self.error = f"Error adding files: {add_result.stderr}"
                    self.status = "failure"
                    return False
            elif self.params.get("add_all", False):
                add_result = subprocess.run(
                    ["git", "add", "."],
                    capture_output=True,
                    text=True
                )
                
                if add_result.returncode != 0:
                    self.error = f"Error adding all files: {add_result.stderr}"
                    self.status = "failure"
                    return False
                    
            # Commit
            commit_result = subprocess.run(
                ["git", "commit", "-m", self.params["message"]],
                capture_output=True,
                text=True
            )
            
            os.chdir(cwd)  # Restore working directory
            
            if commit_result.returncode != 0:
                self.error = f"Error committing: {commit_result.stderr}"
                self.status = "failure"
                return False
                
            self.result = commit_result.stdout
            self.status = "success"
            return True
            
        except Exception as e:
            os.chdir(cwd)  # Restore working directory
            raise e
            
    def _execute_push(self) -> bool:
        """Execute a Git push operation"""
        try:
            # Change to repository directory
            cwd = os.getcwd()
            os.chdir(self.repository_path)
            
            # Prepare command
            cmd = ["git", "push"]
            
            # Add remote if specified
            if "remote" in self.params:
                cmd.append(self.params["remote"])
                
            # Add branch if specified
            if "branch" in self.params:
                cmd.append(self.params["branch"])
                
            # Add additional options
            if self.params.get("force", False):
                cmd.append("--force")
                
            if self.params.get("set_upstream", False):
                cmd.append("--set-upstream")
                
            # Execute push
            push_result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )
            
            os.chdir(cwd)  # Restore working directory
            
            if push_result.returncode != 0:
                self.error = f"Error pushing: {push_result.stderr}"
                self.status = "failure"
                return False
                
            self.result = push_result.stdout
            self.status = "success"
            return True
            
        except Exception as e:
            os.chdir(cwd)  # Restore working directory
            raise e
            
    def _execute_pull(self) -> bool:
        """Execute a Git pull operation"""
        try:
            # Change to repository directory
            cwd = os.getcwd()
            os.chdir(self.repository_path)
            
            # Prepare command
            cmd = ["git", "pull"]
            
            # Add remote if specified
            if "remote" in self.params:
                cmd.append(self.params["remote"])
                
            # Add branch if specified
            if "branch" in self.params:
                cmd.append(self.params["branch"])
                
            # Execute pull
            pull_result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )
            
            os.chdir(cwd)  # Restore working directory
            
            if pull_result.returncode != 0:
                self.error = f"Error pulling: {pull_result.stderr}"
                self.status = "failure"
                return False
                
            self.result = pull_result.stdout
            self.status = "success"
            return True
            
        except Exception as e:
            os.chdir(cwd)  # Restore working directory
            raise e
            
    def _execute_checkout(self) -> bool:
        """Execute a Git checkout operation"""
        if "branch" not in self.params and "commit" not in self.params:
            self.error = "Branch or commit is required for checkout"
            self.status = "failure"
            return False
            
        try:
            # Change to repository directory
            cwd = os.getcwd()
            os.chdir(self.repository_path)
            
            # Prepare command
            cmd = ["git", "checkout"]
            
            # Add branch or commit
            if "branch" in self.params:
                cmd.append(self.params["branch"])
            elif "commit" in self.params:
                cmd.append(self.params["commit"])
                
            # Add create branch option
            if self.params.get("create_branch", False):
                cmd.insert(1, "-b")
                
            # Execute checkout
            checkout_result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )
            
            os.chdir(cwd)  # Restore working directory
            
            if checkout_result.returncode != 0:
                self.error = f"Error checking out: {checkout_result.stderr}"
                self.status = "failure"
                return False
                
            self.result = checkout_result.stdout
            self.status = "success"
            return True
            
        except Exception as e:
            os.chdir(cwd)  # Restore working directory
            raise e
            
    def _execute_branch(self) -> bool:
        """Execute a Git branch operation"""
        try:
            # Change to repository directory
            cwd = os.getcwd()
            os.chdir(self.repository_path)
            
            # Prepare command
            cmd = ["git", "branch"]
            
            # Add branch name if creating
            if "name" in self.params:
                cmd.append(self.params["name"])
                
            # Add options
            if self.params.get("list", False):
                # Already the default, but we'll be explicit
                pass
                
            if self.params.get("delete", False):
                cmd.insert(1, "-d")
                
            if self.params.get("force_delete", False):
                cmd.insert(1, "-D")
                
            # Execute branch command
            branch_result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )
            
            os.chdir(cwd)  # Restore working directory
            
            if branch_result.returncode != 0:
                self.error = f"Error with branch command: {branch_result.stderr}"
                self.status = "failure"
                return False
                
            self.result = branch_result.stdout
            self.status = "success"
            return True
            
        except Exception as e:
            os.chdir(cwd)  # Restore working directory
            raise e
            
    def _execute_status(self) -> bool:
        """Execute a Git status operation"""
        try:
            # Change to repository directory
            cwd = os.getcwd()
            os.chdir(self.repository_path)
            
            # Execute status command
            status_result = subprocess.run(
                ["git", "status"],
                capture_output=True,
                text=True
            )
            
            os.chdir(cwd)  # Restore working directory
            
            if status_result.returncode != 0:
                self.error = f"Error getting status: {status_result.stderr}"
                self.status = "failure"
                return False
                
            self.result = status_result.stdout
            self.status = "success"
            return True
            
        except Exception as e:
            os.chdir(cwd)  # Restore working directory
            raise e
            
    def _execute_log(self) -> bool:
        """Execute a Git log operation"""
        try:
            # Change to repository directory
            cwd = os.getcwd()
            os.chdir(self.repository_path)
            
            # Prepare command
            cmd = ["git", "log"]
            
            # Add options
            if "limit" in self.params:
                cmd.append(f"-{self.params['limit']}")
                
            if self.params.get("oneline", False):
                cmd.append("--oneline")
                
            # Execute log command
            log_result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )
            
            os.chdir(cwd)  # Restore working directory
            
            if log_result.returncode != 0:
                self.error = f"Error getting log: {log_result.stderr}"
                self.status = "failure"
                return False
                
            self.result = log_result.stdout
            self.status = "success"
            return True
            
        except Exception as e:
            os.chdir(cwd)  # Restore working directory
            raise e
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "operation_type": self.operation_type,
            "repository_path": self.repository_path,
            "params": self.params,
            "status": self.status,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at.isoformat()
        }


class CodeGenerationRequest:
    """Represents a request for code generation"""
    
    def __init__(self, prompt: str, language: CodeLanguage, 
                model_name: Optional[str] = None):
        self.id = str(uuid.uuid4())
        self.prompt = prompt
        self.language = language
        self.model_name = model_name
        self.created_at = datetime.datetime.utcnow()
        self.context = {}
        self.parameters = {}
        self.result = None
        self.status = "pending"  # pending, processing, completed, failed
        
    def add_context(self, key: str, value: Any) -> None:
        """Add context for the code generation"""
        self.context[key] = value
        
    def set_parameters(self, parameters: Dict[str, Any]) -> None:
        """Set parameters for the code generation"""
        self.parameters = parameters
        
    def set_result(self, result: Dict[str, Any]) -> None:
        """Set the result of the code generation"""
        self.result = result
        self.status = "completed"
        
    def set_failure(self, error: str) -> None:
        """Set the request as failed"""
        self.result = {"error": error}
        self.status = "failed"
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "prompt": self.prompt,
            "language": self.language.value,
            "model_name": self.model_name,
            "created_at": self.created_at.isoformat(),
            "context": self.context,
            "parameters": self.parameters,
            "result": self.result,
            "status": self.status
        }


class CodeFile:
    """Represents a code file for analysis or editing"""
    
    def __init__(self, file_path: str, content: Optional[str] = None):
        self.file_path = file_path
        self.content = content
        
        # Load content if not provided
        if not self.content and os.path.exists(file_path):
            with open(file_path, 'r') as f:
                self.content = f.read()
                
        self.language = self._detect_language()
        
    def _detect_language(self) -> CodeLanguage:
        """Detect the programming language from the file extension"""
        _, ext = os.path.splitext(self.file_path)
        ext = ext.lower()
        
        language_map = {
            '.py': CodeLanguage.PYTHON,
            '.js': CodeLanguage.JAVASCRIPT,
            '.ts': CodeLanguage.TYPESCRIPT,
            '.java': CodeLanguage.JAVA,
            '.cpp': CodeLanguage.CPP,
            '.c': CodeLanguage.CPP,
            '.cs': CodeLanguage.CSHARP,
            '.go': CodeLanguage.GO,
            '.rs': CodeLanguage.RUST,
            '.sql': CodeLanguage.SQL,
            '.html': CodeLanguage.HTML,
            '.htm': CodeLanguage.HTML,
            '.css': CodeLanguage.CSS,
            '.sh': CodeLanguage.SHELL,
            '.bash': CodeLanguage.SHELL
        }
        
        return language_map.get(ext, CodeLanguage.OTHER)
        
    def save(self) -> bool:
        """Save changes to the file"""
        try:
            with open(self.file_path, 'w') as f:
                f.write(self.content)
            return True
        except Exception as e:
            logger.error(f"Error saving file {self.file_path}: {str(e)}")
            return False
            
    def apply_edit(self, edit: CodeEdit) -> bool:
        """Apply an edit to the file"""
        try:
            self.content = edit.apply(self.content)
            return True
        except Exception as e:
            logger.error(f"Error applying edit to {self.file_path}: {str(e)}")
            return False
            
    def get_lines(self, start: int, end: Optional[int] = None) -> List[str]:
        """Get specific lines from the file"""
        lines = self.content.splitlines()
        
        if end is None:
            end = start + 1
            
        return lines[start:end]
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "file_path": self.file_path,
            "language": self.language.value,
            "size_bytes": len(self.content) if self.content else 0,
            "line_count": len(self.content.splitlines()) if self.content else 0
        }


class CodebaseAnalyzer:
    """Analyzes a codebase for understanding"""
    
    def __init__(self, root_path: str):
        self.root_path = root_path
        
    def list_files(self, extension: Optional[str] = None) -> List[str]:
        """List all files in the codebase, optionally filtered by extension"""
        result = []
        
        for root, _, files in os.walk(self.root_path):
            for file in files:
                if extension is None or file.endswith(extension):
                    file_path = os.path.join(root, file)
                    result.append(file_path)
                    
        return result
        
    def find_references(self, term: str) -> List[Dict[str, Any]]:
        """Find all references to a term in the codebase"""
        result = []
        
        for file_path in self.list_files():
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    
                if term in content:
                    # Find line numbers
                    lines = content.splitlines()
                    for i, line in enumerate(lines):
                        if term in line:
                            result.append({
                                "file_path": file_path,
                                "line_number": i + 1,
                                "line": line
                            })
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {str(e)}")
                
        return result
        
    def analyze_complexity(self, file_path: str) -> Dict[str, Any]:
        """Analyze the complexity of a file"""
        try:
            code_file = CodeFile(file_path)
            
            # In a real implementation, this would use language-specific tools
            # For this example, we'll provide a simple analysis
            
            lines = code_file.content.splitlines()
            line_count = len(lines)
            blank_lines = sum(1 for line in lines if not line.strip())
            comment_lines = sum(1 for line in lines if line.strip().startswith('#') or line.strip().startswith('//'))
            
            # Extremely simple complexity metric: number of control flow statements
            control_flow_count = 0
            if code_file.language == CodeLanguage.PYTHON:
                control_flow_keywords = ['if', 'else', 'elif', 'for', 'while', 'try', 'except']
                control_flow_count = sum(1 for line in lines if any(f' {kw} ' in f' {line} ' for kw in control_flow_keywords))
                
            return {
                "file_path": file_path,
                "language": code_file.language.value,
                "line_count": line_count,
                "blank_lines": blank_lines,
                "comment_lines": comment_lines,
                "code_lines": line_count - blank_lines - comment_lines,
                "complexity_score": control_flow_count,
                "avg_line_length": sum(len(line) for line in lines) / max(line_count, 1)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing complexity of {file_path}: {str(e)}")
            return {
                "file_path": file_path,
                "error": str(e)
            }
            
    def get_dependencies(self, file_path: str) -> Dict[str, Any]:
        """Get the dependencies of a file"""
        try:
            code_file = CodeFile(file_path)
            
            # In a real implementation, this would use language-specific parsing
            # For this example, we'll focus on Python imports
            
            if code_file.language == CodeLanguage.PYTHON:
                imports = []
                for line in code_file.content.splitlines():
                    line = line.strip()
                    if line.startswith('import ') or line.startswith('from '):
                        imports.append(line)
                        
                return {
                    "file_path": file_path,
                    "language": code_file.language.value,
                    "imports": imports
                }
                
            return {
                "file_path": file_path,
                "language": code_file.language.value,
                "dependencies": []
            }
            
        except Exception as e:
            logger.error(f"Error getting dependencies of {file_path}: {str(e)}")
            return {
                "file_path": file_path,
                "error": str(e)
            }
            
    def generate_summary(self) -> Dict[str, Any]:
        """Generate a summary of the codebase"""
        language_counts = {}
        file_count = 0
        total_lines = 0
        
        for file_path in self.list_files():
            try:
                file_count += 1
                code_file = CodeFile(file_path)
                
                # Count lines
                if code_file.content:
                    lines = len(code_file.content.splitlines())
                    total_lines += lines
                    
                # Count languages
                lang = code_file.language.value
                language_counts[lang] = language_counts.get(lang, 0) + 1
                
            except Exception:
                # Skip files that can't be read
                pass
                
        return {
            "root_path": self.root_path,
            "file_count": file_count,
            "total_lines": total_lines,
            "languages": language_counts
        }


class DeveloperTools:
    """Main class for managing developer tools"""
    
    def __init__(self):
        self.code_generators = {}
        self.code_edits: Dict[str, CodeEdit] = {}
        self.git_operations: Dict[str, GitOperation] = {}
        self.code_generation_requests: Dict[str, CodeGenerationRequest] = {}
        
    def generate_code(self, prompt: str, language: CodeLanguage, 
                     model_name: Optional[str] = None,
                     context: Optional[Dict[str, Any]] = None,
                     parameters: Optional[Dict[str, Any]] = None) -> str:
        """Generate code based on a prompt"""
        request = CodeGenerationRequest(prompt, language, model_name)
        
        if context:
            for key, value in context.items():
                request.add_context(key, value)
                
        if parameters:
            request.set_parameters(parameters)
            
        # Store the request
        self.code_generation_requests[request.id] = request
        
        try:
            # In a real implementation, this would call an LLM API
            # For this example, we'll simulate code generation
            
            # Processing status
            request.status = "processing"
            
            # Generate dummy code based on the language
            if language == CodeLanguage.PYTHON:
                code = f"""def generated_function(x, y):
    \"\"\"
    Generated function based on: {prompt}
    \"\"\"
    # TODO: Implement the actual functionality
    result = x + y
    return result
    
# Example usage
if __name__ == "__main__":
    print(generated_function(5, 10))
"""
            elif language in [CodeLanguage.JAVASCRIPT, CodeLanguage.TYPESCRIPT]:
                code = f"""/**
 * Generated function based on: {prompt}
 */
function generatedFunction(x, y) {
    // TODO: Implement the actual functionality
    const result = x + y;
    return result;
}

// Example usage
console.log(generatedFunction(5, 10));
"""
            elif language == CodeLanguage.JAVA:
                code = f"""/**
 * Generated class based on: {prompt}
 */
public class GeneratedClass {{
    /**
     * Generated method
     */
    public int generatedMethod(int x, int y) {{
        // TODO: Implement the actual functionality
        int result = x + y;
        return result;
    }}
    
    // Example usage
    public static void main(String[] args) {{
        GeneratedClass instance = new GeneratedClass();
        System.out.println(instance.generatedMethod(5, 10));
    }}
}}
"""
            else:
                code = f"// Generated code for {language.value} based on: {prompt}\n// TODO: Implement"
                
            # Set result
            request.set_result({
                "code": code,
                "language": language.value,
                "explanation": f"Generated code based on prompt: {prompt}"
            })
            
            return request.id
            
        except Exception as e:
            logger.error(f"Error generating code: {str(e)}")
            request.set_failure(str(e))
            return request.id
            
    def get_generation_result(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get the result of a code generation request"""
        request = self.code_generation_requests.get(request_id)
        if not request:
            return None
            
        return request.to_dict()
        
    def create_code_edit(self, file_path: str) -> str:
        """Create a new code edit for a file"""
        edit = CodeEdit(file_path)
        self.code_edits[edit.id] = edit
        return edit.id
        
    def add_edit_operation(self, edit_id: str, operation_type: str, 
                          **params) -> bool:
        """Add an edit operation to a code edit"""
        edit = self.code_edits.get(edit_id)
        if not edit:
            return False
            
        try:
            if operation_type == "insertion":
                edit.add_insertion(params["position"], params["content"])
            elif operation_type == "deletion":
                edit.add_deletion(params["start"], params["end"])
            elif operation_type == "replacement":
                edit.add_replacement(params["start"], params["end"], params["content"])
            else:
                return False
                
            return True
            
        except KeyError:
            logger.error(f"Missing required parameters for {operation_type} operation")
            return False
            
    def apply_edit(self, edit_id: str, file_path: Optional[str] = None) -> bool:
        """Apply a code edit to a file"""
        edit = self.code_edits.get(edit_id)
        if not edit:
            return False
            
        # Use the edit's file path if none is provided
        if not file_path:
            file_path = edit.file_path
            
        try:
            code_file = CodeFile(file_path)
            result = code_file.apply_edit(edit)
            
            if result:
                return code_file.save()
                
            return False
            
        except Exception as e:
            logger.error(f"Error applying edit: {str(e)}")
            return False
            
    def create_git_operation(self, operation_type: str, repository_path: str) -> str:
        """Create a new Git operation"""
        operation = GitOperation(operation_type, repository_path)
        self.git_operations[operation.id] = operation
        return operation.id
        
    def set_git_operation_params(self, operation_id: str, params: Dict[str, Any]) -> bool:
        """Set parameters for a Git operation"""
        operation = self.git_operations.get(operation_id)
        if not operation:
            return False
            
        operation.set_params(params)
        return True
        
    def execute_git_operation(self, operation_id: str) -> bool:
        """Execute a Git operation"""
        operation = self.git_operations.get(operation_id)
        if not operation:
            return False
            
        return operation.execute()
        
    def get_git_operation_result(self, operation_id: str) -> Optional[Dict[str, Any]]:
        """Get the result of a Git operation"""
        operation = self.git_operations.get(operation_id)
        if not operation:
            return None
            
        return operation.to_dict()
        
    def analyze_codebase(self, root_path: str) -> Dict[str, Any]:
        """Analyze a codebase"""
        analyzer = CodebaseAnalyzer(root_path)
        return analyzer.generate_summary()
        
    def find_references(self, root_path: str, term: str) -> List[Dict[str, Any]]:
        """Find references to a term in a codebase"""
        analyzer = CodebaseAnalyzer(root_path)
        return analyzer.find_references(term)
        
    def analyze_file_complexity(self, file_path: str) -> Dict[str, Any]:
        """Analyze the complexity of a file"""
        analyzer = CodebaseAnalyzer(os.path.dirname(file_path))
        return analyzer.analyze_complexity(file_path)
        
    def get_file_dependencies(self, file_path: str) -> Dict[str, Any]:
        """Get the dependencies of a file"""
        analyzer = CodebaseAnalyzer(os.path.dirname(file_path))
        return analyzer.get_dependencies(file_path)


# Example usage
if __name__ == "__main__":
    # Create developer tools
    dev_tools = DeveloperTools()
    
    # Generate code
    request_id = dev_tools.generate_code(
        "Create a function to calculate the monthly payment for a mortgage",
        CodeLanguage.PYTHON,
        "gpt-4",
        {"interest_rate": 0.04, "years": 30},
        {"temperature": 0.7}
    )
    print(f"Code generation request: {request_id}")
    
    # Get generation result
    result = dev_tools.get_generation_result(request_id)
    print("\nGenerated code:")
    if result and result["status"] == "completed":
        print(result["result"]["code"])
        
    # Create a temporary Python file for editing
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as temp:
        temp.write("""def add(a, b):
    return a + b
    
def subtract(a, b):
    return a - b
    
# Example usage
print(add(5, 3))
print(subtract(10, 4))
""")
        file_path = temp.name
        
    try:
        # Create a code edit
        edit_id = dev_tools.create_code_edit(file_path)
        print(f"\nCreated code edit: {edit_id}")
        
        # Add edit operations
        dev_tools.add_edit_operation(
            edit_id,
            "insertion",
            position=0,
            content="# Math operations module\n\n"
        )
        
        dev_tools.add_edit_operation(
            edit_id,
            "replacement",
            start=47,  # Start of second function
            end=75,    # End of second function
            content="def subtract(a, b):\n    # Enhanced subtraction function\n    return a - b\n"
        )
        
        # Apply the edit
        success = dev_tools.apply_edit(edit_id)
        print(f"Edit applied: {success}")
        
        # Read the edited file
        with open(file_path, "r") as f:
            edited_content = f.read()
            
        print("\nEdited file content:")
        print(edited_content)
        
        # Analyze file complexity
        complexity = dev_tools.analyze_file_complexity(file_path)
        print("\nFile complexity:")
        for key, value in complexity.items():
            print(f"- {key}: {value}")
            
    finally:
        # Clean up the temporary file
        os.unlink(file_path)
        
    # Git operations example (using a temp directory as the repo)
    with tempfile.TemporaryDirectory() as temp_dir:
        # Initialize a git repo
        subprocess.run(["git", "init"], cwd=temp_dir, capture_output=True)
        
        # Create a test file
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("Test content")
            
        # Create and execute git operations
        status_id = dev_tools.create_git_operation("status", temp_dir)
        dev_tools.execute_git_operation(status_id)
        status_result = dev_tools.get_git_operation_result(status_id)
        
        print("\nGit status result:")
        print(status_result["result"])
        
        # Add and commit
        commit_id = dev_tools.create_git_operation("commit", temp_dir)
        dev_tools.set_git_operation_params(commit_id, {
            "message": "Initial commit",
            "add_all": True
        })
        dev_tools.execute_git_operation(commit_id)
        
        commit_result = dev_tools.get_git_operation_result(commit_id)
        print("\nGit commit result:")
        print(commit_result["result"])