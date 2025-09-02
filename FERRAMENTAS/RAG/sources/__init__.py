#!/usr/bin/env python3
"""
Coletores de dados de diferentes fontes
"""

from .academic_collector import AcademicSourceCollector
from .web_collector import WebSourceCollector
from .document_collector import DocumentCollector
from .api_collector import APICollector

__all__ = [
    'AcademicSourceCollector',
    'WebSourceCollector', 
    'DocumentCollector',
    'APICollector'
]