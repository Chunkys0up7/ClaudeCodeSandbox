#!/usr/bin/env python3
"""
Collaboration Tools Module for AI App Store Workspaces

This module provides functionality for team communication, collaboration,
and project management within workspaces.
"""

import enum
import uuid
import logging
import datetime
import json
from typing import Dict, List, Any, Optional, Union, Callable

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ItemType(enum.Enum):
    """Enum representing types of collaboration items"""
    TASK = "task"
    NOTE = "note"
    COMMENT = "comment"
    FILE = "file"
    EVENT = "event"
    POLL = "poll"
    CUSTOM = "custom"


class Priority(enum.Enum):
    """Enum representing task priorities"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Status(enum.Enum):
    """Enum representing item statuses"""
    NEW = "new"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    ARCHIVED = "archived"


class Task:
    """Represents a task in a collaboration space"""
    
    def __init__(self, title: str, description: str, created_by: str):
        self.id = str(uuid.uuid4())
        self.title = title
        self.description = description
        self.created_by = created_by
        self.assignees = []
        self.status = Status.NEW
        self.priority = Priority.MEDIUM
        self.due_date = None
        self.comments = []
        self.tags = []
        self.attachments = []
        self.created_at = datetime.datetime.utcnow()
        self.updated_at = self.created_at
        self.completed_at = None
        
    def add_assignee(self, user_id: str) -> None:
        """Add an assignee to the task"""
        if user_id not in self.assignees:
            self.assignees.append(user_id)
            self.updated_at = datetime.datetime.utcnow()
            
    def remove_assignee(self, user_id: str) -> bool:
        """Remove an assignee from the task"""
        if user_id in self.assignees:
            self.assignees.remove(user_id)
            self.updated_at = datetime.datetime.utcnow()
            return True
        return False
        
    def set_status(self, status: Status) -> None:
        """Update the task status"""
        self.status = status
        self.updated_at = datetime.datetime.utcnow()
        
        if status == Status.COMPLETED and not self.completed_at:
            self.completed_at = self.updated_at
            
    def set_priority(self, priority: Priority) -> None:
        """Update the task priority"""
        self.priority = priority
        self.updated_at = datetime.datetime.utcnow()
        
    def set_due_date(self, due_date: datetime.datetime) -> None:
        """Set the due date for the task"""
        self.due_date = due_date
        self.updated_at = datetime.datetime.utcnow()
        
    def add_comment(self, user_id: str, content: str) -> str:
        """Add a comment to the task"""
        comment_id = str(uuid.uuid4())
        self.comments.append({
            "id": comment_id,
            "user_id": user_id,
            "content": content,
            "created_at": datetime.datetime.utcnow().isoformat()
        })
        self.updated_at = datetime.datetime.utcnow()
        return comment_id
        
    def add_tag(self, tag: str) -> None:
        """Add a tag to the task"""
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.datetime.utcnow()
            
    def remove_tag(self, tag: str) -> bool:
        """Remove a tag from the task"""
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.datetime.utcnow()
            return True
        return False
        
    def add_attachment(self, name: str, file_type: str, url: str, 
                      size: Optional[int] = None) -> str:
        """Add an attachment to the task"""
        attachment_id = str(uuid.uuid4())
        self.attachments.append({
            "id": attachment_id,
            "name": name,
            "file_type": file_type,
            "url": url,
            "size": size,
            "uploaded_at": datetime.datetime.utcnow().isoformat()
        })
        self.updated_at = datetime.datetime.utcnow()
        return attachment_id
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "created_by": self.created_by,
            "assignees": self.assignees,
            "status": self.status.value,
            "priority": self.priority.value,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "comments": self.comments,
            "tags": self.tags,
            "attachments": self.attachments,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


class Note:
    """Represents a shared note in a collaboration space"""
    
    def __init__(self, title: str, content: str, created_by: str):
        self.id = str(uuid.uuid4())
        self.title = title
        self.content = content
        self.created_by = created_by
        self.editors = [created_by]
        self.viewers = []
        self.comments = []
        self.tags = []
        self.created_at = datetime.datetime.utcnow()
        self.updated_at = self.created_at
        self.edit_history = [{
            "user_id": created_by,
            "timestamp": self.created_at.isoformat(),
            "action": "created"
        }]
        
    def update_content(self, user_id: str, content: str) -> bool:
        """Update the note content"""
        if user_id not in self.editors:
            return False
            
        self.content = content
        self.updated_at = datetime.datetime.utcnow()
        
        self.edit_history.append({
            "user_id": user_id,
            "timestamp": self.updated_at.isoformat(),
            "action": "updated"
        })
        
        return True
        
    def add_editor(self, user_id: str) -> None:
        """Add a user who can edit the note"""
        if user_id not in self.editors:
            self.editors.append(user_id)
            
            # Remove from viewers if present
            if user_id in self.viewers:
                self.viewers.remove(user_id)
                
            self.updated_at = datetime.datetime.utcnow()
            
    def add_viewer(self, user_id: str) -> None:
        """Add a user who can view the note"""
        if user_id not in self.editors and user_id not in self.viewers:
            self.viewers.append(user_id)
            self.updated_at = datetime.datetime.utcnow()
            
    def remove_access(self, user_id: str) -> bool:
        """Remove a user's access to the note"""
        updated = False
        
        if user_id in self.editors:
            self.editors.remove(user_id)
            updated = True
            
        if user_id in self.viewers:
            self.viewers.remove(user_id)
            updated = True
            
        if updated:
            self.updated_at = datetime.datetime.utcnow()
            
        return updated
        
    def add_comment(self, user_id: str, content: str) -> Optional[str]:
        """Add a comment to the note"""
        if user_id not in self.editors and user_id not in self.viewers:
            return None
            
        comment_id = str(uuid.uuid4())
        self.comments.append({
            "id": comment_id,
            "user_id": user_id,
            "content": content,
            "created_at": datetime.datetime.utcnow().isoformat()
        })
        self.updated_at = datetime.datetime.utcnow()
        return comment_id
        
    def add_tag(self, tag: str) -> None:
        """Add a tag to the note"""
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.datetime.utcnow()
            
    def remove_tag(self, tag: str) -> bool:
        """Remove a tag from the note"""
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.datetime.utcnow()
            return True
        return False
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "created_by": self.created_by,
            "editors": self.editors,
            "viewers": self.viewers,
            "comments": self.comments,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "edit_history": self.edit_history
        }


class Event:
    """Represents a scheduled event in a collaboration space"""
    
    def __init__(self, title: str, description: str, start_time: datetime.datetime, 
                created_by: str, end_time: Optional[datetime.datetime] = None):
        self.id = str(uuid.uuid4())
        self.title = title
        self.description = description
        self.start_time = start_time
        self.end_time = end_time
        self.created_by = created_by
        self.location = None
        self.attendees = []
        self.responses = {}  # user_id -> response (accepted, declined, tentative)
        self.is_recurring = False
        self.recurrence_pattern = None
        self.reminders = []
        self.attachments = []
        self.created_at = datetime.datetime.utcnow()
        self.updated_at = self.created_at
        
    def set_location(self, location: Dict[str, Any]) -> None:
        """Set the event location"""
        self.location = location
        self.updated_at = datetime.datetime.utcnow()
        
    def add_attendee(self, user_id: str, required: bool = True) -> None:
        """Add an attendee to the event"""
        if user_id not in [a["user_id"] for a in self.attendees]:
            self.attendees.append({
                "user_id": user_id,
                "required": required,
                "added_at": datetime.datetime.utcnow().isoformat()
            })
            self.updated_at = datetime.datetime.utcnow()
            
    def remove_attendee(self, user_id: str) -> bool:
        """Remove an attendee from the event"""
        for i, attendee in enumerate(self.attendees):
            if attendee["user_id"] == user_id:
                self.attendees.pop(i)
                
                # Remove response if exists
                if user_id in self.responses:
                    del self.responses[user_id]
                    
                self.updated_at = datetime.datetime.utcnow()
                return True
                
        return False
        
    def set_attendee_response(self, user_id: str, response: str) -> bool:
        """Set an attendee's response to the event"""
        valid_responses = ["accepted", "declined", "tentative"]
        
        if response not in valid_responses:
            return False
            
        attendee_ids = [a["user_id"] for a in self.attendees]
        if user_id not in attendee_ids:
            return False
            
        self.responses[user_id] = {
            "response": response,
            "updated_at": datetime.datetime.utcnow().isoformat()
        }
        self.updated_at = datetime.datetime.utcnow()
        return True
        
    def set_recurrence(self, is_recurring: bool, pattern: Optional[Dict[str, Any]] = None) -> None:
        """Set the event recurrence pattern"""
        self.is_recurring = is_recurring
        self.recurrence_pattern = pattern
        self.updated_at = datetime.datetime.utcnow()
        
    def add_reminder(self, time_before: int, unit: str) -> str:
        """Add a reminder for the event"""
        reminder_id = str(uuid.uuid4())
        
        self.reminders.append({
            "id": reminder_id,
            "time_before": time_before,
            "unit": unit,  # minutes, hours, days
            "created_at": datetime.datetime.utcnow().isoformat()
        })
        
        self.updated_at = datetime.datetime.utcnow()
        return reminder_id
        
    def remove_reminder(self, reminder_id: str) -> bool:
        """Remove a reminder from the event"""
        for i, reminder in enumerate(self.reminders):
            if reminder["id"] == reminder_id:
                self.reminders.pop(i)
                self.updated_at = datetime.datetime.utcnow()
                return True
                
        return False
        
    def add_attachment(self, name: str, file_type: str, url: str, 
                      size: Optional[int] = None) -> str:
        """Add an attachment to the event"""
        attachment_id = str(uuid.uuid4())
        
        self.attachments.append({
            "id": attachment_id,
            "name": name,
            "file_type": file_type,
            "url": url,
            "size": size,
            "uploaded_at": datetime.datetime.utcnow().isoformat()
        })
        
        self.updated_at = datetime.datetime.utcnow()
        return attachment_id
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "created_by": self.created_by,
            "location": self.location,
            "attendees": self.attendees,
            "responses": self.responses,
            "is_recurring": self.is_recurring,
            "recurrence_pattern": self.recurrence_pattern,
            "reminders": self.reminders,
            "attachments": self.attachments,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class Poll:
    """Represents a poll in a collaboration space"""
    
    def __init__(self, question: str, options: List[str], created_by: str,
                multi_select: bool = False, anonymous: bool = False):
        self.id = str(uuid.uuid4())
        self.question = question
        self.options = [{"id": str(uuid.uuid4()), "text": opt} for opt in options]
        self.created_by = created_by
        self.multi_select = multi_select
        self.anonymous = anonymous
        self.responses = {}  # user_id -> [option_ids] or option_id
        self.is_closed = False
        self.end_time = None
        self.created_at = datetime.datetime.utcnow()
        self.updated_at = self.created_at
        self.closed_at = None
        
    def add_option(self, option_text: str) -> str:
        """Add an option to the poll"""
        option_id = str(uuid.uuid4())
        
        self.options.append({
            "id": option_id,
            "text": option_text
        })
        
        self.updated_at = datetime.datetime.utcnow()
        return option_id
        
    def remove_option(self, option_id: str) -> bool:
        """Remove an option from the poll"""
        for i, option in enumerate(self.options):
            if option["id"] == option_id:
                self.options.pop(i)
                
                # Remove responses for this option
                for user_id, response in self.responses.items():
                    if self.multi_select:
                        if option_id in response:
                            self.responses[user_id].remove(option_id)
                    elif response == option_id:
                        del self.responses[user_id]
                        
                self.updated_at = datetime.datetime.utcnow()
                return True
                
        return False
        
    def add_response(self, user_id: str, option_id: Union[str, List[str]]) -> bool:
        """Add a response to the poll"""
        if self.is_closed:
            return False
            
        # Validate option_id
        valid_option_ids = [opt["id"] for opt in self.options]
        
        if self.multi_select:
            if not isinstance(option_id, list):
                option_id = [option_id]
                
            for opt_id in option_id:
                if opt_id not in valid_option_ids:
                    return False
                    
            self.responses[user_id] = option_id
            
        else:
            if isinstance(option_id, list):
                option_id = option_id[0]
                
            if option_id not in valid_option_ids:
                return False
                
            self.responses[user_id] = option_id
            
        self.updated_at = datetime.datetime.utcnow()
        return True
        
    def set_end_time(self, end_time: datetime.datetime) -> None:
        """Set the end time for the poll"""
        self.end_time = end_time
        self.updated_at = datetime.datetime.utcnow()
        
    def close(self) -> None:
        """Close the poll"""
        self.is_closed = True
        self.closed_at = datetime.datetime.utcnow()
        self.updated_at = self.closed_at
        
    def get_results(self) -> Dict[str, Any]:
        """Get the poll results"""
        results = {}
        
        for option in self.options:
            option_id = option["id"]
            count = 0
            
            if self.multi_select:
                for response in self.responses.values():
                    if option_id in response:
                        count += 1
            else:
                count = list(self.responses.values()).count(option_id)
                
            results[option_id] = {
                "text": option["text"],
                "count": count
            }
            
        total_respondents = len(self.responses)
        
        # Calculate percentages
        if total_respondents > 0:
            for option_id, result in results.items():
                result["percentage"] = (result["count"] / total_respondents) * 100
                
        return {
            "options": results,
            "total_respondents": total_respondents,
            "is_closed": self.is_closed
        }
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        poll_dict = {
            "id": self.id,
            "question": self.question,
            "options": self.options,
            "created_by": self.created_by,
            "multi_select": self.multi_select,
            "anonymous": self.anonymous,
            "is_closed": self.is_closed,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "closed_at": self.closed_at.isoformat() if self.closed_at else None
        }
        
        if not self.anonymous:
            poll_dict["responses"] = self.responses
            
        return poll_dict


class CollaborationSpace:
    """Represents a collaboration space within a workspace"""
    
    def __init__(self, name: str, description: str, created_by: str):
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.created_by = created_by
        self.members = [created_by]  # List of user IDs
        self.tasks: Dict[str, Task] = {}
        self.notes: Dict[str, Note] = {}
        self.events: Dict[str, Event] = {}
        self.polls: Dict[str, Poll] = {}
        self.tags = []
        self.created_at = datetime.datetime.utcnow()
        self.updated_at = self.created_at
        
    def add_member(self, user_id: str) -> None:
        """Add a member to the collaboration space"""
        if user_id not in self.members:
            self.members.append(user_id)
            self.updated_at = datetime.datetime.utcnow()
            
    def remove_member(self, user_id: str) -> bool:
        """Remove a member from the collaboration space"""
        if user_id in self.members:
            self.members.remove(user_id)
            self.updated_at = datetime.datetime.utcnow()
            return True
        return False
        
    def add_task(self, task: Task) -> None:
        """Add a task to the collaboration space"""
        self.tasks[task.id] = task
        self.updated_at = datetime.datetime.utcnow()
        
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID"""
        return self.tasks.get(task_id)
        
    def add_note(self, note: Note) -> None:
        """Add a note to the collaboration space"""
        self.notes[note.id] = note
        self.updated_at = datetime.datetime.utcnow()
        
    def get_note(self, note_id: str) -> Optional[Note]:
        """Get a note by ID"""
        return self.notes.get(note_id)
        
    def add_event(self, event: Event) -> None:
        """Add an event to the collaboration space"""
        self.events[event.id] = event
        self.updated_at = datetime.datetime.utcnow()
        
    def get_event(self, event_id: str) -> Optional[Event]:
        """Get an event by ID"""
        return self.events.get(event_id)
        
    def add_poll(self, poll: Poll) -> None:
        """Add a poll to the collaboration space"""
        self.polls[poll.id] = poll
        self.updated_at = datetime.datetime.utcnow()
        
    def get_poll(self, poll_id: str) -> Optional[Poll]:
        """Get a poll by ID"""
        return self.polls.get(poll_id)
        
    def add_tag(self, tag: str) -> None:
        """Add a tag to the collaboration space"""
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.datetime.utcnow()
            
    def remove_tag(self, tag: str) -> bool:
        """Remove a tag from the collaboration space"""
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.datetime.utcnow()
            return True
        return False
        
    def get_items_by_tag(self, tag: str) -> Dict[str, List[Dict[str, Any]]]:
        """Get all items with a specific tag"""
        result = {
            "tasks": [],
            "notes": [],
            "events": [],
            "polls": []
        }
        
        for task in self.tasks.values():
            if tag in task.tags:
                result["tasks"].append(task.to_dict())
                
        for note in self.notes.values():
            if tag in note.tags:
                result["notes"].append(note.to_dict())
                
        # Events and polls don't have tags in this model
        
        return result
        
    def get_user_items(self, user_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """Get all items associated with a user"""
        result = {
            "tasks": [],
            "notes": [],
            "events": [],
            "polls": []
        }
        
        # Tasks assigned to user
        for task in self.tasks.values():
            if user_id in task.assignees:
                result["tasks"].append(task.to_dict())
                
        # Notes user can edit or view
        for note in self.notes.values():
            if user_id in note.editors or user_id in note.viewers:
                result["notes"].append(note.to_dict())
                
        # Events user is attending
        for event in self.events.values():
            if user_id in [a["user_id"] for a in event.attendees]:
                result["events"].append(event.to_dict())
                
        # Polls user has responded to
        for poll in self.polls.values():
            if user_id in poll.responses:
                result["polls"].append(poll.to_dict())
                
        return result
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_by": self.created_by,
            "members": self.members,
            "task_count": len(self.tasks),
            "note_count": len(self.notes),
            "event_count": len(self.events),
            "poll_count": len(self.polls),
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class CollaborationManager:
    """Main class for managing collaboration tools"""
    
    def __init__(self):
        self.spaces: Dict[str, CollaborationSpace] = {}
        
    def create_space(self, name: str, description: str, created_by: str) -> str:
        """Create a new collaboration space"""
        space = CollaborationSpace(name, description, created_by)
        self.spaces[space.id] = space
        return space.id
        
    def get_space(self, space_id: str) -> Optional[CollaborationSpace]:
        """Get a collaboration space by ID"""
        return self.spaces.get(space_id)
        
    def list_spaces(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List collaboration spaces, optionally filtered by user membership"""
        result = []
        
        for space in self.spaces.values():
            if user_id is None or user_id in space.members:
                result.append(space.to_dict())
                
        return result
        
    def add_member(self, space_id: str, user_id: str) -> bool:
        """Add a member to a collaboration space"""
        space = self.spaces.get(space_id)
        if not space:
            return False
            
        space.add_member(user_id)
        return True
        
    def create_task(self, space_id: str, title: str, description: str, 
                   created_by: str) -> Optional[str]:
        """Create a new task in a collaboration space"""
        space = self.spaces.get(space_id)
        if not space or created_by not in space.members:
            return None
            
        task = Task(title, description, created_by)
        space.add_task(task)
        return task.id
        
    def update_task(self, space_id: str, task_id: str, 
                   updates: Dict[str, Any], user_id: str) -> bool:
        """Update a task in a collaboration space"""
        space = self.spaces.get(space_id)
        if not space or user_id not in space.members:
            return False
            
        task = space.get_task(task_id)
        if not task:
            return False
            
        # Apply updates
        for key, value in updates.items():
            if key == "title":
                task.title = value
            elif key == "description":
                task.description = value
            elif key == "status":
                try:
                    task.set_status(Status(value))
                except ValueError:
                    continue
            elif key == "priority":
                try:
                    task.set_priority(Priority(value))
                except ValueError:
                    continue
            elif key == "due_date":
                try:
                    task.set_due_date(datetime.datetime.fromisoformat(value))
                except (ValueError, TypeError):
                    continue
            elif key == "assignees":
                # Replace all assignees
                if isinstance(value, list):
                    task.assignees = []
                    for assignee in value:
                        task.add_assignee(assignee)
                        
        task.updated_at = datetime.datetime.utcnow()
        return True
        
    def create_note(self, space_id: str, title: str, content: str, 
                   created_by: str) -> Optional[str]:
        """Create a new note in a collaboration space"""
        space = self.spaces.get(space_id)
        if not space or created_by not in space.members:
            return None
            
        note = Note(title, content, created_by)
        space.add_note(note)
        return note.id
        
    def create_event(self, space_id: str, title: str, description: str,
                    start_time: datetime.datetime, created_by: str,
                    end_time: Optional[datetime.datetime] = None) -> Optional[str]:
        """Create a new event in a collaboration space"""
        space = self.spaces.get(space_id)
        if not space or created_by not in space.members:
            return None
            
        event = Event(title, description, start_time, created_by, end_time)
        space.add_event(event)
        return event.id
        
    def create_poll(self, space_id: str, question: str, options: List[str],
                   created_by: str, multi_select: bool = False,
                   anonymous: bool = False) -> Optional[str]:
        """Create a new poll in a collaboration space"""
        space = self.spaces.get(space_id)
        if not space or created_by not in space.members:
            return None
            
        poll = Poll(question, options, created_by, multi_select, anonymous)
        space.add_poll(poll)
        return poll.id
        
    def respond_to_poll(self, space_id: str, poll_id: str, 
                       user_id: str, option_id: Union[str, List[str]]) -> bool:
        """Add a response to a poll"""
        space = self.spaces.get(space_id)
        if not space or user_id not in space.members:
            return False
            
        poll = space.get_poll(poll_id)
        if not poll:
            return False
            
        return poll.add_response(user_id, option_id)
        
    def get_poll_results(self, space_id: str, poll_id: str) -> Optional[Dict[str, Any]]:
        """Get the results of a poll"""
        space = self.spaces.get(space_id)
        if not space:
            return None
            
        poll = space.get_poll(poll_id)
        if not poll:
            return None
            
        results = poll.get_results()
        results["poll_id"] = poll_id
        results["question"] = poll.question
        
        return results
        
    def get_user_tasks(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all tasks assigned to a user across all spaces"""
        tasks = []
        
        for space in self.spaces.values():
            if user_id in space.members:
                for task in space.tasks.values():
                    if user_id in task.assignees:
                        task_dict = task.to_dict()
                        task_dict["space_id"] = space.id
                        task_dict["space_name"] = space.name
                        tasks.append(task_dict)
                        
        return tasks
        
    def get_upcoming_events(self, user_id: str, days: int = 7) -> List[Dict[str, Any]]:
        """Get upcoming events for a user within the specified number of days"""
        events = []
        now = datetime.datetime.utcnow()
        end_date = now + datetime.timedelta(days=days)
        
        for space in self.spaces.values():
            if user_id in space.members:
                for event in space.events.values():
                    if now <= event.start_time <= end_date and user_id in [a["user_id"] for a in event.attendees]:
                        event_dict = event.to_dict()
                        event_dict["space_id"] = space.id
                        event_dict["space_name"] = space.name
                        events.append(event_dict)
                        
        # Sort by start time
        events.sort(key=lambda e: e["start_time"])
        return events


# Example usage
if __name__ == "__main__":
    # Create collaboration manager
    manager = CollaborationManager()
    
    # Create a collaboration space
    user_id = "user-123"
    space_id = manager.create_space(
        "Loan Processing Team",
        "Collaboration space for the loan processing team",
        user_id
    )
    print(f"Created collaboration space: {space_id}")
    
    # Add members
    manager.add_member(space_id, "user-456")
    manager.add_member(space_id, "user-789")
    
    # Create a task
    task_id = manager.create_task(
        space_id,
        "Update loan processing documentation",
        "Update the documentation to reflect the new process changes",
        user_id
    )
    print(f"Created task: {task_id}")
    
    # Update the task
    manager.update_task(
        space_id,
        task_id,
        {
            "priority": "high",
            "status": "in_progress",
            "assignees": ["user-456", "user-789"],
            "due_date": (datetime.datetime.utcnow() + datetime.timedelta(days=7)).isoformat()
        },
        user_id
    )
    
    # Create a note
    note_id = manager.create_note(
        space_id,
        "Process Improvement Ideas",
        "Here are some ideas for improving our loan processing workflow...",
        user_id
    )
    print(f"Created note: {note_id}")
    
    # Create an event
    start_time = datetime.datetime.utcnow() + datetime.timedelta(days=2)
    end_time = start_time + datetime.timedelta(hours=1)
    
    event_id = manager.create_event(
        space_id,
        "Loan Processing Team Meeting",
        "Weekly team meeting to discuss progress and blockers",
        start_time,
        user_id,
        end_time
    )
    print(f"Created event: {event_id}")
    
    # Create a poll
    poll_id = manager.create_poll(
        space_id,
        "What's the best day for our weekly meetings?",
        ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        user_id
    )
    print(f"Created poll: {poll_id}")
    
    # Add responses to the poll
    manager.respond_to_poll(space_id, poll_id, user_id, "Monday")
    manager.respond_to_poll(space_id, poll_id, "user-456", "Wednesday")
    manager.respond_to_poll(space_id, poll_id, "user-789", "Wednesday")
    
    # Get poll results
    results = manager.get_poll_results(space_id, poll_id)
    print("\nPoll results:")
    for option_id, result in results["options"].items():
        print(f"- {result['text']}: {result['count']} votes ({result.get('percentage', 0):.1f}%)")
        
    # Get user tasks
    tasks = manager.get_user_tasks("user-456")
    print(f"\nUser-456 has {len(tasks)} assigned tasks")
    
    # Get upcoming events
    events = manager.get_upcoming_events(user_id)
    print(f"\nUpcoming events for user-123: {len(events)}")