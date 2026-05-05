"""
Router Agent - Routes tickets to appropriate department and assigns priority
"""
from typing import Dict, Any


class RouterAgent:
    """Agent responsible for routing tickets to departments"""
    
    ROUTING_MAP = {
        "Hardware": {
            "department": "Hardware Support",
            "team": "IT Operations",
            "sla_hours": 24
        },
        "Software": {
            "department": "DevOps",
            "team": "Application Support",
            "sla_hours": 8
        },
        "Network": {
            "department": "Network Team",
            "team": "Infrastructure",
            "sla_hours": 4
        },
        "Security": {
            "department": "Security Team",
            "team": "Information Security",
            "sla_hours": 2
        },
        "HR/IT Access": {
            "department": "IT Helpdesk",
            "team": "Identity Management",
            "sla_hours": 2
        },
    }
    
    PRIORITY_LEVELS = {
        "Critical": {"value": 4, "multiplier": 0.5},
        "High": {"value": 3, "multiplier": 0.75},
        "Medium": {"value": 2, "multiplier": 1.0},
        "Low": {"value": 1, "multiplier": 1.5},
    }
    
    def route(self, classification: Dict[str, Any], urgency: str) -> Dict[str, Any]:
        """
        Route ticket to appropriate department
        
        Args:
            classification: Output from ClassifierAgent
            urgency: User-perceived urgency level
            
        Returns:
            Dictionary with routing decisions
        """
        category = classification.get("category", "Other")
        routing_info = self.ROUTING_MAP.get(category, self.ROUTING_MAP["Hardware"])
        
        # Determine priority
        priority = self._calculate_priority(category, urgency, 
                                           classification.get("confidence_score", 0.5))
        
        return {
            "department": routing_info["department"],
            "team": routing_info["team"],
            "priority": priority,
            "sla_hours": routing_info["sla_hours"],
            "assigned_to": routing_info["team"],
            "reasoning": f"Routed to {routing_info['department']} with {priority} priority"
        }
    
    def _calculate_priority(self, category: str, urgency: str, confidence: float) -> str:
        """Calculate actual priority based on multiple factors"""
        urgency_map = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}
        base_priority = urgency_map.get(urgency, 2)
        
        # Security issues get elevated priority
        if category == "Security":
            base_priority = max(base_priority, 3)
        
        # High confidence on critical items stays critical
        if base_priority == 4:
            return "Critical"
        elif base_priority == 3:
            return "High"
        elif base_priority == 2:
            return "Medium"
        else:
            return "Low"
