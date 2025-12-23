# Collectors module for Atlas Academic Search Engine
from .base import BaseCollector
from .arxiv_collector import ArxivCollector
from .ocw_collector import OCWCollector
from .stanford_collector import StanfordCollector
from .harvard_collector import HarvardCollector
from .yale_collector import YaleCollector
from .khan_collector import KhanAcademyCollector
from .openstax_collector import OpenStaxCollector

__all__ = [
    'BaseCollector',
    'ArxivCollector',
    'OCWCollector',
    'StanfordCollector',
    'HarvardCollector',
    'YaleCollector',
    'KhanAcademyCollector',
    'OpenStaxCollector',
]
