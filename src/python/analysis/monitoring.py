#!/usr/bin/env python3
"""
Monitoring Module for the AI App Store

This module provides functionality for monitoring and analyzing AI application
usage, performance, costs, and user interactions.
"""

import enum
import uuid
import logging
import datetime
import json
from typing import Dict, List, Any, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EventType(enum.Enum):
    """Enum representing the possible event types for monitoring"""
    APP_START = "app_start"
    APP_STOP = "app_stop"
    MODEL_INVOKE = "model_invoke"
    USER_INTERACTION = "user_interaction"
    ERROR = "error"
    WARNING = "warning"
    PERFORMANCE_METRIC = "performance_metric"
    COST_METRIC = "cost_metric"
    CUSTOM = "custom"


class Event:
    """Represents a single monitoring event"""
    
    def __init__(self, app_id: str, event_type: EventType, data: Dict[str, Any],
                user_id: Optional[str] = None):
        self.id = str(uuid.uuid4())
        self.app_id = app_id
        self.event_type = event_type
        self.data = data
        self.user_id = user_id
        self.timestamp = datetime.datetime.utcnow()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "app_id": self.app_id,
            "event_type": self.event_type.value,
            "data": self.data,
            "user_id": self.user_id,
            "timestamp": self.timestamp.isoformat()
        }


class WorkflowTrace:
    """Represents a trace of a workflow execution"""
    
    def __init__(self, app_id: str, workflow_id: str, user_id: Optional[str] = None):
        self.id = str(uuid.uuid4())
        self.app_id = app_id
        self.workflow_id = workflow_id
        self.user_id = user_id
        self.events: List[Event] = []
        self.annotations: Dict[str, Any] = {}
        self.started_at = datetime.datetime.utcnow()
        self.completed_at = None
        self.status = "running"  # running, completed, failed
        
    def add_event(self, event: Event) -> None:
        """Add an event to the trace"""
        self.events.append(event)
        
    def add_annotation(self, key: str, value: Any) -> None:
        """Add an annotation to the trace"""
        self.annotations[key] = value
        
    def complete(self, success: bool = True) -> None:
        """Mark the trace as complete"""
        self.status = "completed" if success else "failed"
        self.completed_at = datetime.datetime.utcnow()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "app_id": self.app_id,
            "workflow_id": self.workflow_id,
            "user_id": self.user_id,
            "events": [event.to_dict() for event in self.events],
            "annotations": self.annotations,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "status": self.status
        }


class CostRecord:
    """Represents a record of costs incurred"""
    
    def __init__(self, app_id: str, component_id: str, amount: float, currency: str = "USD"):
        self.id = str(uuid.uuid4())
        self.app_id = app_id
        self.component_id = component_id
        self.amount = amount
        self.currency = currency
        self.timestamp = datetime.datetime.utcnow()
        self.details = {}
        
    def set_details(self, details: Dict[str, Any]) -> None:
        """Set detailed cost information"""
        self.details = details
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "app_id": self.app_id,
            "component_id": self.component_id,
            "amount": self.amount,
            "currency": self.currency,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details
        }


class UsageMetric:
    """Represents a usage metric for an app"""
    
    def __init__(self, app_id: str, metric_name: str, value: float):
        self.id = str(uuid.uuid4())
        self.app_id = app_id
        self.metric_name = metric_name
        self.value = value
        self.timestamp = datetime.datetime.utcnow()
        self.dimensions = {}
        
    def add_dimension(self, key: str, value: str) -> None:
        """Add a dimension to the metric"""
        self.dimensions[key] = value
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "app_id": self.app_id,
            "metric_name": self.metric_name,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "dimensions": self.dimensions
        }


class PerformanceMetric:
    """Represents a performance metric for an app"""
    
    def __init__(self, app_id: str, component_id: str, metric_name: str, value: float):
        self.id = str(uuid.uuid4())
        self.app_id = app_id
        self.component_id = component_id
        self.metric_name = metric_name
        self.value = value
        self.timestamp = datetime.datetime.utcnow()
        self.dimensions = {}
        
    def add_dimension(self, key: str, value: str) -> None:
        """Add a dimension to the metric"""
        self.dimensions[key] = value
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "app_id": self.app_id,
            "component_id": self.component_id,
            "metric_name": self.metric_name,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "dimensions": self.dimensions
        }


class UserInteractionLog:
    """Represents a log of user interactions with an app"""
    
    def __init__(self, app_id: str, user_id: str, interaction_type: str, data: Dict[str, Any]):
        self.id = str(uuid.uuid4())
        self.app_id = app_id
        self.user_id = user_id
        self.interaction_type = interaction_type
        self.data = data
        self.timestamp = datetime.datetime.utcnow()
        self.session_id = None
        
    def set_session_id(self, session_id: str) -> None:
        """Set the session ID for this interaction"""
        self.session_id = session_id
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "app_id": self.app_id,
            "user_id": self.user_id,
            "interaction_type": self.interaction_type,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "session_id": self.session_id
        }


class MonitoringDashboard:
    """Represents a monitoring dashboard configuration"""
    
    def __init__(self, name: str, app_id: Optional[str] = None):
        self.id = str(uuid.uuid4())
        self.name = name
        self.app_id = app_id  # If None, this is a cross-app dashboard
        self.widgets = []
        self.created_at = datetime.datetime.utcnow()
        self.updated_at = self.created_at
        
    def add_widget(self, widget_type: str, title: str, data_source: Dict[str, Any],
                 position: Dict[str, int], size: Dict[str, int]) -> None:
        """Add a widget to the dashboard"""
        self.widgets.append({
            "id": str(uuid.uuid4()),
            "widget_type": widget_type,
            "title": title,
            "data_source": data_source,
            "position": position,
            "size": size
        })
        self.updated_at = datetime.datetime.utcnow()
        
    def update_widget(self, widget_id: str, title: Optional[str] = None,
                     data_source: Optional[Dict[str, Any]] = None,
                     position: Optional[Dict[str, int]] = None,
                     size: Optional[Dict[str, int]] = None) -> bool:
        """Update a widget in the dashboard"""
        for widget in self.widgets:
            if widget["id"] == widget_id:
                if title is not None:
                    widget["title"] = title
                if data_source is not None:
                    widget["data_source"] = data_source
                if position is not None:
                    widget["position"] = position
                if size is not None:
                    widget["size"] = size
                self.updated_at = datetime.datetime.utcnow()
                return True
        return False
        
    def remove_widget(self, widget_id: str) -> bool:
        """Remove a widget from the dashboard"""
        for i, widget in enumerate(self.widgets):
            if widget["id"] == widget_id:
                self.widgets.pop(i)
                self.updated_at = datetime.datetime.utcnow()
                return True
        return False
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "name": self.name,
            "app_id": self.app_id,
            "widgets": self.widgets,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class Alert:
    """Represents an alert configuration"""
    
    def __init__(self, name: str, app_id: str, metric_name: str, condition: str, threshold: float):
        self.id = str(uuid.uuid4())
        self.name = name
        self.app_id = app_id
        self.metric_name = metric_name
        self.condition = condition  # greater_than, less_than, equal_to
        self.threshold = threshold
        self.enabled = True
        self.notification_channels = []
        self.last_triggered = None
        self.created_at = datetime.datetime.utcnow()
        self.updated_at = self.created_at
        
    def add_notification_channel(self, channel_type: str, configuration: Dict[str, Any]) -> None:
        """Add a notification channel for the alert"""
        self.notification_channels.append({
            "id": str(uuid.uuid4()),
            "channel_type": channel_type,
            "configuration": configuration
        })
        self.updated_at = datetime.datetime.utcnow()
        
    def remove_notification_channel(self, channel_id: str) -> bool:
        """Remove a notification channel from the alert"""
        for i, channel in enumerate(self.notification_channels):
            if channel["id"] == channel_id:
                self.notification_channels.pop(i)
                self.updated_at = datetime.datetime.utcnow()
                return True
        return False
        
    def trigger(self) -> None:
        """Mark the alert as triggered"""
        self.last_triggered = datetime.datetime.utcnow()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "name": self.name,
            "app_id": self.app_id,
            "metric_name": self.metric_name,
            "condition": self.condition,
            "threshold": self.threshold,
            "enabled": self.enabled,
            "notification_channels": self.notification_channels,
            "last_triggered": self.last_triggered.isoformat() if self.last_triggered else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class MonitoringManager:
    """Main class for managing app monitoring and analysis"""
    
    def __init__(self):
        self.events: List[Event] = []
        self.workflow_traces: Dict[str, WorkflowTrace] = {}
        self.cost_records: List[CostRecord] = []
        self.usage_metrics: List[UsageMetric] = []
        self.performance_metrics: List[PerformanceMetric] = []
        self.user_interactions: List[UserInteractionLog] = []
        self.dashboards: Dict[str, MonitoringDashboard] = {}
        self.alerts: Dict[str, Alert] = {}
        
        # Initialize default dashboards
        self._create_default_dashboards()
        
    def _create_default_dashboards(self) -> None:
        """Create default monitoring dashboards"""
        # Overall usage dashboard
        usage_dashboard = MonitoringDashboard("Overall Usage")
        
        # Add widgets
        usage_dashboard.add_widget(
            "line_chart",
            "Daily Active Users",
            {
                "metric": "active_users",
                "aggregation": "daily"
            },
            {"x": 0, "y": 0},
            {"width": 6, "height": 4}
        )
        
        usage_dashboard.add_widget(
            "bar_chart",
            "App Usage by Department",
            {
                "metric": "app_usage",
                "dimension": "department"
            },
            {"x": 6, "y": 0},
            {"width": 6, "height": 4}
        )
        
        usage_dashboard.add_widget(
            "metric",
            "Total App Count",
            {
                "metric": "app_count"
            },
            {"x": 0, "y": 4},
            {"width": 3, "height": 2}
        )
        
        usage_dashboard.add_widget(
            "metric",
            "Total User Count",
            {
                "metric": "user_count"
            },
            {"x": 3, "y": 4},
            {"width": 3, "height": 2}
        )
        
        usage_dashboard.add_widget(
            "table",
            "Top 10 Apps by Usage",
            {
                "metric": "app_usage",
                "limit": 10,
                "order": "desc"
            },
            {"x": 6, "y": 4},
            {"width": 6, "height": 6}
        )
        
        self.dashboards[usage_dashboard.id] = usage_dashboard
        
        # Cost analysis dashboard
        cost_dashboard = MonitoringDashboard("Cost Analysis")
        
        cost_dashboard.add_widget(
            "line_chart",
            "Daily Cost by Model Type",
            {
                "metric": "cost",
                "dimension": "model_type",
                "aggregation": "daily"
            },
            {"x": 0, "y": 0},
            {"width": 12, "height": 4}
        )
        
        cost_dashboard.add_widget(
            "pie_chart",
            "Cost Distribution by App",
            {
                "metric": "cost",
                "dimension": "app_id"
            },
            {"x": 0, "y": 4},
            {"width": 6, "height": 6}
        )
        
        cost_dashboard.add_widget(
            "bar_chart",
            "Top 5 Most Expensive Apps",
            {
                "metric": "cost",
                "dimension": "app_id",
                "limit": 5,
                "order": "desc"
            },
            {"x": 6, "y": 4},
            {"width": 6, "height": 6}
        )
        
        self.dashboards[cost_dashboard.id] = cost_dashboard
        
    def record_event(self, app_id: str, event_type: EventType, data: Dict[str, Any],
                    user_id: Optional[str] = None) -> str:
        """Record a monitoring event"""
        event = Event(app_id, event_type, data, user_id)
        self.events.append(event)
        
        # If there's an active trace for this app and user, add the event to it
        for trace in self.workflow_traces.values():
            if (trace.app_id == app_id and 
                trace.status == "running" and 
                (trace.user_id is None or trace.user_id == user_id)):
                trace.add_event(event)
                
        return event.id
        
    def start_workflow_trace(self, app_id: str, workflow_id: str, 
                           user_id: Optional[str] = None) -> str:
        """Start a new workflow trace"""
        trace = WorkflowTrace(app_id, workflow_id, user_id)
        self.workflow_traces[trace.id] = trace
        return trace.id
        
    def complete_workflow_trace(self, trace_id: str, success: bool = True) -> bool:
        """Complete a workflow trace"""
        if trace_id not in self.workflow_traces:
            return False
            
        trace = self.workflow_traces[trace_id]
        trace.complete(success)
        return True
        
    def get_workflow_trace(self, trace_id: str) -> Optional[WorkflowTrace]:
        """Get a workflow trace by ID"""
        return self.workflow_traces.get(trace_id)
        
    def list_workflow_traces(self, app_id: Optional[str] = None, 
                           user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List workflow traces, optionally filtered by app ID and/or user ID"""
        result = []
        
        for trace in self.workflow_traces.values():
            if ((app_id is None or trace.app_id == app_id) and 
                (user_id is None or trace.user_id == user_id)):
                result.append(trace.to_dict())
                
        return result
        
    def record_cost(self, app_id: str, component_id: str, amount: float,
                   currency: str = "USD", details: Dict[str, Any] = None) -> str:
        """Record a cost incurred by an app"""
        record = CostRecord(app_id, component_id, amount, currency)
        
        if details:
            record.set_details(details)
            
        self.cost_records.append(record)
        return record.id
        
    def record_usage_metric(self, app_id: str, metric_name: str, value: float,
                           dimensions: Dict[str, str] = None) -> str:
        """Record a usage metric"""
        metric = UsageMetric(app_id, metric_name, value)
        
        if dimensions:
            for key, value in dimensions.items():
                metric.add_dimension(key, value)
                
        self.usage_metrics.append(metric)
        
        # Check if this metric triggers any alerts
        self._check_alerts(app_id, metric_name, value)
        
        return metric.id
        
    def record_performance_metric(self, app_id: str, component_id: str,
                                metric_name: str, value: float,
                                dimensions: Dict[str, str] = None) -> str:
        """Record a performance metric"""
        metric = PerformanceMetric(app_id, component_id, metric_name, value)
        
        if dimensions:
            for key, value in dimensions.items():
                metric.add_dimension(key, value)
                
        self.performance_metrics.append(metric)
        
        # Check if this metric triggers any alerts
        self._check_alerts(app_id, metric_name, value)
        
        return metric.id
        
    def record_user_interaction(self, app_id: str, user_id: str, interaction_type: str,
                              data: Dict[str, Any], session_id: Optional[str] = None) -> str:
        """Record a user interaction"""
        interaction = UserInteractionLog(app_id, user_id, interaction_type, data)
        
        if session_id:
            interaction.set_session_id(session_id)
            
        self.user_interactions.append(interaction)
        return interaction.id
        
    def create_dashboard(self, name: str, app_id: Optional[str] = None) -> MonitoringDashboard:
        """Create a new monitoring dashboard"""
        dashboard = MonitoringDashboard(name, app_id)
        self.dashboards[dashboard.id] = dashboard
        return dashboard
        
    def get_dashboard(self, dashboard_id: str) -> Optional[MonitoringDashboard]:
        """Get a dashboard by ID"""
        return self.dashboards.get(dashboard_id)
        
    def list_dashboards(self, app_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List dashboards, optionally filtered by app ID"""
        result = []
        
        for dashboard in self.dashboards.values():
            if app_id is None or dashboard.app_id == app_id or dashboard.app_id is None:
                result.append(dashboard.to_dict())
                
        return result
        
    def create_alert(self, name: str, app_id: str, metric_name: str,
                    condition: str, threshold: float) -> Alert:
        """Create a new alert"""
        alert = Alert(name, app_id, metric_name, condition, threshold)
        self.alerts[alert.id] = alert
        return alert
        
    def get_alert(self, alert_id: str) -> Optional[Alert]:
        """Get an alert by ID"""
        return self.alerts.get(alert_id)
        
    def list_alerts(self, app_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List alerts, optionally filtered by app ID"""
        result = []
        
        for alert in self.alerts.values():
            if app_id is None or alert.app_id == app_id:
                result.append(alert.to_dict())
                
        return result
        
    def _check_alerts(self, app_id: str, metric_name: str, value: float) -> None:
        """Check if a metric triggers any alerts"""
        for alert in self.alerts.values():
            if (alert.app_id == app_id and 
                alert.metric_name == metric_name and 
                alert.enabled):
                
                triggered = False
                
                if alert.condition == "greater_than" and value > alert.threshold:
                    triggered = True
                elif alert.condition == "less_than" and value < alert.threshold:
                    triggered = True
                elif alert.condition == "equal_to" and value == alert.threshold:
                    triggered = True
                    
                if triggered:
                    alert.trigger()
                    self._send_alert_notifications(alert, value)
                    
    def _send_alert_notifications(self, alert: Alert, value: float) -> None:
        """Send notifications for a triggered alert"""
        for channel in alert.notification_channels:
            logger.info(f"Sending alert notification: {alert.name} - value: {value} to {channel['channel_type']}")
            # In a real implementation, this would send the notification via the specified channel
            
    def get_app_cost_summary(self, app_id: str, 
                            start_date: Optional[datetime.datetime] = None,
                            end_date: Optional[datetime.datetime] = None) -> Dict[str, Any]:
        """Get a summary of costs for an app"""
        records = []
        
        for record in self.cost_records:
            if record.app_id != app_id:
                continue
                
            if start_date and record.timestamp < start_date:
                continue
                
            if end_date and record.timestamp > end_date:
                continue
                
            records.append(record)
            
        total_cost = sum(record.amount for record in records)
        
        # Group by component
        component_costs = {}
        for record in records:
            if record.component_id not in component_costs:
                component_costs[record.component_id] = 0
            component_costs[record.component_id] += record.amount
            
        return {
            "app_id": app_id,
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
            "total_cost": total_cost,
            "component_costs": component_costs,
            "record_count": len(records)
        }
        
    def get_app_usage_summary(self, app_id: str,
                            start_date: Optional[datetime.datetime] = None,
                            end_date: Optional[datetime.datetime] = None) -> Dict[str, Any]:
        """Get a summary of usage for an app"""
        interactions = []
        
        for interaction in self.user_interactions:
            if interaction.app_id != app_id:
                continue
                
            if start_date and interaction.timestamp < start_date:
                continue
                
            if end_date and interaction.timestamp > end_date:
                continue
                
            interactions.append(interaction)
            
        # Count unique users
        users = set(interaction.user_id for interaction in interactions)
        
        # Group by interaction type
        interaction_types = {}
        for interaction in interactions:
            if interaction.interaction_type not in interaction_types:
                interaction_types[interaction.interaction_type] = 0
            interaction_types[interaction.interaction_type] += 1
            
        return {
            "app_id": app_id,
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
            "total_interactions": len(interactions),
            "unique_users": len(users),
            "interaction_types": interaction_types
        }
        
    def get_app_performance_summary(self, app_id: str,
                                  start_date: Optional[datetime.datetime] = None,
                                  end_date: Optional[datetime.datetime] = None) -> Dict[str, Any]:
        """Get a summary of performance for an app"""
        metrics = []
        
        for metric in self.performance_metrics:
            if metric.app_id != app_id:
                continue
                
            if start_date and metric.timestamp < start_date:
                continue
                
            if end_date and metric.timestamp > end_date:
                continue
                
            metrics.append(metric)
            
        # Group by metric name
        metric_summaries = {}
        for metric in metrics:
            if metric.metric_name not in metric_summaries:
                metric_summaries[metric.metric_name] = {
                    "count": 0,
                    "sum": 0,
                    "min": float('inf'),
                    "max": float('-inf')
                }
                
            summary = metric_summaries[metric.metric_name]
            summary["count"] += 1
            summary["sum"] += metric.value
            summary["min"] = min(summary["min"], metric.value)
            summary["max"] = max(summary["max"], metric.value)
            
        # Calculate averages
        for name, summary in metric_summaries.items():
            if summary["count"] > 0:
                summary["avg"] = summary["sum"] / summary["count"]
            else:
                summary["avg"] = 0
                
            # Remove infinity values if no metrics were found
            if summary["min"] == float('inf'):
                summary["min"] = 0
            if summary["max"] == float('-inf'):
                summary["max"] = 0
                
        return {
            "app_id": app_id,
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
            "metric_count": len(metrics),
            "metric_summaries": metric_summaries
        }


# Example usage
if __name__ == "__main__":
    # Create monitoring manager
    manager = MonitoringManager()
    
    # Record some events and metrics
    app_id = "app-123"
    component_id = "model-456"
    user_id = "user-789"
    
    # Record an app start event
    event_id = manager.record_event(
        app_id, 
        EventType.APP_START, 
        {"version": "1.0.0", "environment": "production"}, 
        user_id
    )
    print(f"Recorded event: {event_id}")
    
    # Start a workflow trace
    workflow_id = "workflow-123"
    trace_id = manager.start_workflow_trace(app_id, workflow_id, user_id)
    print(f"Started workflow trace: {trace_id}")
    
    # Record a model invocation event
    model_event_id = manager.record_event(
        app_id,
        EventType.MODEL_INVOKE,
        {
            "model_id": "gpt-4",
            "input_tokens": 150,
            "output_tokens": 80,
            "latency_ms": 2500
        },
        user_id
    )
    print(f"Recorded model event: {model_event_id}")
    
    # Record a cost
    cost_id = manager.record_cost(
        app_id,
        component_id,
        0.15,
        "USD",
        {
            "input_tokens": 150,
            "output_tokens": 80,
            "input_cost": 0.05,
            "output_cost": 0.10
        }
    )
    print(f"Recorded cost: {cost_id}")
    
    # Record a performance metric
    perf_id = manager.record_performance_metric(
        app_id,
        component_id,
        "response_time",
        2500,
        {"unit": "ms", "endpoint": "/api/analyze"}
    )
    print(f"Recorded performance metric: {perf_id}")
    
    # Record a user interaction
    interaction_id = manager.record_user_interaction(
        app_id,
        user_id,
        "query",
        {"query": "How to calculate mortgage rates", "results_count": 5}
    )
    print(f"Recorded user interaction: {interaction_id}")
    
    # Complete the workflow trace
    manager.complete_workflow_trace(trace_id)
    print("Completed workflow trace")
    
    # Get a cost summary
    cost_summary = manager.get_app_cost_summary(app_id)
    print(f"Cost summary: Total cost: ${cost_summary['total_cost']}")
    
    # Get usage summary
    usage_summary = manager.get_app_usage_summary(app_id)
    print(f"Usage summary: {usage_summary['total_interactions']} interactions by {usage_summary['unique_users']} users")
    
    # Get performance summary
    perf_summary = manager.get_app_performance_summary(app_id)
    print("Performance summary:")
    for name, summary in perf_summary["metric_summaries"].items():
        print(f"- {name}: avg={summary['avg']}, min={summary['min']}, max={summary['max']}")