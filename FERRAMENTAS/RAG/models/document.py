#!/usr/bin/env python3
"""
Modelos de dados para documentos e chunks do sistema RAG
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import numpy as np

@dataclass
class RawDocument:
    """Documento bruto coletado de uma fonte"""
    
    # Campos obrigatorios
    title: str
    content: str
    source_type: str  # 'wikipedia', 'arxiv', 'pubmed', etc.
    
    # Campos opcionais
    url: str = ""
    authors: List[str] = field(default_factory=list)
    publication_date: Optional[datetime] = None
    abstract: str = ""
    keywords: List[str] = field(default_factory=list)
    language: str = "pt"
    
    # Metadados
    collection_timestamp: datetime = field(default_factory=datetime.now)
    source_metadata: Dict[str, Any] = field(default_factory=dict)
    quality_score: float = 0.0
    
    # Identificadores
    document_id: str = ""
    external_id: str = ""  # DOI, ArXiv ID, etc.
    
    def __post_init__(self):
        """Validacao e processamento pos-inicializacao"""
        if not self.document_id:
            # Gerar ID baseado em hash do conteudo
            import hashlib
            content_hash = hashlib.md5(f"{self.title}{self.content}".encode()).hexdigest()[:12]
            self.document_id = f"{self.source_type}_{content_hash}"
    
    @property
    def content_length(self) -> int:
        """Tamanho do conteudo em caracteres"""
        return len(self.content)
    
    @property
    def word_count(self) -> int:
        """Numero de palavras no conteudo"""
        return len(self.content.split())
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionario"""
        return {
            'document_id': self.document_id,
            'title': self.title,
            'content': self.content,
            'source_type': self.source_type,
            'url': self.url,
            'authors': self.authors,
            'publication_date': self.publication_date.isoformat() if self.publication_date else None,
            'abstract': self.abstract,
            'keywords': self.keywords,
            'language': self.language,
            'collection_timestamp': self.collection_timestamp.isoformat(),
            'source_metadata': self.source_metadata,
            'quality_score': self.quality_score,
            'external_id': self.external_id,
            'content_length': self.content_length,
            'word_count': self.word_count
        }

@dataclass
class ProcessedChunk:
    """Chunk processado de um documento"""
    
    # Campos obrigatorios
    text: str
    embedding: np.ndarray
    document_id: str
    chunk_index: int
    
    # Campos opcionais
    chunk_id: str = ""
    source_type: str = ""
    document_title: str = ""
    
    # Metadados de processamento
    processing_timestamp: datetime = field(default_factory=datetime.now)
    chunk_size: int = 0
    overlap_size: int = 0
    
    # Metricas de qualidade
    quality_score: float = 0.0
    embedding_norm: float = 0.0
    
    # Contexto
    previous_chunk_id: str = ""
    next_chunk_id: str = ""
    
    # Metadados adicionais
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Processamento pos-inicializacao"""
        if not self.chunk_id:
            self.chunk_id = f"{self.document_id}_chunk_{self.chunk_index}"
        
        if self.chunk_size == 0:
            self.chunk_size = len(self.text)
            
        if self.embedding_norm == 0.0 and self.embedding is not None:
            self.embedding_norm = float(np.linalg.norm(self.embedding))
    
    @property
    def word_count(self) -> int:
        """Numero de palavras no chunk"""
        return len(self.text.split())
    
    def calculate_similarity(self, other_embedding: np.ndarray) -> float:
        """Calcula similaridade coseno com outro embedding"""
        if self.embedding is None or other_embedding is None:
            return 0.0
            
        dot_product = np.dot(self.embedding, other_embedding)
        norm_product = np.linalg.norm(self.embedding) * np.linalg.norm(other_embedding)
        
        if norm_product == 0:
            return 0.0
            
        return float(dot_product / norm_product)
    
    def to_dict(self, include_embedding: bool = False) -> Dict[str, Any]:
        """Converte para dicionario"""
        result = {
            'chunk_id': self.chunk_id,
            'text': self.text,
            'document_id': self.document_id,
            'chunk_index': self.chunk_index,
            'source_type': self.source_type,
            'document_title': self.document_title,
            'processing_timestamp': self.processing_timestamp.isoformat(),
            'chunk_size': self.chunk_size,
            'overlap_size': self.overlap_size,
            'quality_score': self.quality_score,
            'embedding_norm': self.embedding_norm,
            'previous_chunk_id': self.previous_chunk_id,
            'next_chunk_id': self.next_chunk_id,
            'metadata': self.metadata,
            'word_count': self.word_count
        }
        
        if include_embedding and self.embedding is not None:
            result['embedding'] = self.embedding.tolist()
            
        return result

@dataclass
class SearchResult:
    """Resultado de uma busca no sistema RAG"""
    
    # Campos obrigatorios
    chunk: ProcessedChunk
    score: float
    query: str
    
    # Campos opcionais
    rank: int = 0
    search_timestamp: datetime = field(default_factory=datetime.now)
    search_type: str = "semantic"  # 'semantic', 'keyword', 'hybrid'
    
    # Contexto adicional
    context_chunks: List[ProcessedChunk] = field(default_factory=list)
    highlighted_text: str = ""
    
    # Metadados de busca
    search_metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def content(self) -> str:
        """Conteudo do chunk principal"""
        return self.chunk.text
    
    @property
    def document_title(self) -> str:
        """Titulo do documento de origem"""
        return self.chunk.document_title
    
    @property
    def source_type(self) -> str:
        """Tipo de fonte do documento"""
        return self.chunk.source_type
    
    @property
    def document_id(self) -> str:
        """ID do documento de origem"""
        return self.chunk.document_id
    
    def get_extended_context(self, max_chars: int = 1000) -> str:
        """Obtem contexto estendido incluindo chunks adjacentes"""
        context_parts = [self.chunk.text]
        
        # Adicionar contexto dos chunks adjacentes
        for context_chunk in self.context_chunks:
            if len(' '.join(context_parts)) + len(context_chunk.text) <= max_chars:
                context_parts.append(context_chunk.text)
            else:
                break
                
        return ' '.join(context_parts)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionario"""
        return {
            'rank': self.rank,
            'score': self.score,
            'query': self.query,
            'search_timestamp': self.search_timestamp.isoformat(),
            'search_type': self.search_type,
            'content': self.content,
            'document_title': self.document_title,
            'source_type': self.source_type,
            'document_id': self.document_id,
            'chunk_id': self.chunk.chunk_id,
            'chunk_index': self.chunk.chunk_index,
            'highlighted_text': self.highlighted_text,
            'context_chunks_count': len(self.context_chunks),
            'search_metadata': self.search_metadata
        }

# Funcoes utilitarias

def create_raw_document_from_dict(data: Dict[str, Any]) -> RawDocument:
    """Cria RawDocument a partir de dicionario"""
    # Converter data de publicacao se presente
    pub_date = None
    if data.get('publication_date'):
        try:
            pub_date = datetime.fromisoformat(data['publication_date'])
        except (ValueError, TypeError):
            pass
    
    # Converter timestamp de coleta se presente
    collection_ts = datetime.now()
    if data.get('collection_timestamp'):
        try:
            collection_ts = datetime.fromisoformat(data['collection_timestamp'])
        except (ValueError, TypeError):
            pass
    
    return RawDocument(
        title=data.get('title', ''),
        content=data.get('content', ''),
        source_type=data.get('source_type', ''),
        url=data.get('url', ''),
        authors=data.get('authors', []),
        publication_date=pub_date,
        abstract=data.get('abstract', ''),
        keywords=data.get('keywords', []),
        language=data.get('language', 'pt'),
        collection_timestamp=collection_ts,
        source_metadata=data.get('source_metadata', {}),
        quality_score=data.get('quality_score', 0.0),
        document_id=data.get('document_id', ''),
        external_id=data.get('external_id', '')
    )

def create_processed_chunk_from_dict(data: Dict[str, Any]) -> ProcessedChunk:
    """Cria ProcessedChunk a partir de dicionario"""
    # Converter embedding se presente
    embedding = None
    if data.get('embedding'):
        try:
            embedding = np.array(data['embedding'])
        except (ValueError, TypeError):
            pass
    
    # Converter timestamp se presente
    processing_ts = datetime.now()
    if data.get('processing_timestamp'):
        try:
            processing_ts = datetime.fromisoformat(data['processing_timestamp'])
        except (ValueError, TypeError):
            pass
    
    return ProcessedChunk(
        text=data.get('text', ''),
        embedding=embedding,
        document_id=data.get('document_id', ''),
        chunk_index=data.get('chunk_index', 0),
        chunk_id=data.get('chunk_id', ''),
        source_type=data.get('source_type', ''),
        document_title=data.get('document_title', ''),
        processing_timestamp=processing_ts,
        chunk_size=data.get('chunk_size', 0),
        overlap_size=data.get('overlap_size', 0),
        quality_score=data.get('quality_score', 0.0),
        embedding_norm=data.get('embedding_norm', 0.0),
        previous_chunk_id=data.get('previous_chunk_id', ''),
        next_chunk_id=data.get('next_chunk_id', ''),
        metadata=data.get('metadata', {})
    )