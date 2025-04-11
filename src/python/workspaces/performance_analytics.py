#!/usr/bin/env python3
"""
Performance Analytics Module for AI App Store Workspaces

This module provides functionality for monitoring workspace performance,
analyzing workflow efficiency, and generating performance reports to help
users optimize their workflows and make data-driven decisions.
"""

import uuid
import logging
import datetime
import json
import statistics
from typing import Dict, List, Any, Optional, Set, Union, Tuple, Callable
import enum
import time
import threading
import math
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MetricType(enum.Enum):
    """Enum representing types of performance metrics"""
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    RESOURCE_USAGE = "resource_usage"
    SUCCESS_RATE = "success_rate"
    COST = "cost"
    CUSTOM = "custom"


class ResourceType(enum.Enum):
    """Enum representing resource types for metrics"""
    WORKSPACE = "workspace"
    APP = "app"
    WORKFLOW = "workflow"
    MODEL = "model"
    FUNCTION = "function"
    INTEGRATION = "integration"
    CUSTOM = "custom"


class TimeInterval(enum.Enum):
    """Enum representing time intervals for aggregation"""
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    CUSTOM = "custom"


class MetricDataPoint:
    """Represents a single data point for a metric"""
    
    def __init__(self, metric_id: str, value: float, timestamp: Optional[datetime.datetime] = None):
        self.id = str(uuid.uuid4())
        self.metric_id = metric_id
        self.value = value
        self.timestamp = timestamp or datetime.datetime.utcnow()
        self.tags = {}
        
    def add_tag(self, key: str, value: str) -> None:
        """Add a tag to the data point"""
        self.tags[key] = value
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "metric_id": self.metric_id,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "tags": self.tags
        }


class Metric:
    """Represents a performance metric"""
    
    def __init__(self, name: str, type: MetricType, resource_type: ResourceType, 
                resource_id: str, unit: str = "", description: str = ""):
        self.id = str(uuid.uuid4())
        self.name = name
        self.type = type
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.unit = unit
        self.description = description
        self.created_at = datetime.datetime.utcnow()
        self.data_points: List[MetricDataPoint] = []
        self.aggregations = {}
        
    def add_data_point(self, value: float, tags: Optional[Dict[str, str]] = None,
                    timestamp: Optional[datetime.datetime] = None) -> str:
        """Add a data point to the metric"""
        data_point = MetricDataPoint(self.id, value, timestamp)
        
        if tags:
            for key, value in tags.items():
                data_point.add_tag(key, value)
                
        self.data_points.append(data_point)
        return data_point.id
        
    def get_data_points(self, start_time: Optional[datetime.datetime] = None,
                      end_time: Optional[datetime.datetime] = None,
                      tags: Optional[Dict[str, str]] = None) -> List[MetricDataPoint]:
        """Get filtered data points"""
        result = []
        
        for point in self.data_points:
            # Apply time filters
            if start_time and point.timestamp < start_time:
                continue
                
            if end_time and point.timestamp > end_time:
                continue
                
            # Apply tag filters
            if tags:
                match = True
                for key, value in tags.items():
                    if key not in point.tags or point.tags[key] != value:
                        match = False
                        break
                        
                if not match:
                    continue
                    
            result.append(point)
            
        return result
        
    def calculate_statistics(self, start_time: Optional[datetime.datetime] = None,
                           end_time: Optional[datetime.datetime] = None,
                           tags: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Calculate statistics for the metric data points"""
        data_points = self.get_data_points(start_time, end_time, tags)
        
        if not data_points:
            return {
                "count": 0,
                "min": None,
                "max": None,
                "sum": None,
                "mean": None,
                "median": None,
                "stddev": None,
                "p95": None,
                "p99": None
            }
            
        values = [point.value for point in data_points]
        
        # Calculate percentiles
        values_sorted = sorted(values)
        p95_index = int(len(values) * 0.95)
        p99_index = int(len(values) * 0.99)
        
        # Calculate statistics
        stats = {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "sum": sum(values),
            "mean": statistics.mean(values) if values else None,
            "median": statistics.median(values) if values else None,
            "stddev": statistics.stdev(values) if len(values) > 1 else 0,
            "p95": values_sorted[p95_index] if p95_index < len(values) else values_sorted[-1],
            "p99": values_sorted[p99_index] if p99_index < len(values) else values_sorted[-1]
        }
        
        return stats
        
    def aggregate_by_interval(self, interval: TimeInterval, 
                            start_time: Optional[datetime.datetime] = None,
                            end_time: Optional[datetime.datetime] = None,
                            aggregation_function: str = "avg") -> Dict[str, Any]:
        """Aggregate data points by time interval"""
        data_points = self.get_data_points(start_time, end_time)
        
        if not data_points:
            return {"intervals": []}
            
        # Default to last 24 hours if no time range specified
        if not start_time and not end_time:
            end_time = datetime.datetime.utcnow()
            start_time = end_time - datetime.timedelta(days=1)
            
        if not start_time:
            start_time = min(point.timestamp for point in data_points)
            
        if not end_time:
            end_time = max(point.timestamp for point in data_points)
            
        # Generate time intervals
        intervals = []
        current_time = start_time
        
        while current_time < end_time:
            next_time = None
            
            if interval == TimeInterval.MINUTE:
                next_time = current_time + datetime.timedelta(minutes=1)
            elif interval == TimeInterval.HOUR:
                next_time = current_time + datetime.timedelta(hours=1)
            elif interval == TimeInterval.DAY:
                next_time = current_time + datetime.timedelta(days=1)
            elif interval == TimeInterval.WEEK:
                next_time = current_time + datetime.timedelta(weeks=1)
            elif interval == TimeInterval.MONTH:
                # Approximate a month as 30 days
                next_time = current_time + datetime.timedelta(days=30)
            else:
                # Default to hourly
                next_time = current_time + datetime.timedelta(hours=1)
                
            intervals.append((current_time, next_time))
            current_time = next_time
            
        # Aggregate data points into intervals
        result = {"intervals": []}
        
        for interval_start, interval_end in intervals:
            interval_points = [
                point for point in data_points 
                if interval_start <= point.timestamp < interval_end
            ]
            
            if not interval_points:
                result["intervals"].append({
                    "start_time": interval_start.isoformat(),
                    "end_time": interval_end.isoformat(),
                    "count": 0,
                    "value": None
                })
                continue
                
            values = [point.value for point in interval_points]
            
            # Calculate the aggregated value
            agg_value = None
            
            if aggregation_function == "avg" and values:
                agg_value = statistics.mean(values)
            elif aggregation_function == "sum":
                agg_value = sum(values)
            elif aggregation_function == "min" and values:
                agg_value = min(values)
            elif aggregation_function == "max" and values:
                agg_value = max(values)
            elif aggregation_function == "count":
                agg_value = len(values)
                
            result["intervals"].append({
                "start_time": interval_start.isoformat(),
                "end_time": interval_end.isoformat(),
                "count": len(values),
                "value": agg_value
            })
            
        return result
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "resource_type": self.resource_type.value,
            "resource_id": self.resource_id,
            "unit": self.unit,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "data_point_count": len(self.data_points)
        }


class Alert:
    """Represents a performance alert"""
    
    def __init__(self, name: str, metric_id: str, condition: str, 
                threshold: float, window_minutes: int = 5):
        self.id = str(uuid.uuid4())
        self.name = name
        self.metric_id = metric_id
        self.condition = condition  # gt, lt, gte, lte
        self.threshold = threshold
        self.window_minutes = window_minutes
        self.enabled = True
        self.created_at = datetime.datetime.utcnow()
        self.last_triggered = None
        self.actions = []
        
    def add_action(self, action_type: str, config: Dict[str, Any]) -> str:
        """Add an action to be triggered by the alert"""
        action_id = str(uuid.uuid4())
        
        action = {
            "id": action_id,
            "type": action_type,
            "config": config,
            "created_at": datetime.datetime.utcnow().isoformat()
        }
        
        self.actions.append(action)
        return action_id
        
    def evaluate(self, metric: Metric) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Evaluate if the alert should be triggered"""
        if not self.enabled:
            return False, None
            
        end_time = datetime.datetime.utcnow()
        start_time = end_time - datetime.timedelta(minutes=self.window_minutes)
        
        # Get recent data points
        points = metric.get_data_points(start_time, end_time)
        
        if not points:
            return False, None
            
        # Calculate the aggregate value over the window
        values = [point.value for point in points]
        agg_value = statistics.mean(values)
        
        # Check condition
        triggered = False
        
        if self.condition == "gt" and agg_value > self.threshold:
            triggered = True
        elif self.condition == "lt" and agg_value < self.threshold:
            triggered = True
        elif self.condition == "gte" and agg_value >= self.threshold:
            triggered = True
        elif self.condition == "lte" and agg_value <= self.threshold:
            triggered = True
            
        if triggered:
            self.last_triggered = datetime.datetime.utcnow()
            
            return True, {
                "alert_id": self.id,
                "alert_name": self.name,
                "metric_id": self.metric_id,
                "condition": self.condition,
                "threshold": self.threshold,
                "actual_value": agg_value,
                "window_minutes": self.window_minutes,
                "triggered_at": self.last_triggered.isoformat()
            }
            
        return False, None
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "name": self.name,
            "metric_id": self.metric_id,
            "condition": self.condition,
            "threshold": self.threshold,
            "window_minutes": self.window_minutes,
            "enabled": self.enabled,
            "created_at": self.created_at.isoformat(),
            "last_triggered": self.last_triggered.isoformat() if self.last_triggered else None,
            "actions": self.actions
        }


class PerformanceReport:
    """Represents a performance report"""
    
    def __init__(self, name: str, description: str, resource_type: ResourceType, resource_id: str):
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.created_at = datetime.datetime.utcnow()
        self.updated_at = self.created_at
        self.sections = []
        self.metrics = []
        self.schedule = None
        
    def add_metric(self, metric_id: str) -> None:
        """Add a metric to the report"""
        if metric_id not in self.metrics:
            self.metrics.append(metric_id)
            self.updated_at = datetime.datetime.utcnow()
            
    def add_section(self, title: str, content: str) -> str:
        """Add a section to the report"""
        section_id = str(uuid.uuid4())
        
        section = {
            "id": section_id,
            "title": title,
            "content": content,
            "created_at": datetime.datetime.utcnow().isoformat()
        }
        
        self.sections.append(section)
        self.updated_at = datetime.datetime.utcnow()
        return section_id
        
    def set_schedule(self, interval: str, day: Optional[int] = None, 
                    hour: Optional[int] = None, minute: Optional[int] = None) -> None:
        """Set a schedule for the report generation"""
        self.schedule = {
            "interval": interval,  # daily, weekly, monthly
            "day": day,  # Day of week (0-6) or day of month (1-31)
            "hour": hour,
            "minute": minute,
            "created_at": datetime.datetime.utcnow().isoformat(),
            "next_run": self._calculate_next_run(interval, day, hour, minute)
        }
        
        self.updated_at = datetime.datetime.utcnow()
        
    def _calculate_next_run(self, interval: str, day: Optional[int], 
                         hour: Optional[int], minute: Optional[int]) -> str:
        """Calculate the next run time based on the schedule"""
        now = datetime.datetime.utcnow()
        next_run = now
        
        # Set minute
        if minute is not None:
            next_run = next_run.replace(minute=minute, second=0, microsecond=0)
        else:
            next_run = next_run.replace(minute=0, second=0, microsecond=0)
            
        # Set hour
        if hour is not None:
            next_run = next_run.replace(hour=hour)
        else:
            next_run = next_run.replace(hour=0)
            
        # Handle different intervals
        if interval == "daily":
            # If the calculated time is in the past, move to the next day
            if next_run <= now:
                next_run = next_run + datetime.timedelta(days=1)
                
        elif interval == "weekly":
            # Set day of week
            days_ahead = day - next_run.weekday()
            if days_ahead <= 0:  # Target day already happened this week
                days_ahead += 7
                
            next_run = next_run + datetime.timedelta(days=days_ahead)
            
        elif interval == "monthly":
            # Set day of month
            if day is not None:
                # Get the last day of the current month
                current_month = next_run.month
                current_year = next_run.year
                last_day = self._get_last_day_of_month(current_year, current_month)
                
                # If the day is beyond the last day of the month, use the last day
                target_day = min(day, last_day)
                
                # Try to set the day
                try:
                    next_run = next_run.replace(day=target_day)
                except ValueError:
                    # Handle case where target day doesn't exist in this month
                    next_run = next_run.replace(day=last_day)
                    
                # If the calculated time is in the past, move to the next month
                if next_run <= now:
                    if current_month == 12:
                        next_month = 1
                        next_year = current_year + 1
                    else:
                        next_month = current_month + 1
                        next_year = current_year
                        
                    last_day = self._get_last_day_of_month(next_year, next_month)
                    target_day = min(day, last_day)
                    
                    next_run = next_run.replace(year=next_year, month=next_month, day=target_day)
                    
        return next_run.isoformat()
        
    def _get_last_day_of_month(self, year: int, month: int) -> int:
        """Get the last day of a month"""
        if month == 12:
            last_day = datetime.datetime(year + 1, 1, 1) - datetime.timedelta(days=1)
        else:
            last_day = datetime.datetime(year, month + 1, 1) - datetime.timedelta(days=1)
            
        return last_day.day
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "resource_type": self.resource_type.value,
            "resource_id": self.resource_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "sections": self.sections,
            "metrics": self.metrics,
            "schedule": self.schedule
        }


class WorkflowAnalyzer:
    """Analyzes workflow performance and efficiency"""
    
    def __init__(self, workflow_id: str):
        self.workflow_id = workflow_id
        self.execution_times = []
        self.step_times = {}
        self.failure_points = {}
        self.resources_used = {}
        
    def add_execution(self, execution_id: str, start_time: datetime.datetime, 
                    end_time: Optional[datetime.datetime] = None, 
                    status: str = "running",
                    step_data: Optional[Dict[str, Any]] = None) -> None:
        """Add a workflow execution record"""
        if end_time is None and status == "completed":
            end_time = datetime.datetime.utcnow()
            
        execution = {
            "id": execution_id,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat() if end_time else None,
            "status": status,
            "duration": (end_time - start_time).total_seconds() if end_time else None,
            "steps": step_data or {}
        }
        
        self.execution_times.append(execution)
        
        # Update step times
        if step_data:
            for step_id, step_info in step_data.items():
                if "duration" in step_info:
                    if step_id not in self.step_times:
                        self.step_times[step_id] = []
                    self.step_times[step_id].append(step_info["duration"])
                    
                # Track failures
                if step_info.get("status") == "failed":
                    if step_id not in self.failure_points:
                        self.failure_points[step_id] = 0
                    self.failure_points[step_id] += 1
                    
                # Track resource usage
                if "resources" in step_info:
                    for resource, usage in step_info["resources"].items():
                        if resource not in self.resources_used:
                            self.resources_used[resource] = []
                        self.resources_used[resource].append(usage)
                        
    def get_average_execution_time(self) -> Optional[float]:
        """Get the average execution time for the workflow"""
        durations = [
            execution["duration"] for execution in self.execution_times
            if execution["duration"] is not None
        ]
        
        if not durations:
            return None
            
        return statistics.mean(durations)
        
    def get_step_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for each workflow step"""
        result = {}
        
        for step_id, times in self.step_times.items():
            if not times:
                continue
                
            result[step_id] = {
                "count": len(times),
                "avg_duration": statistics.mean(times),
                "min_duration": min(times),
                "max_duration": max(times),
                "total_duration": sum(times),
                "failure_count": self.failure_points.get(step_id, 0)
            }
            
        return result
        
    def get_bottlenecks(self) -> List[Dict[str, Any]]:
        """Identify bottlenecks in the workflow"""
        bottlenecks = []
        step_stats = self.get_step_statistics()
        
        # Sort steps by average duration
        sorted_steps = sorted(
            step_stats.items(),
            key=lambda x: x[1]["avg_duration"],
            reverse=True
        )
        
        for step_id, stats in sorted_steps:
            bottlenecks.append({
                "step_id": step_id,
                "avg_duration": stats["avg_duration"],
                "failure_rate": stats["failure_count"] / stats["count"] if stats["count"] > 0 else 0,
                "bottleneck_score": stats["avg_duration"] * (1 + stats["failure_count"] / max(1, stats["count"]))
            })
            
        return bottlenecks
        
    def get_resource_usage(self) -> Dict[str, Dict[str, Any]]:
        """Get resource usage statistics"""
        result = {}
        
        for resource, usages in self.resources_used.items():
            if not usages:
                continue
                
            result[resource] = {
                "count": len(usages),
                "avg_usage": statistics.mean(usages),
                "min_usage": min(usages),
                "max_usage": max(usages),
                "total_usage": sum(usages)
            }
            
        return result
        
    def get_execution_success_rate(self) -> float:
        """Calculate the execution success rate"""
        if not self.execution_times:
            return 0.0
            
        successful = sum(
            1 for execution in self.execution_times
            if execution["status"] == "completed"
        )
        
        return successful / len(self.execution_times)
        
    def suggest_optimizations(self) -> List[Dict[str, Any]]:
        """Suggest optimizations to improve workflow performance"""
        suggestions = []
        bottlenecks = self.get_bottlenecks()
        
        # Suggest optimizations for top bottlenecks
        for bottleneck in bottlenecks[:3]:
            step_id = bottleneck["step_id"]
            failure_rate = bottleneck["failure_rate"]
            
            if failure_rate > 0.1:  # More than 10% failure rate
                suggestions.append({
                    "step_id": step_id,
                    "issue": "high_failure_rate",
                    "description": f"Step {step_id} has a high failure rate of {failure_rate:.2%}",
                    "suggestion": "Review error logs and add better error handling or retry logic"
                })
                
            suggestions.append({
                "step_id": step_id,
                "issue": "high_duration",
                "description": f"Step {step_id} takes {bottleneck['avg_duration']:.2f} seconds on average",
                "suggestion": "Consider optimizing this step or running it in parallel if possible"
            })
            
        # Check for resource usage optimizations
        resource_usage = self.get_resource_usage()
        for resource, stats in resource_usage.items():
            if stats["avg_usage"] > 80:  # More than 80% usage
                suggestions.append({
                    "resource": resource,
                    "issue": "high_resource_usage",
                    "description": f"Resource {resource} is used at {stats['avg_usage']:.2f}% on average",
                    "suggestion": "Consider allocating more resources or optimizing usage"
                })
                
        return suggestions
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "workflow_id": self.workflow_id,
            "execution_count": len(self.execution_times),
            "avg_execution_time": self.get_average_execution_time(),
            "success_rate": self.get_execution_success_rate(),
            "step_stats": self.get_step_statistics(),
            "bottlenecks": self.get_bottlenecks()[:3],
            "optimizations": self.suggest_optimizations()
        }


class PerformanceAnalyticsManager:
    """Main class for managing performance analytics"""
    
    def __init__(self):
        self.metrics: Dict[str, Metric] = {}
        self.alerts: Dict[str, Alert] = {}
        self.reports: Dict[str, PerformanceReport] = {}
        self.workflow_analyzers: Dict[str, WorkflowAnalyzer] = {}
        self.alert_thread = None
        self.alert_thread_running = False
        
    def create_metric(self, name: str, type: MetricType, resource_type: ResourceType,
                    resource_id: str, unit: str = "", description: str = "") -> str:
        """Create a new metric"""
        metric = Metric(name, type, resource_type, resource_id, unit, description)
        self.metrics[metric.id] = metric
        
        logger.info(f"Created metric: {name} ({metric.id})")
        return metric.id
        
    def get_metric(self, metric_id: str) -> Optional[Metric]:
        """Get a metric by ID"""
        return self.metrics.get(metric_id)
        
    def add_metric_data_point(self, metric_id: str, value: float, 
                           tags: Optional[Dict[str, str]] = None,
                           timestamp: Optional[datetime.datetime] = None) -> Optional[str]:
        """Add a data point to a metric"""
        metric = self.get_metric(metric_id)
        if not metric:
            logger.warning(f"Metric not found: {metric_id}")
            return None
            
        data_point_id = metric.add_data_point(value, tags, timestamp)
        return data_point_id
        
    def get_metric_statistics(self, metric_id: str, 
                            start_time: Optional[datetime.datetime] = None,
                            end_time: Optional[datetime.datetime] = None,
                            tags: Optional[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
        """Get statistics for a metric"""
        metric = self.get_metric(metric_id)
        if not metric:
            logger.warning(f"Metric not found: {metric_id}")
            return None
            
        return metric.calculate_statistics(start_time, end_time, tags)
        
    def aggregate_metric(self, metric_id: str, interval: TimeInterval,
                       start_time: Optional[datetime.datetime] = None,
                       end_time: Optional[datetime.datetime] = None,
                       aggregation_function: str = "avg") -> Optional[Dict[str, Any]]:
        """Aggregate a metric by time interval"""
        metric = self.get_metric(metric_id)
        if not metric:
            logger.warning(f"Metric not found: {metric_id}")
            return None
            
        return metric.aggregate_by_interval(
            interval, start_time, end_time, aggregation_function)
            
    def create_alert(self, name: str, metric_id: str, condition: str,
                  threshold: float, window_minutes: int = 5) -> Optional[str]:
        """Create a new alert"""
        if metric_id not in self.metrics:
            logger.warning(f"Metric not found: {metric_id}")
            return None
            
        alert = Alert(name, metric_id, condition, threshold, window_minutes)
        self.alerts[alert.id] = alert
        
        logger.info(f"Created alert: {name} ({alert.id})")
        return alert.id
        
    def add_alert_action(self, alert_id: str, action_type: str, 
                       config: Dict[str, Any]) -> Optional[str]:
        """Add an action to an alert"""
        alert = self.alerts.get(alert_id)
        if not alert:
            logger.warning(f"Alert not found: {alert_id}")
            return None
            
        action_id = alert.add_action(action_type, config)
        return action_id
        
    def enable_alert(self, alert_id: str) -> bool:
        """Enable an alert"""
        alert = self.alerts.get(alert_id)
        if not alert:
            logger.warning(f"Alert not found: {alert_id}")
            return False
            
        alert.enabled = True
        return True
        
    def disable_alert(self, alert_id: str) -> bool:
        """Disable an alert"""
        alert = self.alerts.get(alert_id)
        if not alert:
            logger.warning(f"Alert not found: {alert_id}")
            return False
            
        alert.enabled = False
        return True
        
    def evaluate_alert(self, alert_id: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Evaluate an alert"""
        alert = self.alerts.get(alert_id)
        if not alert:
            logger.warning(f"Alert not found: {alert_id}")
            return False, None
            
        metric = self.metrics.get(alert.metric_id)
        if not metric:
            logger.warning(f"Metric not found: {alert.metric_id}")
            return False, None
            
        return alert.evaluate(metric)
        
    def start_alert_monitoring(self, interval_seconds: int = 60) -> None:
        """Start a background thread to monitor alerts"""
        if self.alert_thread_running:
            logger.warning("Alert monitoring is already running")
            return
            
        self.alert_thread_running = True
        
        def monitor_alerts():
            while self.alert_thread_running:
                try:
                    self.check_all_alerts()
                    time.sleep(interval_seconds)
                except Exception as e:
                    logger.error(f"Error in alert monitoring: {str(e)}")
                    
        self.alert_thread = threading.Thread(target=monitor_alerts)
        self.alert_thread.daemon = True
        self.alert_thread.start()
        
        logger.info(f"Started alert monitoring with interval: {interval_seconds} seconds")
        
    def stop_alert_monitoring(self) -> None:
        """Stop the alert monitoring thread"""
        self.alert_thread_running = False
        if self.alert_thread:
            self.alert_thread.join(timeout=1.0)
            self.alert_thread = None
            
        logger.info("Stopped alert monitoring")
        
    def check_all_alerts(self) -> List[Dict[str, Any]]:
        """Check all enabled alerts"""
        triggered_alerts = []
        
        for alert_id, alert in self.alerts.items():
            if not alert.enabled:
                continue
                
            triggered, alert_data = self.evaluate_alert(alert_id)
            if triggered and alert_data:
                triggered_alerts.append(alert_data)
                
                # Execute actions
                for action in alert.actions:
                    self._execute_alert_action(action, alert_data)
                    
        return triggered_alerts
        
    def _execute_alert_action(self, action: Dict[str, Any], 
                           alert_data: Dict[str, Any]) -> None:
        """Execute an alert action"""
        action_type = action["type"]
        config = action["config"]
        
        if action_type == "log":
            logger.warning(f"ALERT TRIGGERED: {alert_data['alert_name']} - "
                         f"{alert_data['actual_value']} {alert_data['condition']} "
                         f"{alert_data['threshold']}")
                         
        elif action_type == "notification":
            # In a real implementation, this would send a notification
            # For demo purposes, we just log it
            notification_method = config.get("method", "console")
            recipient = config.get("recipient", "admin")
            
            logger.info(f"Would send notification to {recipient} via {notification_method}: "
                      f"Alert {alert_data['alert_name']} triggered")
                      
        elif action_type == "webhook":
            # In a real implementation, this would call a webhook
            # For demo purposes, we just log it
            webhook_url = config.get("url", "")
            
            logger.info(f"Would call webhook {webhook_url} with alert data")
            
        else:
            logger.warning(f"Unknown action type: {action_type}")
            
    def create_report(self, name: str, description: str, 
                    resource_type: ResourceType, resource_id: str) -> str:
        """Create a new performance report"""
        report = PerformanceReport(name, description, resource_type, resource_id)
        self.reports[report.id] = report
        
        logger.info(f"Created report: {name} ({report.id})")
        return report.id
        
    def add_report_section(self, report_id: str, title: str, content: str) -> Optional[str]:
        """Add a section to a report"""
        report = self.reports.get(report_id)
        if not report:
            logger.warning(f"Report not found: {report_id}")
            return None
            
        return report.add_section(title, content)
        
    def add_metric_to_report(self, report_id: str, metric_id: str) -> bool:
        """Add a metric to a report"""
        report = self.reports.get(report_id)
        if not report:
            logger.warning(f"Report not found: {report_id}")
            return False
            
        if metric_id not in self.metrics:
            logger.warning(f"Metric not found: {metric_id}")
            return False
            
        report.add_metric(metric_id)
        return True
        
    def schedule_report(self, report_id: str, interval: str, day: Optional[int] = None,
                      hour: Optional[int] = None, minute: Optional[int] = None) -> bool:
        """Schedule a report for automatic generation"""
        report = self.reports.get(report_id)
        if not report:
            logger.warning(f"Report not found: {report_id}")
            return False
            
        report.set_schedule(interval, day, hour, minute)
        return True
        
    def generate_report(self, report_id: str, 
                      start_time: Optional[datetime.datetime] = None,
                      end_time: Optional[datetime.datetime] = None) -> Optional[Dict[str, Any]]:
        """Generate a performance report"""
        report = self.reports.get(report_id)
        if not report:
            logger.warning(f"Report not found: {report_id}")
            return None
            
        # Use past day as default period if not specified
        if not end_time:
            end_time = datetime.datetime.utcnow()
            
        if not start_time:
            start_time = end_time - datetime.timedelta(days=1)
            
        # Create report data
        report_data = {
            "id": report.id,
            "name": report.name,
            "description": report.description,
            "resource_type": report.resource_type.value,
            "resource_id": report.resource_id,
            "generated_at": datetime.datetime.utcnow().isoformat(),
            "period": {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat()
            },
            "sections": report.sections.copy(),
            "metrics": []
        }
        
        # Add metric data
        for metric_id in report.metrics:
            metric = self.metrics.get(metric_id)
            if not metric:
                continue
                
            # Get statistics
            stats = metric.calculate_statistics(start_time, end_time)
            
            # Get time series data
            time_series = metric.aggregate_by_interval(TimeInterval.HOUR, start_time, end_time)
            
            report_data["metrics"].append({
                "id": metric_id,
                "name": metric.name,
                "type": metric.type.value,
                "unit": metric.unit,
                "statistics": stats,
                "time_series": time_series
            })
            
        return report_data
        
    def create_workflow_analyzer(self, workflow_id: str) -> str:
        """Create a workflow analyzer"""
        analyzer = WorkflowAnalyzer(workflow_id)
        self.workflow_analyzers[workflow_id] = analyzer
        
        logger.info(f"Created workflow analyzer for: {workflow_id}")
        return workflow_id
        
    def add_workflow_execution(self, workflow_id: str, execution_id: str,
                            start_time: datetime.datetime,
                            end_time: Optional[datetime.datetime] = None,
                            status: str = "running",
                            step_data: Optional[Dict[str, Any]] = None) -> bool:
        """Add a workflow execution record"""
        analyzer = self.workflow_analyzers.get(workflow_id)
        if not analyzer:
            if workflow_id not in self.workflow_analyzers:
                # Create analyzer if it doesn't exist
                analyzer = WorkflowAnalyzer(workflow_id)
                self.workflow_analyzers[workflow_id] = analyzer
            else:
                logger.warning(f"Workflow analyzer not found: {workflow_id}")
                return False
                
        analyzer.add_execution(execution_id, start_time, end_time, status, step_data)
        return True
        
    def get_workflow_analysis(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get a workflow analysis"""
        analyzer = self.workflow_analyzers.get(workflow_id)
        if not analyzer:
            logger.warning(f"Workflow analyzer not found: {workflow_id}")
            return None
            
        return analyzer.to_dict()
        
    def get_workflow_bottlenecks(self, workflow_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get workflow bottlenecks"""
        analyzer = self.workflow_analyzers.get(workflow_id)
        if not analyzer:
            logger.warning(f"Workflow analyzer not found: {workflow_id}")
            return None
            
        return analyzer.get_bottlenecks()
        
    def get_workflow_optimizations(self, workflow_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get workflow optimization suggestions"""
        analyzer = self.workflow_analyzers.get(workflow_id)
        if not analyzer:
            logger.warning(f"Workflow analyzer not found: {workflow_id}")
            return None
            
        return analyzer.suggest_optimizations()
        
    def compare_workflows(self, workflow_ids: List[str]) -> Dict[str, Any]:
        """Compare multiple workflows"""
        results = {}
        
        # Get analyzers for all workflows
        analyzers = {}
        for workflow_id in workflow_ids:
            analyzer = self.workflow_analyzers.get(workflow_id)
            if analyzer:
                analyzers[workflow_id] = analyzer
                
        if not analyzers:
            logger.warning("No valid workflow analyzers found")
            return {"error": "No valid workflow analyzers found"}
            
        # Compare execution times
        execution_times = {}
        for workflow_id, analyzer in analyzers.items():
            execution_times[workflow_id] = analyzer.get_average_execution_time() or 0
            
        # Compare success rates
        success_rates = {}
        for workflow_id, analyzer in analyzers.items():
            success_rates[workflow_id] = analyzer.get_execution_success_rate()
            
        # Find overall fastest and most reliable
        fastest_workflow = min(execution_times.items(), key=lambda x: x[1])[0]
        most_reliable_workflow = max(success_rates.items(), key=lambda x: x[1])[0]
        
        results = {
            "workflows": list(analyzers.keys()),
            "execution_times": execution_times,
            "success_rates": success_rates,
            "fastest_workflow": fastest_workflow,
            "most_reliable_workflow": most_reliable_workflow,
            "comparison_time": datetime.datetime.utcnow().isoformat()
        }
        
        return results


# Example usage
if __name__ == "__main__":
    # Create a performance analytics manager
    manager = PerformanceAnalyticsManager()
    
    # Create some metrics
    workflow_latency_id = manager.create_metric(
        "workflow_execution_time",
        MetricType.LATENCY,
        ResourceType.WORKFLOW,
        "workflow-123",
        "seconds",
        "Time taken to execute the workflow"
    )
    
    app_memory_id = manager.create_metric(
        "app_memory_usage",
        MetricType.RESOURCE_USAGE,
        ResourceType.APP,
        "app-456",
        "MB",
        "Memory usage of the application"
    )
    
    # Add some data points
    for i in range(10):
        # Add workflow latency data - getting faster
        manager.add_metric_data_point(
            workflow_latency_id,
            10.0 - i * 0.5,  # Decreasing latency
            {"environment": "development", "version": "1.0"},
            datetime.datetime.utcnow() - datetime.timedelta(hours=i)
        )
        
        # Add memory usage data - increasing then decreasing
        memory_usage = 100 + i * 20 if i < 5 else 200 - (i - 5) * 30
        manager.add_metric_data_point(
            app_memory_id,
            memory_usage,
            {"environment": "production", "version": "1.0"},
            datetime.datetime.utcnow() - datetime.timedelta(hours=i)
        )
        
    # Create an alert
    alert_id = manager.create_alert(
        "High Memory Usage",
        app_memory_id,
        "gt",  # greater than
        150.0,  # threshold
        5  # window minutes
    )
    
    # Add an action to the alert
    manager.add_alert_action(
        alert_id,
        "notification",
        {
            "method": "email",
            "recipient": "admin@example.com",
            "template": "alert_notification"
        }
    )
    
    # Create a workflow analyzer
    workflow_id = "workflow-123"
    manager.create_workflow_analyzer(workflow_id)
    
    # Add workflow executions
    for i in range(5):
        start_time = datetime.datetime.utcnow() - datetime.timedelta(hours=i)
        end_time = start_time + datetime.timedelta(minutes=10 - i)  # Getting faster
        
        step_data = {
            "step1": {
                "status": "completed",
                "duration": 120.0 - i * 10,
                "resources": {"cpu": 50 + i * 5, "memory": 100}
            },
            "step2": {
                "status": "completed" if i != 2 else "failed",
                "duration": 300.0 - i * 20,
                "resources": {"cpu": 70, "memory": 150}
            },
            "step3": {
                "status": "completed",
                "duration": 60.0,
                "resources": {"cpu": 30, "memory": 80}
            }
        }
        
        manager.add_workflow_execution(
            workflow_id,
            f"execution-{i}",
            start_time,
            end_time,
            "completed" if i != 2 else "failed",
            step_data
        )
        
    # Create a performance report
    report_id = manager.create_report(
        "Daily Workflow Performance",
        "Daily report of workflow performance metrics",
        ResourceType.WORKFLOW,
        workflow_id
    )
    
    # Add metrics to the report
    manager.add_metric_to_report(report_id, workflow_latency_id)
    
    # Add a section to the report
    manager.add_report_section(
        report_id,
        "Overview",
        "This report provides an overview of workflow performance metrics."
    )
    
    # Schedule the report
    manager.schedule_report(
        report_id,
        "daily",
        hour=8,
        minute=0
    )
    
    # Generate the report
    report_data = manager.generate_report(report_id)
    
    # Print some results
    print("Workflow Analysis:")
    analysis = manager.get_workflow_analysis(workflow_id)
    print(f"- Avg Execution Time: {analysis['avg_execution_time']} seconds")
    print(f"- Success Rate: {analysis['success_rate'] * 100:.2f}%")
    
    print("\nBottlenecks:")
    for bottleneck in analysis['bottlenecks']:
        print(f"- Step: {bottleneck['step_id']}, Score: {bottleneck['bottleneck_score']:.2f}")
    
    print("\nOptimization Suggestions:")
    for suggestion in analysis['optimizations']:
        print(f"- {suggestion['description']}")
        print(f"  Suggestion: {suggestion['suggestion']}")
        
    print("\nMetric Statistics (Workflow Latency):")
    stats = manager.get_metric_statistics(workflow_latency_id)
    print(f"- Count: {stats['count']}")
    print(f"- Mean: {stats['mean']:.2f} seconds")
    print(f"- Min: {stats['min']:.2f} seconds")
    print(f"- Max: {stats['max']:.2f} seconds")
    
    # Check if any alerts are triggered
    print("\nChecking Alerts:")
    triggered_alerts = manager.check_all_alerts()
    if triggered_alerts:
        for alert in triggered_alerts:
            print(f"- ALERT: {alert['alert_name']} - Value: {alert['actual_value']:.2f}, Threshold: {alert['threshold']:.2f}")
    else:
        print("- No alerts triggered")