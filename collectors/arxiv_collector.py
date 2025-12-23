"""
arXiv Collector for Atlas Academic Search Engine.
Fetches research papers from arXiv using their official API.
"""
import arxiv
from typing import List, Dict, Any
from .base import BaseCollector


class ArxivCollector(BaseCollector):
    """
    Collector for arXiv research papers.
    
    Uses the arxiv Python library to fetch papers from various categories.
    """
    
    # CS-focused categories for student relevance
    DEFAULT_CATEGORIES = [
        "cs.AI",      # Artificial Intelligence
        "cs.LG",      # Machine Learning
        "cs.CL",      # Computation and Language (NLP)
        "cs.CV",      # Computer Vision
        "cs.SE",      # Software Engineering
        "cs.DB",      # Databases
        "cs.DS",      # Data Structures and Algorithms
        "cs.CR",      # Cryptography and Security
    ]
    
    def __init__(self, categories: List[str] = None):
        super().__init__(name="arXiv")
        self.categories = categories or self.DEFAULT_CATEGORIES
        self.client = arxiv.Client()
    
    def collect(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch recent papers from arXiv.
        
        Args:
            limit: Maximum number of papers to fetch per category
            
        Returns:
            List of paper payloads
        """
        payloads = []
        
        for category in self.categories:
            try:
                # Build search query for category
                search = arxiv.Search(
                    query=f"cat:{category}",
                    max_results=limit // len(self.categories),  # Distribute limit
                    sort_by=arxiv.SortCriterion.SubmittedDate,
                    sort_order=arxiv.SortOrder.Descending
                )
                
                for paper in self.client.results(search):
                    if not self.is_new(paper.entry_id):
                        continue
                    
                    # Extract author names
                    authors = [author.name for author in paper.authors]
                    
                    # Create standardized payload
                    payload = self.create_payload(
                        title=paper.title,
                        summary=paper.summary,
                        authors=authors,
                        url=paper.pdf_url or paper.entry_id,
                        source="arXiv",
                        resource_type="Paper",
                        published=paper.published.isoformat() if paper.published else None
                    )
                    
                    payloads.append(payload)
                    print(f"[arXiv] Collected: {paper.title[:60]}...")
                    
            except Exception as e:
                print(f"[arXiv] Error fetching {category}: {e}")
        
        return payloads
