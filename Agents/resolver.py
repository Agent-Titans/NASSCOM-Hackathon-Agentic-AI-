"""
Resolver Agent - Generates resolution steps based on ticket classification
"""
from typing import Dict, Any, List


class ResolverAgent:
    """Agent responsible for suggesting resolutions"""
    
    RESOLUTIONS = {
        "Hardware": {
            "Printer": [
                "Check if printer is powered on",
                "Verify network connectivity to printer",
                "Clear printer queue on your computer",
                "Restart the printer device",
                "Update printer drivers",
            ],
            "Monitor": [
                "Verify power cable connections",
                "Check monitor input source (HDMI/DisplayPort)",
                "Adjust brightness and contrast settings",
                "Restart connected computer",
                "Test with another display cable",
            ],
            "Server": [
                "Check server logs for errors",
                "Verify server connectivity",
                "Monitor CPU and memory usage",
                "Restart affected services",
                "Escalate to Senior IT Operations",
            ],
        },
        "Software": {
            "Application": [
                "Clear application cache",
                "Restart the application",
                "Check for software updates",
                "Verify user has required permissions",
                "Reinstall the application",
            ],
            "Database": [
                "Check database connectivity",
                "Verify database service status",
                "Review error logs",
                "Check available disk space",
                "Contact database administrator",
            ],
        },
        "Network": {
            "Connectivity": [
                "Restart your network device",
                "Check WiFi signal strength",
                "Verify correct network selection",
                "Clear DNS cache",
                "Contact Network Team",
            ],
            "VPN": [
                "Verify VPN credentials",
                "Check VPN client version",
                "Restart VPN connection",
                "Clear VPN cache",
                "Contact IT Helpdesk",
            ],
        },
        "Security": {
            "Access Control": [
                "Verify user permissions",
                "Check Active Directory status",
                "Review access logs",
                "Contact Security Team immediately",
                "Escalate to Information Security",
            ],
            "Authentication": [
                "Verify credentials are correct",
                "Check account lock status",
                "Reset password through secure channel",
                "Enable multi-factor authentication",
                "Contact IT Helpdesk for assistance",
            ],
        },
        "HR/IT Access": {
            "Account Reset": [
                "Verify user identity",
                "Reset password using recovery options",
                "Unlock account if locked",
                "Verify MFA devices",
                "Provide temporary credentials",
            ],
            "Onboarding": [
                "Create user account in Active Directory",
                "Provision email account",
                "Configure group memberships",
                "Provision hardware access",
                "Complete onboarding documentation",
            ],
        },
    }
    
    def resolve(self, classification: Dict[str, Any], ticket_description: str) -> Dict[str, Any]:
        """
        Generate resolution steps for the ticket
        
        Args:
            classification: Output from ClassifierAgent
            ticket_description: Original ticket description
            
        Returns:
            Dictionary with resolution steps
        """
        category = classification.get("category", "Hardware")
        subcategory = classification.get("subcategory", "Other")
        
        # Get resolution steps
        resolution_steps = self._get_resolution_steps(category, subcategory)
        
        return {
            "resolution_steps": resolution_steps,
            "estimated_resolution_time": self._estimate_time(category),
            "references": self._get_references(category, subcategory),
            "knowledge_base_link": f"kb/{category.lower().replace('/', '_')}.html",
            "reasoning": f"Generated {len(resolution_steps)} resolution steps for {category} issue"
        }
    
    def _get_resolution_steps(self, category: str, subcategory: str) -> List[str]:
        """Get resolution steps for category/subcategory"""
        steps = self.RESOLUTIONS.get(category, {}).get(subcategory, [])
        if not steps:
            steps = [
                "Document the issue details",
                "Search knowledge base for similar issues",
                "Contact relevant support team",
                "Escalate to senior support if needed",
            ]
        return steps
    
    def _estimate_time(self, category: str) -> str:
        """Estimate resolution time based on category"""
        estimates = {
            "Hardware": "4-24 hours",
            "Software": "1-4 hours",
            "Network": "30 minutes - 2 hours",
            "Security": "Immediate escalation",
            "HR/IT Access": "30 minutes - 2 hours",
        }
        return estimates.get(category, "2-4 hours")
    
    def _get_references(self, category: str, subcategory: str) -> List[str]:
        """Get knowledge base references"""
        return [
            f"KB Article: {category} Common Issues",
            f"FAQ: {subcategory} Troubleshooting",
            "IT Support Portal: knowledge.company.com"
        ]
