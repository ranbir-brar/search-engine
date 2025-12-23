"""
Base Collector class for Atlas Academic Search Engine.
All collectors should inherit from this class.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime


class BaseCollector(ABC):
    """
    Abstract base class for all academic resource collectors.
    
    Each collector is responsible for:
    1. Fetching resources from a specific source
    2. Transforming them into a standardized schema
    3. Returning a list of payloads ready for Kafka
    """
    
    # Valid resource types
    RESOURCE_TYPES = ["Paper", "Lecture Slides", "Course Notes", "Syllabus"]
    
    def __init__(self, name: str):
        self.name = name
        self.seen_urls = set()
    
    @abstractmethod
    def collect(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Collect resources from the source.
        
        Args:
            limit: Maximum number of resources to collect per run
            
        Returns:
            List of payload dictionaries ready for Kafka
        """
        pass
    
    def create_payload(
        self,
        title: str,
        summary: str,
        authors: List[str],
        url: str,
        source: str,
        resource_type: str,
        published: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a standardized payload for Kafka.
        
        Args:
            title: Resource title
            summary: Abstract or description
            authors: List of author/instructor names
            url: Direct URL to the resource
            source: Source name (e.g., "arXiv", "MIT OCW")
            resource_type: One of RESOURCE_TYPES
            published: Publication date string
            
        Returns:
            Standardized payload dictionary
        """
        if resource_type not in self.RESOURCE_TYPES:
            raise ValueError(f"Invalid resource_type: {resource_type}. Must be one of {self.RESOURCE_TYPES}")
        
        return {
            "title": title,
            "summary": summary,
            "authors": authors,
            "url": url,
            "source": source,
            "resource_type": resource_type,
            "published": published or datetime.now().isoformat(),
            # Combined content for embedding
            "content": f"{title}\n\n{summary}"
        }
    
    def is_new(self, url: str) -> bool:
        """Check if URL has been seen before."""
        if url in self.seen_urls:
            return False
        self.seen_urls.add(url)
        return True
