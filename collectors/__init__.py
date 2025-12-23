# Collectors module for Atlas Academic Search Engine
from .base import BaseCollector
from .arxiv_collector import ArxivCollector
from .ocw_collector import OCWCollector

__all__ = ['BaseCollector', 'ArxivCollector', 'OCWCollector']
