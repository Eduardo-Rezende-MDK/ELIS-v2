#!/usr/bin/env python3
"""
Sistema de armazenamento vetorial com FAISS
Versão simplificada sem SQLite - apenas FAISS + arquivos
"""

import faiss
import numpy as np
import pickle
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.document import ProcessedChunk, SearchResult

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
        self.chunks = []  # Cache local dos chunks
        self.chunk_metadata = {}  # Metadados dos chunks
        
        # Arquivos de persistência
        self.index_file = self.storage_path / 'faiss_index.bin'
        self.chunks_file = self.storage_path / 'chunks.pkl'
        self.metadata_file = self.storage_path / 'metadata.json'
        
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
            # Filtrar chunks que já existem
            new_chunks = []
            new_embeddings = []
            
            for chunk in chunks:
                if chunk.chunk_id not in self.chunk_metadata:
                    new_chunks.append(chunk)
                    new_embeddings.append(chunk.embedding)
            
            if not new_chunks:
                print("Todos os chunks já existem")
                return True
            
            # Extrair embeddings apenas dos chunks novos
            embeddings = np.array(new_embeddings).astype('float32')
            
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
            
            # Obter próximo índice interno
            current_size = len(self.chunks)
            
            # Adicionar embeddings ao indice FAISS
            self.index.add(embeddings)
            
            # Armazenar chunks e metadados
            for i, chunk in enumerate(new_chunks):
                internal_id = current_size + i
                
                # Adicionar ao cache local
                self.chunks.append(chunk)
                
                # Adicionar metadados
                self.chunk_metadata[chunk.chunk_id] = {
                    'internal_id': internal_id,
                    'chunk': chunk,
                    'added_timestamp': datetime.now().isoformat()
                }
            
            # Atualizar estatisticas
            self._update_stats()
            
            print(f"Adicionados {len(new_chunks)} chunks ao vector store")
            print(f"Total de chunks: {len(self.chunks)}")
            
            return True
            
        except Exception as e:
            print(f"Erro ao adicionar chunks: {e}")
            return False
    
    def search(self, query_embedding: np.ndarray, top_k: int = None, 
              filters: Dict[str, Any] = None) -> List[SearchResult]:
        """Busca chunks similares usando embedding da query"""
        if self.index is None or self.index.ntotal == 0:
            return []
        
        top_k = min(top_k or self.default_top_k, self.max_top_k, self.index.ntotal)
        
        try:
            start_time = datetime.now()
            
            # Normalizar query embedding
            query_embedding = query_embedding.astype('float32').reshape(1, -1)
            faiss.normalize_L2(query_embedding)
            
            # Buscar no indice FAISS
            scores, indices = self.index.search(query_embedding, top_k * 2)  # Buscar mais para filtrar
            
            # Converter resultados
            results = []
            for i, (score, faiss_idx) in enumerate(zip(scores[0], indices[0])):
                if faiss_idx == -1:  # FAISS retorna -1 para resultados invalidos
                    continue
                
                # Aplicar threshold de similaridade
                if score < self.similarity_threshold:
                    continue
                
                # Obter chunk do cache local
                chunk = self._get_chunk_by_index(int(faiss_idx))
                if not chunk:
                    continue
                
                # Aplicar filtros se especificados
                if filters and not self._apply_filters(filters, chunk):
                    continue
                
                # Criar resultado
                search_result = SearchResult(
                    chunk=chunk,
                    score=float(score),
                    query="",  # Query sera definida externamente
                    rank=len(results) + 1,
                    search_type="semantic",
                    search_metadata={
                        'faiss_index': int(faiss_idx),
                        'original_score': float(score),
                        'index_type': self.index_type
                    }
                )
                
                results.append(search_result)
                
                # Parar quando atingir top_k
                if len(results) >= top_k:
                    break
            
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
    
    def _get_chunk_by_index(self, index: int) -> Optional[ProcessedChunk]:
        """Obtem chunk pelo índice interno"""
        if 0 <= index < len(self.chunks):
            return self.chunks[index]
        return None
    
    def _apply_filters(self, filters: Dict[str, Any], chunk: ProcessedChunk) -> bool:
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
        if metadata:
            return metadata['chunk']
        return None
    
    def get_chunks_by_document(self, document_id: str) -> List[ProcessedChunk]:
        """Obtem todos os chunks de um documento"""
        chunks = []
        for chunk in self.chunks:
            if chunk.document_id == document_id:
                chunks.append(chunk)
        return chunks
    
    def remove_chunks_by_document(self, document_id: str) -> int:
        """Remove todos os chunks de um documento"""
        try:
            removed_count = 0
            chunks_to_keep = []
            
            # Filtrar chunks
            for chunk in self.chunks:
                if chunk.document_id == document_id:
                    removed_count += 1
                    # Remover dos metadados
                    if chunk.chunk_id in self.chunk_metadata:
                        del self.chunk_metadata[chunk.chunk_id]
                else:
                    chunks_to_keep.append(chunk)
            
            # Atualizar lista de chunks
            self.chunks = chunks_to_keep
            
            if removed_count > 0:
                print(f"Removidos {removed_count} chunks do documento {document_id}")
                print("Reconstruindo índice FAISS...")
                self.rebuild_index()
            
            return removed_count
            
        except Exception as e:
            print(f"Erro ao remover chunks do documento {document_id}: {e}")
            return 0
    
    def rebuild_index(self) -> bool:
        """Reconstrói índice FAISS a partir dos chunks válidos"""
        try:
            print("Reconstruindo índice FAISS...")
            
            if not self.chunks:
                print("Nenhum chunk encontrado para reconstrução")
                self.index = self._create_index(self.embedding_dim)
                return True
            
            # Filtrar chunks com embeddings válidos
            valid_chunks = [chunk for chunk in self.chunks if chunk.embedding and len(chunk.embedding) > 0]
            
            if not valid_chunks:
                print("Nenhum chunk com embeddings válidos encontrado")
                self.index = self._create_index(self.embedding_dim)
                return True
            
            print(f"Reconstruindo com {len(valid_chunks)} chunks válidos")
            
            # Criar novo índice
            self.index = self._create_index(self.embedding_dim)
            
            # Preparar embeddings
            embeddings = np.array([chunk.embedding for chunk in valid_chunks], dtype=np.float32)
            
            # Treinar índice se necessário
            if hasattr(self.index, 'is_trained') and not self.index.is_trained:
                self.index.train(embeddings)
            
            # Adicionar embeddings
            self.index.add(embeddings)
            
            # Atualizar chunks e metadados
            self.chunks = valid_chunks
            self.chunk_metadata = {}
            for i, chunk in enumerate(valid_chunks):
                self.chunk_metadata[chunk.chunk_id] = {
                    'internal_id': i,
                    'chunk': chunk,
                    'added_timestamp': datetime.now().isoformat()
                }
            
            # Salvar índice reconstruído
            self.save_index()
            
            print(f"Índice reconstruído com sucesso: {self.index.ntotal} vetores")
            return True
            
        except Exception as e:
            print(f"Erro ao reconstruir índice: {e}")
            return False
    
    def save_index(self, path: Optional[str] = None) -> bool:
        """Salva índice FAISS e dados no disco"""
        if self.index is None:
            print("Nenhum índice para salvar")
            return False
        
        try:
            # Salvar índice FAISS
            index_path = path or str(self.index_file)
            faiss.write_index(self.index, index_path)
            
            # Salvar chunks
            with open(self.chunks_file, 'wb') as f:
                pickle.dump(self.chunks, f)
            
            # Salvar metadados
            metadata = {
                'chunk_metadata': self.chunk_metadata,
                'stats': self.stats,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            print(f"Dados salvos: {len(self.chunks)} chunks")
            return True
        except Exception as e:
            print(f"Erro ao salvar dados: {e}")
            return False
    
    def _load_existing_index(self) -> bool:
        """Carrega indice FAISS existente"""
        try:
            # Verificar se arquivos existem
            if not self.index_file.exists():
                print("Nenhum índice FAISS encontrado")
                return False
                
            if not self.chunks_file.exists():
                print("Nenhum arquivo de chunks encontrado")
                return False
            
            # Carregar indice FAISS
            self.index = faiss.read_index(str(self.index_file))
            print(f"Índice FAISS carregado: {self.index.ntotal} vetores")
            
            # Carregar chunks
            with open(self.chunks_file, 'rb') as f:
                self.chunks = pickle.load(f)
            
            # Carregar metadados se existir
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.chunk_metadata = data.get('chunk_metadata', {})
                    self.stats = data.get('stats', self.stats)
            
            # Reconstruir metadados se necessário
            if not self.chunk_metadata:
                for i, chunk in enumerate(self.chunks):
                    self.chunk_metadata[chunk.chunk_id] = {
                        'internal_id': i,
                        'chunk': chunk,
                        'added_timestamp': datetime.now().isoformat()
                    }
            
            # Atualizar estatísticas
            self._update_stats()
            
            print(f"Índice FAISS carregado com sucesso")
            return True
            
        except Exception as e:
            print(f"Erro ao carregar índice existente: {e}")
            import traceback
            traceback.print_exc()
            return False
    

    

    
    def _update_stats(self):
        """Atualiza estatisticas do vector store"""
        self.stats['total_chunks'] = self.index.ntotal if self.index else 0
        self.stats['total_documents'] = 0  # Será obtido do SQLite quando necessário
        self.stats['index_size'] = self.index.ntotal if self.index else 0
        self.stats['last_updated'] = datetime.now().isoformat()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtem estatisticas do vector store"""
        try:
            # Calcular estatísticas dos documentos
            document_ids = set(chunk.document_id for chunk in self.chunks)
            source_distribution = {}
            quality_scores = []
            
            for chunk in self.chunks:
                # Distribuição por tipo de fonte
                source_type = chunk.source_type
                source_distribution[source_type] = source_distribution.get(source_type, 0) + 1
                
                # Scores de qualidade
                quality_scores.append(chunk.quality_score)
            
            avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
            
            # Estatisticas basicas
            basic_stats = {
                'total_chunks': len(self.chunks),
                'total_documents': len(document_ids),
                'index_size': self.index.ntotal if self.index else 0,
                'embedding_dimension': self.embedding_dim,
                'index_type': self.index_type,
                'search_count': self.stats['search_count'],
                'last_updated': self.stats['last_updated']
            }
            
            # Informacoes do indice FAISS
            index_info = {
                'type': self.index_type,
                'dimension': self.embedding_dim,
                'metric_type': 'inner_product' if self.metric_type == faiss.METRIC_INNER_PRODUCT else 'l2',
                'total_vectors': self.index.ntotal if self.index else 0,
                'is_trained': self.index.is_trained if self.index else False
            }
            
            if self.index_type == 'ivf' and self.index:
                index_info.update({
                    'nlist': self.nlist,
                    'nprobe': self.nprobe
                })
            elif self.index_type == 'hnsw' and self.index:
                index_info.update({
                    'hnsw_m': self.hnsw_m,
                    'hnsw_ef_search': self.hnsw_ef_search
                })
            
            return {
                'basic_stats': basic_stats,
                'source_distribution': source_distribution,
                'document_distribution': {
                    'total_documents': len(document_ids),
                    'total_chunks': len(self.chunks)
                },
                'quality_metrics': {
                    'avg_quality_score': avg_quality,
                    'min_quality': min(quality_scores) if quality_scores else 0,
                    'max_quality': max(quality_scores) if quality_scores else 0
                },
                'index_info': index_info
            }
        except Exception as e:
            print(f"Erro ao obter estatísticas: {e}")
            # Retornar estatísticas básicas em caso de erro
            return {
                'basic_stats': {
                    'total_chunks': len(self.chunks),
                    'total_documents': 0,
                    'index_size': self.index.ntotal if self.index else 0,
                    'embedding_dimension': self.embedding_dim,
                    'index_type': self.index_type,
                    'search_count': self.stats['search_count'],
                    'last_updated': self.stats['last_updated']
                },
                'source_distribution': {},
                'document_distribution': {},
                'quality_metrics': {},
                'index_info': {
                    'type': self.index_type,
                    'dimension': self.embedding_dim,
                    'total_vectors': self.index.ntotal if self.index else 0
                }
            }
    
    def close(self):
        """Fecha todas as conexões e libera recursos"""
        try:
            # Limpar referências
            self.index = None
            self.chunks = []
            self.chunk_metadata = {}
            
            # Forçar garbage collection
            import gc
            gc.collect()
            
            print("Vector store fechado")
        except Exception as e:
            print(f"Erro ao fechar vector store: {e}")
    
    def clear_all(self):
        """Remove todos os dados do vector store"""
        try:
            # Limpar dados em memória
            self.index = None
            self.chunks = []
            self.chunk_metadata = {}
            
            # Remover arquivos de persistência
            if self.index_file.exists():
                self.index_file.unlink()
            if self.chunks_file.exists():
                self.chunks_file.unlink()
            if self.metadata_file.exists():
                self.metadata_file.unlink()
            
            # Recriar índice vazio
            self.index = self._create_index(self.embedding_dim)
            
            # Atualizar estatísticas
            self._update_stats()
            
            print("Vector store limpo com sucesso")
            return {
                'status': 'success',
                'message': 'Vector store limpo com sucesso',
                'total_chunks': 0,
                'total_documents': 0
            }
        except Exception as e:
            print(f"Erro ao limpar vector store: {e}")
            return {
                'status': 'error',
                'message': f'Erro ao limpar vector store: {e}',
                'total_chunks': len(self.chunks)
            }