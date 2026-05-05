"""
Classifier Agent - Analyzes ticket description and assigns category
"""
from typing import Dict, Any


class ClassifierAgent:
    """Agent responsible for ticket classification"""
    
    CATEGORIES = {
        "Hardware": ["printer", "monitor", "keyboard", "mouse", "server", "hardware", "equipment"],
        "Software": ["bug", "crash", "error", "install", "application", "software", "license"],
        "Network": ["internet", "connection", "wifi", "vpn", "bandwidth", "network", "connectivity"],
        "Security": ["password", "access", "permission", "breach", "malware", "security", "compromised"],
        "HR/IT Access": ["account", "reset", "onboarding", "access", "user", "email"],
    }
    
    def classify(self, ticket_description: str) -> Dict[str, Any]:
        """
        Classify ticket into appropriate category
        
        Args:
            ticket_description: The ticket text to classify
            
        Returns:
            Dictionary with classification results
        """
        ticket_lower = ticket_description.lower()
        scores = {}
        
        # Simple keyword-based classification (will be replaced with LLM)
        for category, keywords in self.CATEGORIES.items():
            score = sum(1 for keyword in keywords if keyword in ticket_lower)
            scores[category] = score
        
        # Determine primary category
        primary_category = max(scores, key=scores.get) if scores else "Other"
        
        return {
            "category": primary_category,
            "subcategory": self._get_subcategory(primary_category, ticket_lower),
            "confidence_score": min(scores.get(primary_category, 0) / 3, 1.0),
            "all_scores": scores,
            "reasoning": f"Classified as {primary_category} based on keyword analysis"
        }
    
    def _get_subcategory(self, category: str, ticket_text: str) -> str:
        """Determine subcategory based on category"""
        subcategories = {
            "Hardware": ["Printer", "Monitor", "Server", "Peripheral", "Other"],
            "Software": ["Application", "OS", "Database", "License", "Installation"],
            "Network": ["Connectivity", "VPN", "Bandwidth", "WiFi", "Other"],
            "Security": ["Access Control", "Authentication", "Data Breach", "Malware", "Other"],
            "HR/IT Access": ["Account Reset", "Onboarding", "Permissions", "Email", "Other"],
        }
        return subcategories.get(category, ["Unknown"])[0]
