# Collectors module for Atlas Course Materials Search Engine
from .base import BaseCollector
from .ocw_collector import OCWCollector
from .stanford_collector import StanfordCollector
from .harvard_collector import HarvardCollector
from .yale_collector import YaleCollector
from .cmu_collector import CMUCollector
from .github_notes_collector import GitHubNotesCollector

__all__ = [
    'BaseCollector',
    # Bucket A: Deep Crawl - Centralized Portals
    'OCWCollector',
    'YaleCollector',
    'CMUCollector',
    'StanfordCollector',
    'HarvardCollector',
    # Bucket B: GitHub Repos
    'GitHubNotesCollector',
]
