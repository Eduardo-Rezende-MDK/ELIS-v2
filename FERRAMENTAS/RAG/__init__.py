#!/usr/bin/env python3
"""
Sistema RAG Simplificado
Sistema completo de Retrieval-Augmented Generation
"""

__version__ = "1.0.0"
__author__ = "ELIS v2"

from .models.document import RawDocument, ProcessedChunk, SearchResult
from .sources.academic_collector import AcademicSourceCollector
from .sources.web_collector import WebSourceCollector
from .processing.document_processor import DocumentProcessor
from .processing.quality_filters import QualityFilter
from .storage.vector_store import RAGVectorStore
from .rag_pipeline import RAGPipeline

__all__ = [
    'RawDocument',
    'ProcessedChunk', 
    'SearchResult',
    'AcademicSourceCollector',
    'WebSourceCollector',
    'DocumentProcessor',
    'QualityFilter',
    'RAGVectorStore',
    'RAGPipeline'
]