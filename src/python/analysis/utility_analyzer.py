#!/usr/bin/env python3
"""
Utility Analyzer Module for the AI App Store

This module provides functionality for analyzing the utility and value
of AI applications, focusing on cost-benefit analysis and ROI calculations.
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


class MetricType(enum.Enum):
    """Enum representing the types of utility metrics"""
    FINANCIAL = "financial"
    OPERATIONAL = "operational"
    USER_SATISFACTION = "user_satisfaction"
    TIME_SAVING = "time_saving"
    QUALITY_IMPROVEMENT = "quality_improvement"
    CUSTOM = "custom"


class UtilityMetric:
    """Represents a utility metric for an AI app"""
    
    def __init__(self, app_id: str, metric_type: MetricType, name: str, value: float):
        self.id = str(uuid.uuid4())
        self.app_id = app_id
        self.metric_type = metric_type
        self.name = name
        self.value = value
        self.unit = ""
        self.timestamp = datetime.datetime.utcnow()
        self.metadata = {}
        
    def set_unit(self, unit: str) -> None:
        """Set the unit for this metric"""
        self.unit = unit
        
    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to the metric"""
        self.metadata[key] = value
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "app_id": self.app_id,
            "metric_type": self.metric_type.value,
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }


class CostBenefitAnalysis:
    """Represents a cost-benefit analysis for an AI app"""
    
    def __init__(self, app_id: str, name: str, created_by: str):
        self.id = str(uuid.uuid4())
        self.app_id = app_id
        self.name = name
        self.created_by = created_by
        self.costs = []
        self.benefits = []
        self.time_period = {}  # e.g., {"unit": "month", "value": 12}
        self.discount_rate = 0.0
        self.created_at = datetime.datetime.utcnow()
        self.updated_at = self.created_at
        
    def set_time_period(self, unit: str, value: int) -> None:
        """Set the time period for the analysis"""
        self.time_period = {"unit": unit, "value": value}
        self.updated_at = datetime.datetime.utcnow()
        
    def set_discount_rate(self, rate: float) -> None:
        """Set the discount rate for present value calculations"""
        self.discount_rate = rate
        self.updated_at = datetime.datetime.utcnow()
        
    def add_cost(self, name: str, amount: float, 
                is_recurring: bool = False, 
                recurring_period: Optional[Dict[str, Any]] = None) -> None:
        """Add a cost to the analysis"""
        self.costs.append({
            "id": str(uuid.uuid4()),
            "name": name,
            "amount": amount,
            "is_recurring": is_recurring,
            "recurring_period": recurring_period
        })
        self.updated_at = datetime.datetime.utcnow()
        
    def add_benefit(self, name: str, amount: float, 
                   is_recurring: bool = False, 
                   recurring_period: Optional[Dict[str, Any]] = None) -> None:
        """Add a benefit to the analysis"""
        self.benefits.append({
            "id": str(uuid.uuid4()),
            "name": name,
            "amount": amount,
            "is_recurring": is_recurring,
            "recurring_period": recurring_period
        })
        self.updated_at = datetime.datetime.utcnow()
        
    def calculate_net_present_value(self) -> float:
        """Calculate the net present value of the app"""
        total_costs = self._calculate_present_value(self.costs)
        total_benefits = self._calculate_present_value(self.benefits)
        return total_benefits - total_costs
        
    def calculate_benefit_cost_ratio(self) -> float:
        """Calculate the benefit-cost ratio of the app"""
        total_costs = self._calculate_present_value(self.costs)
        total_benefits = self._calculate_present_value(self.benefits)
        
        if total_costs == 0:
            return float('inf')
            
        return total_benefits / total_costs
        
    def calculate_return_on_investment(self) -> float:
        """Calculate the return on investment (ROI) of the app"""
        total_costs = self._calculate_present_value(self.costs)
        total_benefits = self._calculate_present_value(self.benefits)
        
        if total_costs == 0:
            return float('inf')
            
        return (total_benefits - total_costs) / total_costs * 100
        
    def _calculate_present_value(self, items: List[Dict[str, Any]]) -> float:
        """Calculate the present value of a list of costs or benefits"""
        total = 0.0
        
        for item in items:
            if not item["is_recurring"]:
                total += item["amount"]
            else:
                # Calculate the present value of recurring items
                recurring_period = item.get("recurring_period", {"unit": "month", "value": 1})
                unit = recurring_period["unit"]
                value = recurring_period["value"]
                
                # Convert the time period to the same unit as the recurring period
                if self.time_period.get("unit") == unit:
                    periods = self.time_period.get("value", 1) / value
                else:
                    # Simple conversion - in a real implementation, this would handle different time units properly
                    periods = self.time_period.get("value", 1)
                
                amount = item["amount"]
                rate = self.discount_rate / 100  # Convert percentage to decimal
                
                # Calculate present value using the formula: PV = Amount * [(1 - (1 + r)^-n) / r]
                if rate > 0:
                    pv = amount * ((1 - (1 + rate) ** -periods) / rate)
                else:
                    pv = amount * periods
                    
                total += pv
                
        return total
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        result = {
            "id": self.id,
            "app_id": self.app_id,
            "name": self.name,
            "created_by": self.created_by,
            "costs": self.costs,
            "benefits": self.benefits,
            "time_period": self.time_period,
            "discount_rate": self.discount_rate,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
        
        # Add calculated metrics
        result["net_present_value"] = self.calculate_net_present_value()
        result["benefit_cost_ratio"] = self.calculate_benefit_cost_ratio()
        result["roi"] = self.calculate_return_on_investment()
        
        return result


class ResourceAllocationScenario:
    """Represents a resource allocation scenario for optimizing app investments"""
    
    def __init__(self, name: str, budget: float, created_by: str):
        self.id = str(uuid.uuid4())
        self.name = name
        self.budget = budget
        self.created_by = created_by
        self.apps = []  # List of apps with their costs and expected benefits
        self.constraints = []  # Additional constraints on the allocation
        self.created_at = datetime.datetime.utcnow()
        self.updated_at = self.created_at
        
    def add_app(self, app_id: str, name: str, cost: float, benefit: float) -> None:
        """Add an app to the scenario"""
        self.apps.append({
            "id": app_id,
            "name": name,
            "cost": cost,
            "benefit": benefit,
            "allocated": False
        })
        self.updated_at = datetime.datetime.utcnow()
        
    def add_constraint(self, constraint_type: str, parameters: Dict[str, Any]) -> None:
        """Add a constraint to the scenario"""
        self.constraints.append({
            "id": str(uuid.uuid4()),
            "type": constraint_type,
            "parameters": parameters
        })
        self.updated_at = datetime.datetime.utcnow()
        
    def optimize_allocation(self) -> Dict[str, Any]:
        """Optimize the resource allocation based on the budget and constraints"""
        # In a real implementation, this would use a more sophisticated optimization algorithm
        # For this example, we'll use a simple greedy algorithm based on benefit/cost ratio
        
        # Calculate benefit/cost ratio for each app
        for app in self.apps:
            app["ratio"] = app["benefit"] / app["cost"] if app["cost"] > 0 else float('inf')
            app["allocated"] = False
            
        # Sort apps by benefit/cost ratio (descending)
        sorted_apps = sorted(self.apps, key=lambda a: a["ratio"], reverse=True)
        
        # Allocate resources within budget
        allocated_apps = []
        remaining_budget = self.budget
        total_benefit = 0.0
        
        for app in sorted_apps:
            if app["cost"] <= remaining_budget:
                app["allocated"] = True
                allocated_apps.append(app)
                remaining_budget -= app["cost"]
                total_benefit += app["benefit"]
                
        # Apply constraints (simplified version)
        for constraint in self.constraints:
            if constraint["type"] == "mandatory_app" and "app_id" in constraint["parameters"]:
                app_id = constraint["parameters"]["app_id"]
                
                # Find the app
                for app in self.apps:
                    if app["id"] == app_id and not app["allocated"]:
                        # If we can't allocate within budget, remove the app with the lowest ratio
                        if app["cost"] > remaining_budget:
                            allocated_apps.sort(key=lambda a: a["ratio"])
                            while allocated_apps and app["cost"] > remaining_budget:
                                removed_app = allocated_apps.pop(0)
                                remaining_budget += removed_app["cost"]
                                total_benefit -= removed_app["benefit"]
                                
                                # Update the app's allocation status
                                for a in self.apps:
                                    if a["id"] == removed_app["id"]:
                                        a["allocated"] = False
                                        break
                        
                        # Allocate the mandatory app if possible
                        if app["cost"] <= remaining_budget:
                            app["allocated"] = True
                            allocated_apps.append(app)
                            remaining_budget -= app["cost"]
                            total_benefit += app["benefit"]
                            break
        
        return {
            "total_cost": self.budget - remaining_budget,
            "total_benefit": total_benefit,
            "remaining_budget": remaining_budget,
            "allocated_apps": [app for app in self.apps if app["allocated"]],
            "unallocated_apps": [app for app in self.apps if not app["allocated"]]
        }
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        allocation_result = self.optimize_allocation()
        
        return {
            "id": self.id,
            "name": self.name,
            "budget": self.budget,
            "created_by": self.created_by,
            "apps": self.apps,
            "constraints": self.constraints,
            "allocation_result": allocation_result,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class UsageTrendAnalysis:
    """Represents an analysis of usage trends for an app"""
    
    def __init__(self, app_id: str, name: str, created_by: str, 
                metrics: List[str], time_range: Dict[str, Any]):
        self.id = str(uuid.uuid4())
        self.app_id = app_id
        self.name = name
        self.created_by = created_by
        self.metrics = metrics  # List of metric names to analyze
        self.time_range = time_range  # e.g., {"start": "2023-01-01", "end": "2023-12-31"}
        self.aggregation = "daily"  # daily, weekly, monthly
        self.trend_data = {}  # Will hold the calculated trend data
        self.created_at = datetime.datetime.utcnow()
        self.updated_at = self.created_at
        
    def set_aggregation(self, aggregation: str) -> None:
        """Set the aggregation period for the trend analysis"""
        valid_aggregations = ["hourly", "daily", "weekly", "monthly", "quarterly", "yearly"]
        if aggregation not in valid_aggregations:
            raise ValueError(f"Invalid aggregation: {aggregation}. Must be one of {valid_aggregations}")
            
        self.aggregation = aggregation
        self.updated_at = datetime.datetime.utcnow()
        
    def add_metric(self, metric_name: str) -> None:
        """Add a metric to analyze"""
        if metric_name not in self.metrics:
            self.metrics.append(metric_name)
            self.updated_at = datetime.datetime.utcnow()
            
    def remove_metric(self, metric_name: str) -> bool:
        """Remove a metric from the analysis"""
        if metric_name in self.metrics:
            self.metrics.remove(metric_name)
            self.updated_at = datetime.datetime.utcnow()
            return True
        return False
        
    def calculate_trends(self, metric_data: Dict[str, List[Dict[str, Any]]]) -> None:
        """Calculate trends based on the provided metric data"""
        self.trend_data = {}
        
        for metric_name, data_points in metric_data.items():
            if metric_name not in self.metrics:
                continue
                
            # Sort data points by timestamp
            sorted_data = sorted(data_points, key=lambda x: x["timestamp"])
            
            # Group by aggregation period
            grouped_data = self._group_by_aggregation(sorted_data)
            
            # Calculate statistics for each period
            stats = []
            for period, points in grouped_data.items():
                values = [p["value"] for p in points]
                stats.append({
                    "period": period,
                    "count": len(values),
                    "sum": sum(values),
                    "avg": sum(values) / len(values) if values else 0,
                    "min": min(values) if values else 0,
                    "max": max(values) if values else 0
                })
                
            self.trend_data[metric_name] = stats
            
        self.updated_at = datetime.datetime.utcnow()
        
    def _group_by_aggregation(self, data_points: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group data points by the specified aggregation period"""
        result = {}
        
        for point in data_points:
            # Parse timestamp
            timestamp = datetime.datetime.fromisoformat(point["timestamp"].replace("Z", "+00:00"))
            
            # Generate period key based on aggregation
            if self.aggregation == "hourly":
                period = timestamp.strftime("%Y-%m-%d %H:00")
            elif self.aggregation == "daily":
                period = timestamp.strftime("%Y-%m-%d")
            elif self.aggregation == "weekly":
                # ISO week format
                period = f"{timestamp.year}-W{timestamp.isocalendar()[1]:02d}"
            elif self.aggregation == "monthly":
                period = timestamp.strftime("%Y-%m")
            elif self.aggregation == "quarterly":
                quarter = (timestamp.month - 1) // 3 + 1
                period = f"{timestamp.year}-Q{quarter}"
            elif self.aggregation == "yearly":
                period = str(timestamp.year)
            else:
                period = timestamp.strftime("%Y-%m-%d")  # Default to daily
                
            if period not in result:
                result[period] = []
                
            result[period].append(point)
            
        return result
        
    def get_trend_summary(self) -> Dict[str, Any]:
        """Get a summary of the calculated trends"""
        summary = {}
        
        for metric_name, stats in self.trend_data.items():
            if not stats:
                continue
                
            # Calculate overall statistics
            values = [s["avg"] for s in stats]
            
            # Calculate trend (simple linear regression)
            n = len(values)
            if n >= 2:
                x = list(range(n))
                x_mean = sum(x) / n
                y_mean = sum(values) / n
                
                numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
                denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
                
                slope = numerator / denominator if denominator != 0 else 0
                
                # Determine trend direction
                if slope > 0:
                    trend = "increasing"
                elif slope < 0:
                    trend = "decreasing"
                else:
                    trend = "stable"
                    
                # Calculate percentage change
                if values[0] != 0:
                    percent_change = (values[-1] - values[0]) / values[0] * 100
                else:
                    percent_change = 0
            else:
                trend = "insufficient_data"
                slope = 0
                percent_change = 0
                
            summary[metric_name] = {
                "min": min(values) if values else 0,
                "max": max(values) if values else 0,
                "avg": sum(values) / n if values else 0,
                "trend": trend,
                "slope": slope,
                "percent_change": percent_change,
                "period_count": n
            }
            
        return summary
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "app_id": self.app_id,
            "name": self.name,
            "created_by": self.created_by,
            "metrics": self.metrics,
            "time_range": self.time_range,
            "aggregation": self.aggregation,
            "trend_data": self.trend_data,
            "trend_summary": self.get_trend_summary(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class UtilityAnalyzer:
    """Main class for analyzing the utility of AI applications"""
    
    def __init__(self):
        self.utility_metrics: List[UtilityMetric] = []
        self.cost_benefit_analyses: Dict[str, CostBenefitAnalysis] = {}
        self.resource_allocation_scenarios: Dict[str, ResourceAllocationScenario] = {}
        self.usage_trend_analyses: Dict[str, UsageTrendAnalysis] = {}
        
    def record_utility_metric(self, app_id: str, metric_type: MetricType, 
                            name: str, value: float, unit: str = "",
                            metadata: Dict[str, Any] = None) -> str:
        """Record a utility metric"""
        metric = UtilityMetric(app_id, metric_type, name, value)
        
        if unit:
            metric.set_unit(unit)
            
        if metadata:
            for key, value in metadata.items():
                metric.add_metadata(key, value)
                
        self.utility_metrics.append(metric)
        return metric.id
        
    def get_utility_metrics(self, app_id: Optional[str] = None,
                          metric_type: Optional[MetricType] = None,
                          name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get utility metrics, optionally filtered"""
        result = []
        
        for metric in self.utility_metrics:
            if app_id is not None and metric.app_id != app_id:
                continue
                
            if metric_type is not None and metric.metric_type != metric_type:
                continue
                
            if name is not None and metric.name != name:
                continue
                
            result.append(metric.to_dict())
            
        return result
        
    def create_cost_benefit_analysis(self, app_id: str, name: str, created_by: str) -> CostBenefitAnalysis:
        """Create a new cost-benefit analysis"""
        analysis = CostBenefitAnalysis(app_id, name, created_by)
        self.cost_benefit_analyses[analysis.id] = analysis
        return analysis
        
    def get_cost_benefit_analysis(self, analysis_id: str) -> Optional[CostBenefitAnalysis]:
        """Get a cost-benefit analysis by ID"""
        return self.cost_benefit_analyses.get(analysis_id)
        
    def list_cost_benefit_analyses(self, app_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List cost-benefit analyses, optionally filtered by app ID"""
        result = []
        
        for analysis in self.cost_benefit_analyses.values():
            if app_id is None or analysis.app_id == app_id:
                result.append(analysis.to_dict())
                
        return result
        
    def create_resource_allocation_scenario(self, name: str, budget: float, 
                                          created_by: str) -> ResourceAllocationScenario:
        """Create a new resource allocation scenario"""
        scenario = ResourceAllocationScenario(name, budget, created_by)
        self.resource_allocation_scenarios[scenario.id] = scenario
        return scenario
        
    def get_resource_allocation_scenario(self, scenario_id: str) -> Optional[ResourceAllocationScenario]:
        """Get a resource allocation scenario by ID"""
        return self.resource_allocation_scenarios.get(scenario_id)
        
    def list_resource_allocation_scenarios(self) -> List[Dict[str, Any]]:
        """List all resource allocation scenarios"""
        return [scenario.to_dict() for scenario in self.resource_allocation_scenarios.values()]
        
    def create_usage_trend_analysis(self, app_id: str, name: str, created_by: str,
                                  metrics: List[str], time_range: Dict[str, Any]) -> UsageTrendAnalysis:
        """Create a new usage trend analysis"""
        analysis = UsageTrendAnalysis(app_id, name, created_by, metrics, time_range)
        self.usage_trend_analyses[analysis.id] = analysis
        return analysis
        
    def get_usage_trend_analysis(self, analysis_id: str) -> Optional[UsageTrendAnalysis]:
        """Get a usage trend analysis by ID"""
        return self.usage_trend_analyses.get(analysis_id)
        
    def list_usage_trend_analyses(self, app_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List usage trend analyses, optionally filtered by app ID"""
        result = []
        
        for analysis in self.usage_trend_analyses.values():
            if app_id is None or analysis.app_id == app_id:
                result.append(analysis.to_dict())
                
        return result
        
    def analyze_app_value(self, app_id: str) -> Dict[str, Any]:
        """Perform a comprehensive value analysis of an app"""
        # Get all utility metrics for this app
        metrics = self.get_utility_metrics(app_id=app_id)
        
        # Get cost-benefit analyses for this app
        analyses = self.list_cost_benefit_analyses(app_id=app_id)
        
        # Get usage trend analyses for this app
        trend_analyses = self.list_usage_trend_analyses(app_id=app_id)
        
        # Calculate aggregate statistics
        metric_by_type = {}
        for metric in metrics:
            metric_type = metric["metric_type"]
            if metric_type not in metric_by_type:
                metric_by_type[metric_type] = []
            metric_by_type[metric_type].append(metric)
            
        # Get the latest cost-benefit analysis if available
        latest_analysis = None
        if analyses:
            latest_analysis = max(analyses, key=lambda a: a["updated_at"])
            
        # Compile results
        result = {
            "app_id": app_id,
            "metrics_count": len(metrics),
            "metrics_by_type": {k: len(v) for k, v in metric_by_type.items()},
            "financial_indicators": {},
            "trend_summary": {}
        }
        
        # Add financial indicators if available
        if latest_analysis:
            result["financial_indicators"] = {
                "net_present_value": latest_analysis["net_present_value"],
                "benefit_cost_ratio": latest_analysis["benefit_cost_ratio"],
                "roi": latest_analysis["roi"]
            }
            
        # Add trend summaries if available
        if trend_analyses:
            for analysis in trend_analyses:
                for metric_name, summary in analysis["trend_summary"].items():
                    result["trend_summary"][metric_name] = summary
                    
        return result


# Example usage
if __name__ == "__main__":
    # Create utility analyzer
    analyzer = UtilityAnalyzer()
    
    # Record some utility metrics
    app_id = "app-123"
    
    # Financial metric
    analyzer.record_utility_metric(
        app_id,
        MetricType.FINANCIAL,
        "cost_savings",
        120000,
        "USD",
        {"department": "underwriting", "period": "annual"}
    )
    
    # Time saving metric
    analyzer.record_utility_metric(
        app_id,
        MetricType.TIME_SAVING,
        "process_time_reduction",
        45,
        "percent",
        {"process": "loan_approval", "baseline": "manual_process"}
    )
    
    # User satisfaction metric
    analyzer.record_utility_metric(
        app_id,
        MetricType.USER_SATISFACTION,
        "user_satisfaction_score",
        4.2,
        "rating",
        {"scale": "1-5", "respondents": 150}
    )
    
    # Create a cost-benefit analysis
    analysis = analyzer.create_cost_benefit_analysis(
        app_id,
        "Annual Cost-Benefit Analysis",
        "user-456"
    )
    
    # Set time period and discount rate
    analysis.set_time_period("year", 3)
    analysis.set_discount_rate(5.0)
    
    # Add costs
    analysis.add_cost("Development costs", 50000)
    analysis.add_cost("Infrastructure", 1000, True, {"unit": "month", "value": 1})
    analysis.add_cost("Support staff", 5000, True, {"unit": "month", "value": 1})
    
    # Add benefits
    analysis.add_benefit("Time savings", 8000, True, {"unit": "month", "value": 1})
    analysis.add_benefit("Error reduction", 3000, True, {"unit": "month", "value": 1})
    analysis.add_benefit("Customer satisfaction improvement", 5000, True, {"unit": "month", "value": 3})
    
    # Calculate financial indicators
    npv = analysis.calculate_net_present_value()
    bcr = analysis.calculate_benefit_cost_ratio()
    roi = analysis.calculate_return_on_investment()
    
    print(f"Net Present Value: ${npv:.2f}")
    print(f"Benefit-Cost Ratio: {bcr:.2f}")
    print(f"Return on Investment: {roi:.2f}%")
    
    # Create a resource allocation scenario
    scenario = analyzer.create_resource_allocation_scenario(
        "Q1 2023 AI Investment Portfolio",
        200000,
        "user-789"
    )
    
    # Add apps to the scenario
    scenario.add_app("app-123", "Loan Eligibility Predictor", 75000, 150000)
    scenario.add_app("app-456", "Document Processor", 50000, 85000)
    scenario.add_app("app-789", "Customer Chatbot", 40000, 60000)
    scenario.add_app("app-012", "Fraud Detection System", 80000, 200000)
    
    # Add constraints
    scenario.add_constraint("mandatory_app", {"app_id": "app-789"})
    
    # Optimize allocation
    allocation = scenario.optimize_allocation()
    
    print("\nResource Allocation Results:")
    print(f"Total Cost: ${allocation['total_cost']}")
    print(f"Total Benefit: ${allocation['total_benefit']}")
    print(f"Remaining Budget: ${allocation['remaining_budget']}")
    print("Allocated Apps:")
    for app in allocation["allocated_apps"]:
        print(f"- {app['name']}: ${app['cost']} (Benefit: ${app['benefit']})")
        
    # Create a usage trend analysis
    trend_analysis = analyzer.create_usage_trend_analysis(
        app_id,
        "Monthly Usage Trends",
        "user-456",
        ["active_users", "queries_per_user", "response_time"],
        {"start": "2023-01-01", "end": "2023-06-30"}
    )
    
    # Set aggregation to monthly
    trend_analysis.set_aggregation("monthly")
    
    # Simulate some metric data
    metric_data = {
        "active_users": [
            {"timestamp": "2023-01-15T12:00:00Z", "value": 100},
            {"timestamp": "2023-02-15T12:00:00Z", "value": 120},
            {"timestamp": "2023-03-15T12:00:00Z", "value": 150},
            {"timestamp": "2023-04-15T12:00:00Z", "value": 200},
            {"timestamp": "2023-05-15T12:00:00Z", "value": 250},
            {"timestamp": "2023-06-15T12:00:00Z", "value": 300}
        ],
        "queries_per_user": [
            {"timestamp": "2023-01-15T12:00:00Z", "value": 5},
            {"timestamp": "2023-02-15T12:00:00Z", "value": 6},
            {"timestamp": "2023-03-15T12:00:00Z", "value": 7},
            {"timestamp": "2023-04-15T12:00:00Z", "value": 8},
            {"timestamp": "2023-05-15T12:00:00Z", "value": 10},
            {"timestamp": "2023-06-15T12:00:00Z", "value": 12}
        ],
        "response_time": [
            {"timestamp": "2023-01-15T12:00:00Z", "value": 500},
            {"timestamp": "2023-02-15T12:00:00Z", "value": 450},
            {"timestamp": "2023-03-15T12:00:00Z", "value": 400},
            {"timestamp": "2023-04-15T12:00:00Z", "value": 350},
            {"timestamp": "2023-05-15T12:00:00Z", "value": 300},
            {"timestamp": "2023-06-15T12:00:00Z", "value": 250}
        ]
    }
    
    # Calculate trends
    trend_analysis.calculate_trends(metric_data)
    
    # Get trend summary
    trend_summary = trend_analysis.get_trend_summary()
    
    print("\nUsage Trend Summary:")
    for metric_name, summary in trend_summary.items():
        print(f"{metric_name}:")
        print(f"  Trend: {summary['trend']}")
        print(f"  Percent Change: {summary['percent_change']:.2f}%")
        print(f"  Average: {summary['avg']:.2f}")
        
    # Perform comprehensive app value analysis
    value_analysis = analyzer.analyze_app_value(app_id)
    
    print("\nApp Value Analysis:")
    print(f"Total Metrics: {value_analysis['metrics_count']}")
    print("Financial Indicators:")
    for name, value in value_analysis["financial_indicators"].items():
        print(f"  {name}: {value:.2f}")