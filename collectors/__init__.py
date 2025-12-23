# Collectors module for Atlas Course Materials Search Engine
from .base import BaseCollector
from .ocw_collector import OCWCollector
from .stanford_collector import StanfordCollector
from .harvard_collector import HarvardCollector
from .yale_collector import YaleCollector
from .waterloo_collector import WaterlooCollector
from .uoft_collector import UofTCollector
from .ubc_collector import UBCCollector
from .mcgill_collector import McGillCollector

__all__ = [
    'BaseCollector',
    'OCWCollector',
    'StanfordCollector',
    'HarvardCollector',
    'YaleCollector',
    'WaterlooCollector',
    'UofTCollector',
    'UBCCollector',
    'McGillCollector',
]
