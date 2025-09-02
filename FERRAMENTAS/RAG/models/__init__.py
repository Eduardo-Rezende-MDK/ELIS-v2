#!/usr/bin/env python3
"""
Modelos de dados para o sistema RAG
"""

from .document import RawDocument, ProcessedChunk, SearchResult

__all__ = ['RawDocument', 'ProcessedChunk', 'SearchResult']