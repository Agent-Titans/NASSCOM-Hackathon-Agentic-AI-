"""
Data Processing Utilities
"""
import re
from typing import Dict, Any


class DataProcessor:
    """Handles data preprocessing and validation"""
    
    @staticmethod
    def preprocess_ticket(ticket_description: str) -> str:
        """
        Preprocess ticket description
        
        Args:
            ticket_description: Raw ticket text
            
        Returns:
            Cleaned ticket text
        """
        # Remove extra whitespace
        text = " ".join(ticket_description.split())
        
        # Convert to lowercase for processing
        text = text.lower()
        
        # Remove special characters but keep spaces and punctuation
        text = re.sub(r'[^\w\s.!?-]', '', text)
        
        return text.strip()
    
    @staticmethod
    def extract_keywords(text: str, num_keywords: int = 5) -> list:
        """
        Extract keywords from text
        
        Args:
            text: Input text
            num_keywords: Number of keywords to extract
            
        Returns:
            List of keywords
        """
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'is', 'are', 'was', 'were', 'be', 'been', 'being'
        }
        
        words = text.lower().split()
        keywords = [w for w in words if w not in stop_words and len(w) > 3]
        
        return keywords[:num_keywords]
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate email format
        
        Args:
            email: Email address to validate
            
        Returns:
            True if valid, False otherwise
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def mask_pii(text: str) -> str:
        """
        Mask personally identifiable information
        
        Args:
            text: Text potentially containing PII
            
        Returns:
            Text with PII masked
        """
        # Mask emails
        text = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '[EMAIL]', text)
        
        # Mask phone numbers
        text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', text)
        
        # Mask IP addresses
        text = re.sub(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', '[IP_ADDRESS]', text)
        
        # Mask common personal identifiers
        text = re.sub(r'\b(?:SSN|ID|PIN):\s*\d+\b', '[IDENTIFIER]', text, flags=re.IGNORECASE)
        
        return text
    
    @staticmethod
    def format_ticket_output(result: Dict[str, Any]) -> str:
        """
        Format ticket processing result for display
        
        Args:
            result: Ticket processing result
            
        Returns:
            Formatted string
        """
        output = []
        output.append(f"Category: {result.get('category', 'N/A')}")
        output.append(f"Department: {result.get('department', 'N/A')}")
        output.append(f"Priority: {result.get('priority', 'N/A')}")
        output.append(f"Confidence: {result.get('confidence', 0):.0%}")
        
        if result.get('resolution_steps'):
            output.append("\nResolution Steps:")
            for i, step in enumerate(result['resolution_steps'], 1):
                output.append(f"  {i}. {step}")
        
        if result.get('escalate'):
            output.append(f"\nEscalation Required: {result.get('escalation_reason', 'N/A')}")
        
        return "\n".join(output)
