#!/usr/bin/env python3
"""
Sistema de armazenamento vetorial com FAISS
"""

import faiss
import numpy as np
import pickle
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from ..models.document import ProcessedChunk, SearchResult

class RAGVectorStore:
    """Sistema de armazenamento vetorial para chunks processados"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Configuracoes do indice FAISS
        self.embedding_dim = self.config.get('embedding_dim', 384)
        self.index_type = self.config.get('index_type', 'flat')  # 'flat', 'ivf', 'hnsw'
        self.metric_type = self.config.get('metric_type', faiss.METRIC_INNER_PRODUCT)
        
        # Configuracoes especificas para IVF
        self.nlist = self.config.get('nlist', 100)  # Numero de clusters
        self.nprobe = self.config.get('nprobe', 10)  # Numero de clusters a buscar
        
        # Configuracoes especificas para HNSW
        self.hnsw_m = self.config.get('hnsw_m', 32)
        self.hnsw_ef_construction = self.config.get('hnsw_ef_construction', 200)
        self.hnsw_ef_search = self.config.get('hnsw_ef_search', 50)
        
        # Configuracoes de armazenamento
        self.storage_path = Path(self.config.get('storage_path', './rag_storage'))
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Configuracoes de busca
        self.default_top_k = self.config.get('default_top_k', 10)
        self.max_top_k = self.config.get('max_top_k', 100)
        self.similarity_threshold = self.config.get('similarity_threshold', 0.5)
        
        # Inicializar componentes
        self.index = None
        self.chunks = []  # Lista de chunks armazenados
        self.chunk_metadata = {}  # Metadados dos chunks por ID
        
        # Estatisticas
        self.stats = {
            'total_chunks': 0,
            'total_documents': 0,
            'index_size': 0,
            'last_updated': None,
            'search_count': 0
        }
        
        # Tentar carregar indice existente
        self._load_existing_index()
    
    def _create_index(self, dimension: int) -> faiss.Index:
        """Cria indice FAISS baseado na configuracao"""
        if self.index_type == 'flat':
            # Indice plano (busca exaustiva)
            index = faiss.IndexFlatIP(dimension)  # Inner Product (cosine similarity)
            
        elif self.index_type == 'ivf':
            # Indice IVF (Inverted File)
            quantizer = faiss.IndexFlatIP(dimension)
            index = faiss.IndexIVFFlat(quantizer, dimension, self.nlist)
            index.nprobe = self.nprobe
            
        elif self.index_type == 'hnsw':
            # Indice HNSW (Hierarchical Navigable Small World)
            index = faiss.IndexHNSWFlat(dimension, self.hnsw_m)
            index.hnsw.efConstruction = self.hnsw_ef_construction
            index.hnsw.efSearch = self.hnsw_ef_search
            
        else:
            raise ValueError(f"Tipo de indice nao suportado: {self.index_type}")
        
        return index
    
    def add_chunks(self, chunks: List[ProcessedChunk]) -> bool:
        """Adiciona chunks ao vector store"""
        if not chunks:
            return False
        
        try:
            # Extrair embeddings
            embeddings = np.array([chunk.embedding for chunk in chunks]).astype('float32')
            
            # Normalizar embeddings para similaridade coseno
            faiss.normalize_L2(embeddings)
            
            # Criar indice se nao existir
            if self.index is None:
                self.embedding_dim = embeddings.shape[1]
                self.index = self._create_index(self.embedding_dim)
                
                # Treinar indice se necessario (IVF)
                if self.index_type == 'ivf' and not self.index.is_trained:
                    print(f"Treinando indice IVF com {len(embeddings)} embeddings...")
                    self.index.train(embeddings)
            
            # Adicionar embeddings ao indice
            start_id = len(self.chunks)
            self.index.add(embeddings)
            
            # Armazenar chunks e metadados
            for i, chunk in enumerate(chunks):
                chunk_id = start_id + i
                self.chunks.append(chunk)
                self.chunk_metadata[chunk.chunk_id] = {
                    'internal_id': chunk_id,
                    'chunk': chunk,
                    'added_timestamp': datetime.now().isoformat()
                }
            
            # Atualizar estatisticas
            self._update_stats()
            
            print(f"Adicionados {len(chunks)} chunks ao vector store")
            print(f"Total de chunks: {len(self.chunks)}")
            
            return True
            
        except Exception as e:
            print(f"Erro ao adicionar chunks: {e}")
            return False
    
    def search(self, query_embedding: np.ndarray, top_k: int = None, 
              filters: Dict[str, Any] = None) -> List[SearchResult]:
        """Busca chunks similares usando embedding da query"""
        if self.index is None or len(self.chunks) == 0:
            return []
        
        top_k = min(top_k or self.default_top_k, self.max_top_k, len(self.chunks))
        
        try:
            # Normalizar query embedding
            query_embedding = query_embedding.astype('float32').reshape(1, -1)
            faiss.normalize_L2(query_embedding)
            
            # Buscar no indice FAISS
            scores, indices = self.index.search(query_embedding, top_k)
            
            # Converter resultados
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx == -1:  # FAISS retorna -1 para resultados invalidos
                    continue
                    
                chunk = self.chunks[idx]
                
                # Aplicar filtros se especificados
                if filters and not self._apply_filters(chunk, filters):
                    continue
                
                # Aplicar threshold de similaridade
                if score < self.similarity_threshold:
                    continue
                
                # Criar resultado
                search_result = SearchResult(
                    chunk=chunk,
                    score=float(score),
                    query="",  # Query sera definida externamente
                    rank=i + 1,
                    search_type="semantic",
                    search_metadata={
                        'faiss_index': int(idx),
                        'original_score': float(score),
                        'index_type': self.index_type
                    }
                )
                
                results.append(search_result)
            
            # Atualizar estatisticas
            self.stats['search_count'] += 1
            
            return results
            
        except Exception as e:
            print(f"Erro na busca: {e}")
            return []
    
    def search_with_context(self, query_embedding: np.ndarray, top_k: int = None,
                           context_window: int = 1) -> List[SearchResult]:
        """Busca com contexto de chunks adjacentes"""
        results = self.search(query_embedding, top_k)
        
        # Adicionar contexto para cada resultado
        for result in results:
            context_chunks = self._get_context_chunks(result.chunk, context_window)
            result.context_chunks = context_chunks
        
        return results
    
    def _get_context_chunks(self, chunk: ProcessedChunk, window: int) -> List[ProcessedChunk]:
        """Obtem chunks de contexto adjacentes"""
        context_chunks = []
        
        # Buscar chunks do mesmo documento
        document_chunks = [c for c in self.chunks if c.document_id == chunk.document_id]
        document_chunks.sort(key=lambda x: x.chunk_index)
        
        # Encontrar posicao do chunk atual
        current_idx = None
        for i, doc_chunk in enumerate(document_chunks):
            if doc_chunk.chunk_id == chunk.chunk_id:
                current_idx = i
                break
        
        if current_idx is not None:
            # Adicionar chunks anteriores e posteriores
            start_idx = max(0, current_idx - window)
            end_idx = min(len(document_chunks), current_idx + window + 1)
            
            for i in range(start_idx, end_idx):
                if i != current_idx:  # Nao incluir o chunk principal
                    context_chunks.append(document_chunks[i])
        
        return context_chunks
    
    def _apply_filters(self, chunk: ProcessedChunk, filters: Dict[str, Any]) -> bool:
        """Aplica filtros a um chunk"""
        # Filtro por tipo de fonte
        if 'source_type' in filters:
            allowed_sources = filters['source_type']
            if isinstance(allowed_sources, str):
                allowed_sources = [allowed_sources]
            if chunk.source_type not in allowed_sources:
                return False
        
        # Filtro por score de qualidade
        if 'quality_score' in filters:
            quality_filter = filters['quality_score']
            if isinstance(quality_filter, dict):
                min_score = quality_filter.get('min', 0)
                max_score = quality_filter.get('max', 1)
                if not (min_score <= chunk.quality_score <= max_score):
                    return False
            elif isinstance(quality_filter, (int, float)):
                if chunk.quality_score < quality_filter:
                    return False
        
        # Filtro por documento
        if 'document_id' in filters:
            allowed_docs = filters['document_id']
            if isinstance(allowed_docs, str):
                allowed_docs = [allowed_docs]
            if chunk.document_id not in allowed_docs:
                return False
        
        # Filtro por tamanho do chunk
        if 'chunk_size' in filters:
            size_filter = filters['chunk_size']
            if isinstance(size_filter, dict):
                min_size = size_filter.get('min', 0)
                max_size = size_filter.get('max', float('inf'))
                if not (min_size <= chunk.chunk_size <= max_size):
                    return False
        
        return True
    
    def get_chunk_by_id(self, chunk_id: str) -> Optional[ProcessedChunk]:
        """Obtem chunk por ID"""
        metadata = self.chunk_metadata.get(chunk_id)
        return metadata['chunk'] if metadata else None
    
    def get_chunks_by_document(self, document_id: str) -> List[ProcessedChunk]:
        """Obtem todos os chunks de um documento"""
        return [chunk for chunk in self.chunks if chunk.document_id == document_id]
    
    def remove_chunks_by_document(self, document_id: str) -> int:
        """Remove todos os chunks de um documento"""
        # Esta operacao e complexa com FAISS, pois nao suporta remocao direta
        # Por simplicidade, vamos apenas marcar como removidos
        removed_count = 0
        
        for chunk in self.chunks:
            if chunk.document_id == document_id:
                # Marcar como removido nos metadados
                if chunk.chunk_id in self.chunk_metadata:
                    self.chunk_metadata[chunk.chunk_id]['removed'] = True
                    removed_count += 1
        
        print(f"Marcados {removed_count} chunks para remocao (documento: {document_id})")
        print("Nota: Para remocao fisica, reconstrua o indice")
        
        return removed_count
    
    def rebuild_index(self) -> bool:
        """Reconstroi o indice removendo chunks marcados para remocao"""
        try:
            # Filtrar chunks nao removidos
            active_chunks = []
            for chunk in self.chunks:
                metadata = self.chunk_metadata.get(chunk.chunk_id, {})
                if not metadata.get('removed', False):
                    active_chunks.append(chunk)
            
            if not active_chunks:
                print("Nenhum chunk ativo encontrado")
                return False
            
            # Limpar estado atual
            self.index = None
            self.chunks = []
            self.chunk_metadata = {}
            
            # Readicionar chunks ativos
            success = self.add_chunks(active_chunks)
            
            if success:
                print(f"Indice reconstruido com {len(active_chunks)} chunks")
            
            return success
            
        except Exception as e:
            print(f"Erro ao reconstruir indice: {e}")
            return False
    
    def save_index(self, path: Optional[str] = None) -> bool:
        """Salva indice e metadados em disco"""
        try:
            save_path = Path(path) if path else self.storage_path
            save_path.mkdir(parents=True, exist_ok=True)
            
            # Salvar indice FAISS
            if self.index is not None:
                index_file = save_path / "faiss_index.bin"
                faiss.write_index(self.index, str(index_file))
            
            # Salvar chunks
            chunks_file = save_path / "chunks.pkl"
            with open(chunks_file, 'wb') as f:
                pickle.dump(self.chunks, f)
            
            # Salvar metadados
            metadata_file = save_path / "metadata.json"
            # Converter chunks para dict para serializacao JSON
            serializable_metadata = {}
            for chunk_id, metadata in self.chunk_metadata.items():
                serializable_metadata[chunk_id] = {
                    'internal_id': metadata['internal_id'],
                    'added_timestamp': metadata['added_timestamp'],
                    'removed': metadata.get('removed', False)
                }
            
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'chunk_metadata': serializable_metadata,
                    'stats': self.stats,
                    'config': self.config
                }, f, indent=2, ensure_ascii=False)
            
            print(f"Indice salvo em: {save_path}")
            return True
            
        except Exception as e:
            print(f"Erro ao salvar indice: {e}")
            return False
    
    def _load_existing_index(self) -> bool:
        """Carrega indice existente se disponivel"""
        try:
            index_file = self.storage_path / "faiss_index.bin"
            chunks_file = self.storage_path / "chunks.pkl"
            metadata_file = self.storage_path / "metadata.json"
            
            if not all(f.exists() for f in [index_file, chunks_file, metadata_file]):
                return False
            
            # Carregar indice FAISS
            self.index = faiss.read_index(str(index_file))
            
            # Carregar chunks
            with open(chunks_file, 'rb') as f:
                self.chunks = pickle.load(f)
            
            # Carregar metadados
            with open(metadata_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Reconstruir metadados com objetos chunk
                self.chunk_metadata = {}
                for chunk_id, metadata in data.get('chunk_metadata', {}).items():
                    # Encontrar chunk correspondente
                    chunk = next((c for c in self.chunks if c.chunk_id == chunk_id), None)
                    if chunk:
                        self.chunk_metadata[chunk_id] = {
                            'internal_id': metadata['internal_id'],
                            'chunk': chunk,
                            'added_timestamp': metadata['added_timestamp'],
                            'removed': metadata.get('removed', False)
                        }
                
                self.stats = data.get('stats', self.stats)
            
            print(f"Indice carregado: {len(self.chunks)} chunks")
            return True
            
        except Exception as e:
            print(f"Erro ao carregar indice existente: {e}")
            return False
    
    def _update_stats(self):
        """Atualiza estatisticas do vector store"""
        self.stats['total_chunks'] = len(self.chunks)
        self.stats['total_documents'] = len(set(chunk.document_id for chunk in self.chunks))
        self.stats['index_size'] = self.index.ntotal if self.index else 0
        self.stats['last_updated'] = datetime.now().isoformat()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtem estatisticas do vector store"""
        # Atualizar estatisticas
        self._update_stats()
        
        # Distribuicao por fonte
        source_distribution = {}
        for chunk in self.chunks:
            source_distribution[chunk.source_type] = source_distribution.get(chunk.source_type, 0) + 1
        
        # Distribuicao por documento
        document_distribution = {}
        for chunk in self.chunks:
            document_distribution[chunk.document_id] = document_distribution.get(chunk.document_id, 0) + 1
        
        # Metricas de qualidade
        quality_scores = [chunk.quality_score for chunk in self.chunks]
        embedding_norms = [chunk.embedding_norm for chunk in self.chunks]
        
        return {
            'basic_stats': self.stats,
            'source_distribution': source_distribution,
            'document_distribution': document_distribution,
            'quality_metrics': {
                'avg_quality_score': np.mean(quality_scores) if quality_scores else 0,
                'min_quality_score': min(quality_scores) if quality_scores else 0,
                'max_quality_score': max(quality_scores) if quality_scores else 0,
                'avg_embedding_norm': np.mean(embedding_norms) if embedding_norms else 0
            },
            'index_info': {
                'type': self.index_type,
                'dimension': self.embedding_dim,
                'metric_type': 'inner_product',
                'total_vectors': self.index.ntotal if self.index else 0
            }
        }
    
    def clear_all(self):
        """Limpa todo o conteudo do vector store"""
        self.index = None
        self.chunks = []
        self.chunk_metadata = {}
        self.stats = {
            'total_chunks': 0,
            'total_documents': 0,
            'index_size': 0,
            'last_updated': None,
            'search_count': 0
        }
        print("Vector store limpo")