"""
Supervisor Agent - Reviews ticket processing and determines confidence/escalation
"""
from typing import Dict, Any


class SupervisorAgent:
    """Agent responsible for final review and confidence assessment"""
    
    def supervise(self, classification: Dict[str, Any], 
                  routing: Dict[str, Any],
                  resolution: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform final supervision and confidence assessment
        
        Args:
            classification: Output from ClassifierAgent
            routing: Output from RouterAgent
            resolution: Output from ResolverAgent
            
        Returns:
            Final ticket processing result
        """
        # Calculate overall confidence
        confidence = self._calculate_confidence(classification, routing, resolution)
        
        # Determine if escalation is needed
        escalate, escalation_reason = self._determine_escalation(
            confidence, classification, routing
        )
        
        return {
            "category": classification.get("category", "Unknown"),
            "subcategory": classification.get("subcategory", "Unknown"),
            "department": routing.get("department", "Unknown"),
            "team": routing.get("team", "Unknown"),
            "priority": routing.get("priority", "Medium"),
            "confidence": confidence,
            "escalate": escalate,
            "escalation_reason": escalation_reason,
            "resolution_steps": resolution.get("resolution_steps", []),
            "estimated_time": resolution.get("estimated_resolution_time", "N/A"),
            "sla_hours": routing.get("sla_hours", 24),
            "classifier_notes": classification.get("reasoning", ""),
            "router_notes": routing.get("reasoning", ""),
            "supervisor_notes": self._generate_supervisor_notes(
                confidence, escalate, classification
            ),
            "similar_tickets": self._get_similar_tickets(),
            "processing_status": "completed",
            "requires_human_review": escalate
        }
    
    def _calculate_confidence(self, classification: Dict[str, Any],
                             routing: Dict[str, Any],
                             resolution: Dict[str, Any]) -> float:
        """Calculate overall confidence score"""
        classifier_confidence = classification.get("confidence_score", 0.5)
        
        # Adjust based on resolution availability
        resolution_steps = resolution.get("resolution_steps", [])
        resolution_confidence = min(len(resolution_steps) / 5, 1.0)
        
        # Category-specific adjustments
        category = classification.get("category", "")
        if category == "Security":
            # Security tickets need higher confidence before auto-resolution
            resolution_confidence *= 0.8
        
        # Average confidences
        overall_confidence = (classifier_confidence * 0.4 + 
                             resolution_confidence * 0.6)
        
        return round(overall_confidence, 2)
    
    def _determine_escalation(self, confidence: float,
                             classification: Dict[str, Any],
                             routing: Dict[str, Any]) -> tuple:
        """Determine if ticket should be escalated"""
        confidence_threshold = 0.75
        
        # Always escalate security issues
        if classification.get("category") == "Security":
            return True, "Security issue requires human review"
        
        # Escalate low confidence tickets
        if confidence < confidence_threshold:
            return True, f"Low confidence score ({confidence:.0%}) - requires expert review"
        
        # Escalate if no resolution steps available
        resolution_steps = classification.get("subcategory", "")
        if not resolution_steps:
            return True, "No automated resolution available"
        
        # Escalate critical priority tickets
        if routing.get("priority") == "Critical":
            return True, "Critical priority ticket - requires immediate attention"
        
        return False, ""
    
    def _generate_supervisor_notes(self, confidence: float,
                                  escalate: bool,
                                  classification: Dict[str, Any]) -> str:
        """Generate supervisor assessment notes"""
        status = "Approved for auto-resolution" if not escalate else "Flagged for escalation"
        
        notes = f"{status}. "
        notes += f"Confidence level: {confidence:.0%}. "
        
        if escalate:
            notes += "This ticket requires human expertise for proper resolution."
        else:
            notes += "Recommended automated resolution should resolve most cases."
        
        return notes
    
    def _get_similar_tickets(self) -> list:
        """Retrieve similar past tickets from RAG (placeholder)"""
        return [
            "Ticket #2045: Similar printer connectivity issue - resolved in 2 hours",
            "Ticket #2012: Related hardware troubleshooting - resolved in 6 hours",
        ]
