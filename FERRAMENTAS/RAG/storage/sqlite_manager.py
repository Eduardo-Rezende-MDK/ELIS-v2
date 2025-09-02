#!/usr/bin/env python3
"""
Gerenciador SQLite para persistência híbrida com FAISS
Armazena metadados estruturados enquanto FAISS gerencia vetores
"""

import sqlite3
import json
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.document import RawDocument, ProcessedChunk, SearchResult

class SQLiteManager:
    """Gerenciador SQLite para metadados do sistema RAG"""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or "rag_storage/rag_database.db"
        
        # Garantir que o diretório existe
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Inicializar banco
        self._init_database()
    
    def _init_database(self):
        """Inicializa o banco de dados com schema completo"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                -- Tabela de documentos originais
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    url TEXT,
                    authors TEXT, -- JSON array
                    publication_date TEXT, -- ISO format
                    abstract TEXT,
                    keywords TEXT, -- JSON array
                    language TEXT,
                    external_id TEXT,
                    quality_score REAL,
                    source_metadata TEXT, -- JSON
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                
                -- Tabela de chunks processados
                CREATE TABLE IF NOT EXISTS chunks (
                    id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL,
                    text TEXT NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    chunk_size INTEGER NOT NULL,
                    overlap_size INTEGER,
                    source_type TEXT NOT NULL,
                    document_title TEXT NOT NULL,
                    quality_score REAL,
                    embedding_norm REAL,
                    faiss_index INTEGER, -- Índice no FAISS
                    previous_chunk_id TEXT,
                    next_chunk_id TEXT,
                    metadata TEXT, -- JSON
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (document_id) REFERENCES documents (id) ON DELETE CASCADE
                );
                
                -- Tabela de histórico de buscas
                CREATE TABLE IF NOT EXISTS search_history (
                    id TEXT PRIMARY KEY,
                    query TEXT NOT NULL,
                    query_embedding_hash TEXT, -- Hash do embedding para cache
                    results_count INTEGER,
                    top_score REAL,
                    avg_score REAL,
                    execution_time_ms REAL,
                    filters_applied TEXT, -- JSON
                    results_summary TEXT, -- JSON com IDs dos chunks retornados
                    created_at TEXT NOT NULL
                );
                
                -- Tabela de configurações do sistema
                CREATE TABLE IF NOT EXISTS system_config (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    description TEXT,
                    updated_at TEXT NOT NULL
                );
                
                -- Índices para performance
                CREATE INDEX IF NOT EXISTS idx_documents_source_type ON documents(source_type);
                CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents(created_at);
                CREATE INDEX IF NOT EXISTS idx_documents_quality_score ON documents(quality_score);
                
                CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON chunks(document_id);
                CREATE INDEX IF NOT EXISTS idx_chunks_source_type ON chunks(source_type);
                CREATE INDEX IF NOT EXISTS idx_chunks_faiss_index ON chunks(faiss_index);
                CREATE INDEX IF NOT EXISTS idx_chunks_quality_score ON chunks(quality_score);
                CREATE INDEX IF NOT EXISTS idx_chunks_created_at ON chunks(created_at);
                
                CREATE INDEX IF NOT EXISTS idx_search_history_query ON search_history(query);
                CREATE INDEX IF NOT EXISTS idx_search_history_created_at ON search_history(created_at);
            """)
            
            # Inserir configurações padrão
            self._insert_default_config(conn)
    
    def _insert_default_config(self, conn: sqlite3.Connection):
        """Insere configurações padrão do sistema"""
        default_configs = [
            ('embedding_model', 'sentence-transformers/all-MiniLM-L6-v2', 'Modelo de embeddings usado'),
            ('embedding_dimension', '384', 'Dimensão dos embeddings'),
            ('faiss_index_type', 'flat', 'Tipo de índice FAISS'),
            ('chunk_size', '512', 'Tamanho padrão dos chunks'),
            ('chunk_overlap', '50', 'Overlap entre chunks'),
            ('quality_threshold', '0.4', 'Threshold mínimo de qualidade'),
            ('similarity_threshold', '0.5', 'Threshold mínimo de similaridade'),
            ('system_version', '2.0', 'Versão do sistema RAG')
        ]
        
        for key, value, description in default_configs:
            conn.execute("""
                INSERT OR IGNORE INTO system_config (key, value, description, updated_at)
                VALUES (?, ?, ?, ?)
            """, (key, value, description, datetime.now().isoformat()))
    
    def insert_document(self, document: RawDocument) -> str:
        """Insere um documento no banco"""
        doc_id = document.document_id
        now = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO documents (
                    id, title, content, source_type, url, authors, publication_date,
                    abstract, keywords, language, external_id, quality_score,
                    source_metadata, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                doc_id, document.title, document.content, document.source_type,
                document.url, json.dumps(document.authors),
                document.publication_date.isoformat() if document.publication_date else None,
                document.abstract, json.dumps(document.keywords), document.language,
                document.external_id, document.quality_score,
                json.dumps(document.source_metadata), now, now
            ))
        
        return doc_id
    
    def insert_chunk(self, chunk: ProcessedChunk, faiss_index: int) -> str:
        """Insere um chunk no banco com referência ao índice FAISS"""
        chunk_id = chunk.chunk_id
        now = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            # Verificar se chunk já existe
            cursor = conn.execute("SELECT id FROM chunks WHERE id = ?", (chunk_id,))
            if cursor.fetchone():
                # Chunk já existe, não inserir novamente
                return chunk_id
            
            # Inserir novo chunk
            conn.execute("""
                INSERT INTO chunks (
                    id, document_id, text, chunk_index, chunk_size, overlap_size,
                    source_type, document_title, quality_score, embedding_norm,
                    faiss_index, previous_chunk_id, next_chunk_id, metadata,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                chunk_id, chunk.document_id, chunk.text, chunk.chunk_index,
                chunk.chunk_size, chunk.overlap_size, chunk.source_type,
                chunk.document_title, chunk.quality_score, chunk.embedding_norm,
                faiss_index, chunk.previous_chunk_id, chunk.next_chunk_id,
                json.dumps(chunk.metadata), now, now
            ))
        
        return chunk_id
    
    def get_chunk_by_faiss_index(self, faiss_index: int) -> Optional[ProcessedChunk]:
        """Recupera chunk pelo índice FAISS"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM chunks WHERE faiss_index = ?
            """, (faiss_index,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return self._row_to_chunk(row)
    
    def get_chunks_by_document(self, document_id: str) -> List[ProcessedChunk]:
        """Recupera todos os chunks de um documento"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM chunks WHERE document_id = ? ORDER BY chunk_index
            """, (document_id,))
            
            return [self._row_to_chunk(row) for row in cursor.fetchall()]
    
    def get_all_chunks(self) -> List[ProcessedChunk]:
        """Recupera todos os chunks do banco de dados"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM chunks 
                ORDER BY created_at ASC, chunk_index ASC
            """)
            
            return [self._row_to_chunk(row) for row in cursor.fetchall()]
    
    def search_chunks(self, filters: Dict[str, Any], limit: int = 100) -> List[ProcessedChunk]:
        """Busca chunks com filtros SQL"""
        where_clauses = []
        params = []
        
        # Construir filtros dinamicamente
        if 'source_type' in filters:
            where_clauses.append("source_type = ?")
            params.append(filters['source_type'])
        
        if 'quality_score_min' in filters:
            where_clauses.append("quality_score >= ?")
            params.append(filters['quality_score_min'])
        
        if 'document_id' in filters:
            where_clauses.append("document_id = ?")
            params.append(filters['document_id'])
        
        if 'created_after' in filters:
            where_clauses.append("created_at >= ?")
            params.append(filters['created_after'])
        
        # Construir query
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
        query = f"""
            SELECT * FROM chunks 
            WHERE {where_sql} 
            ORDER BY quality_score DESC, created_at DESC 
            LIMIT ?
        """
        params.append(limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            
            return [self._row_to_chunk(row) for row in cursor.fetchall()]
    
    def log_search(self, query: str, results: List[SearchResult], 
                   execution_time_ms: float, filters: Dict[str, Any] = None) -> str:
        """Registra uma busca no histórico"""
        search_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        # Calcular estatísticas
        results_count = len(results)
        top_score = max([r.score for r in results]) if results else 0.0
        avg_score = sum([r.score for r in results]) / len(results) if results else 0.0
        
        # Resumo dos resultados
        results_summary = {
            'chunk_ids': [r.chunk.chunk_id for r in results],
            'scores': [r.score for r in results],
            'sources': [r.chunk.source_type for r in results]
        }
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO search_history (
                    id, query, results_count, top_score, avg_score,
                    execution_time_ms, filters_applied, results_summary, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                search_id, query, results_count, top_score, avg_score,
                execution_time_ms, json.dumps(filters or {}),
                json.dumps(results_summary), now
            ))
        
        return search_id
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtem estatísticas completas do banco"""
        with sqlite3.connect(self.db_path) as conn:
            # Estatísticas de documentos
            doc_stats = conn.execute("""
                SELECT 
                    COUNT(*) as total_documents,
                    COUNT(DISTINCT source_type) as unique_sources,
                    AVG(quality_score) as avg_quality,
                    MIN(created_at) as oldest_document,
                    MAX(created_at) as newest_document
                FROM documents
            """).fetchone()
            
            # Estatísticas de chunks
            chunk_stats = conn.execute("""
                SELECT 
                    COUNT(*) as total_chunks,
                    AVG(chunk_size) as avg_chunk_size,
                    AVG(quality_score) as avg_quality,
                    COUNT(DISTINCT document_id) as documents_with_chunks
                FROM chunks
            """).fetchone()
            
            # Distribuição por fonte
            source_dist = conn.execute("""
                SELECT source_type, COUNT(*) as count
                FROM chunks
                GROUP BY source_type
                ORDER BY count DESC
            """).fetchall()
            
            # Estatísticas de busca
            search_stats = conn.execute("""
                SELECT 
                    COUNT(*) as total_searches,
                    AVG(execution_time_ms) as avg_execution_time,
                    AVG(results_count) as avg_results_count,
                    AVG(top_score) as avg_top_score
                FROM search_history
                WHERE created_at >= datetime('now', '-30 days')
            """).fetchone()
            
            return {
                'documents': {
                    'total': doc_stats[0],
                    'unique_sources': doc_stats[1],
                    'avg_quality': doc_stats[2],
                    'oldest': doc_stats[3],
                    'newest': doc_stats[4]
                },
                'chunks': {
                    'total': chunk_stats[0],
                    'avg_size': chunk_stats[1],
                    'avg_quality': chunk_stats[2],
                    'documents_processed': chunk_stats[3]
                },
                'source_distribution': dict(source_dist),
                'search_performance': {
                    'total_searches_30d': search_stats[0],
                    'avg_execution_time_ms': search_stats[1],
                    'avg_results_count': search_stats[2],
                    'avg_top_score': search_stats[3]
                }
            }
    
    def _row_to_chunk(self, row: sqlite3.Row) -> ProcessedChunk:
        """Converte row do SQLite para ProcessedChunk"""
        # Criar embedding vazio (será preenchido pelo FAISS)
        import numpy as np
        
        chunk = ProcessedChunk(
            text=row['text'],
            embedding=np.array([]),  # Será carregado do FAISS
            document_id=row['document_id'],
            chunk_index=row['chunk_index'],
            source_type=row['source_type'],
            document_title=row['document_title'],
            chunk_size=row['chunk_size'],
            overlap_size=row['overlap_size'],
            metadata=json.loads(row['metadata']) if row['metadata'] else {}
        )
        
        # Definir IDs e scores
        chunk.chunk_id = row['id']
        chunk.quality_score = row['quality_score']
        chunk.embedding_norm = row['embedding_norm']
        chunk.previous_chunk_id = row['previous_chunk_id']
        chunk.next_chunk_id = row['next_chunk_id']
        
        return chunk
    
    def cleanup_old_searches(self, days: int = 30):
        """Remove buscas antigas do histórico"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                DELETE FROM search_history 
                WHERE created_at < datetime('now', '-{} days')
            """.format(days))
            
            return cursor.rowcount
    
    def vacuum_database(self):
        """Otimiza o banco de dados"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("VACUUM")
    
    def get_config(self, key: str) -> Optional[str]:
        """Obtem valor de configuração"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT value FROM system_config WHERE key = ?", (key,)
            )
            row = cursor.fetchone()
            return row[0] if row else None
    
    def set_config(self, key: str, value: str, description: str = None):
        """Define valor de configuração"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO system_config (key, value, description, updated_at)
                VALUES (?, ?, ?, ?)
            """, (key, value, description, datetime.now().isoformat()))
    
    def close(self):
        """Fecha todas as conexões SQLite abertas"""
        try:
            # Forçar fechamento de todas as conexões
            import gc
            gc.collect()  # Força garbage collection
            
            # Tentar fechar conexão explicitamente se existir
            if hasattr(self, '_connection'):
                if self._connection:
                    self._connection.close()
                    self._connection = None
            
            print("Conexões SQLite fechadas")
        except Exception as e:
            print(f"Erro ao fechar conexões SQLite: {e}")