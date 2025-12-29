"""
Email Extraction Module
Extracts and deduplicates emails using regex patterns
"""

import re
from typing import Set, List


class EmailExtractor:
    """Handles email extraction and deduplication"""
    
    # Comprehensive regex pattern for email validation
    EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    
    @staticmethod
    def extract_emails(text: str) -> Set[str]:
        """
        Extract all emails from text using regex
        
        Args:
            text (str): Text to extract emails from
            
        Returns:
            Set[str]: Set of unique emails (duplicates removed automatically)
        """
        if not text:
            return set()
        
        # Find all matches using the email pattern
        emails = re.findall(EmailExtractor.EMAIL_PATTERN, text)
        
        # Convert to set to remove duplicates and to lowercase for consistency
        unique_emails = set(email.lower() for email in emails)
        
        return unique_emails
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate if a string is a valid email format
        
        Args:
            email (str): Email string to validate
            
        Returns:
            bool: True if valid email format, False otherwise
        """
        pattern = re.compile(EmailExtractor.EMAIL_PATTERN)
        return pattern.match(email) is not None
    
    @staticmethod
    def filter_emails(emails: Set[str], exclude_domains: List[str] = None) -> Set[str]:
        """
        Filter emails by excluding certain domains
        
        Args:
            emails (Set[str]): Set of emails to filter
            exclude_domains (List[str]): List of domains to exclude (e.g., ['gmail.com', 'yahoo.com'])
            
        Returns:
            Set[str]: Filtered set of emails
        """
        if not exclude_domains:
            return emails
        
        exclude_domains = [domain.lower() for domain in exclude_domains]
        filtered = set()
        
        for email in emails:
            domain = email.split('@')[1].lower()
            if domain not in exclude_domains:
                filtered.add(email)
        
        return filtered


def extract_emails_from_text(text: str) -> Set[str]:
    """
    Convenience function to extract emails from text
    
    Args:
        text (str): Text to extract emails from
        
    Returns:
        Set[str]: Set of unique emails
    """
    return EmailExtractor.extract_emails(text)


def get_sorted_emails(emails: Set[str]) -> List[str]:
    """
    Get sorted list of emails
    
    Args:
        emails (Set[str]): Set of emails
        
    Returns:
        List[str]: Sorted list of emails
    """
    return sorted(list(emails))
