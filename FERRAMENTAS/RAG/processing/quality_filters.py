#!/usr/bin/env python3
"""
Filtros de qualidade para documentos e chunks
"""

import re
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.document import RawDocument, ProcessedChunk

class QualityFilter:
    """Sistema de filtros de qualidade para documentos e chunks"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Configuracoes de filtros para documentos
        self.min_document_length = self.config.get('min_document_length', 200)
        self.max_document_length = self.config.get('max_document_length', 50000)
        self.min_document_quality_score = self.config.get('min_document_quality_score', 0.3)
        
        # Configuracoes de filtros para chunks
        self.min_chunk_length = self.config.get('min_chunk_length', 100)
        self.max_chunk_length = self.config.get('max_chunk_length', 2000)
        self.min_chunk_quality_score = self.config.get('min_chunk_quality_score', 0.4)
        self.min_embedding_norm = self.config.get('min_embedding_norm', 0.1)
        
        # Configuracoes de deteccao de duplicatas
        self.similarity_threshold = self.config.get('similarity_threshold', 0.95)
        self.enable_duplicate_detection = self.config.get('enable_duplicate_detection', True)
        
        # Padroes de baixa qualidade
        self.low_quality_patterns = self.config.get('low_quality_patterns', [
            r'404 not found',
            r'page not found',
            r'access denied',
            r'login required',
            r'javascript required',
            r'error \d+',
            r'forbidden',
            r'unauthorized'
        ])
        
        # Indicadores de qualidade academica
        self.academic_indicators = self.config.get('academic_indicators', [
            'abstract', 'introduction', 'methodology', 'conclusion',
            'references', 'doi:', 'issn:', 'journal', 'university',
            'research', 'study', 'analysis', 'experiment'
        ])
        
        # Cache para deteccao de duplicatas
        self.duplicate_cache = {}
        
    def filter_documents(self, documents: List[RawDocument]) -> Tuple[List[RawDocument], Dict[str, Any]]:
        """Filtra documentos baseado em criterios de qualidade"""
        if not documents:
            return [], {'total_input': 0, 'total_output': 0, 'filtered_reasons': {}}
        
        filtered_documents = []
        filter_stats = {
            'total_input': len(documents),
            'total_output': 0,
            'filtered_reasons': {
                'too_short': 0,
                'too_long': 0,
                'low_quality_score': 0,
                'low_quality_patterns': 0,
                'duplicate': 0,
                'other': 0
            }
        }
        
        print(f"Filtrando {len(documents)} documentos...")
        
        for document in documents:
            filter_reason = self._should_filter_document(document)
            
            if filter_reason:
                filter_stats['filtered_reasons'][filter_reason] += 1
            else:
                filtered_documents.append(document)
        
        # Deteccao de duplicatas se habilitada
        if self.enable_duplicate_detection and len(filtered_documents) > 1:
            filtered_documents, duplicate_count = self._remove_duplicate_documents(filtered_documents)
            filter_stats['filtered_reasons']['duplicate'] = duplicate_count
        
        filter_stats['total_output'] = len(filtered_documents)
        
        print(f"Documentos filtrados: {len(documents)} -> {len(filtered_documents)}")
        self._print_filter_stats(filter_stats)
        
        return filtered_documents, filter_stats
    
    def filter_chunks(self, chunks: List[ProcessedChunk]) -> Tuple[List[ProcessedChunk], Dict[str, Any]]:
        """Filtra chunks baseado em criterios de qualidade"""
        if not chunks:
            return [], {'total_input': 0, 'total_output': 0, 'filtered_reasons': {}}
        
        filtered_chunks = []
        filter_stats = {
            'total_input': len(chunks),
            'total_output': 0,
            'filtered_reasons': {
                'too_short': 0,
                'too_long': 0,
                'low_quality_score': 0,
                'low_embedding_norm': 0,
                'duplicate': 0,
                'other': 0
            }
        }
        
        print(f"Filtrando {len(chunks)} chunks...")
        
        for chunk in chunks:
            filter_reason = self._should_filter_chunk(chunk)
            
            if filter_reason:
                filter_stats['filtered_reasons'][filter_reason] += 1
            else:
                filtered_chunks.append(chunk)
        
        # Deteccao de duplicatas se habilitada
        if self.enable_duplicate_detection and len(filtered_chunks) > 1:
            filtered_chunks, duplicate_count = self._remove_duplicate_chunks(filtered_chunks)
            filter_stats['filtered_reasons']['duplicate'] = duplicate_count
        
        filter_stats['total_output'] = len(filtered_chunks)
        
        print(f"Chunks filtrados: {len(chunks)} -> {len(filtered_chunks)}")
        self._print_filter_stats(filter_stats)
        
        return filtered_chunks, filter_stats
    
    def _should_filter_document(self, document: RawDocument) -> Optional[str]:
        """Verifica se um documento deve ser filtrado"""
        # Filtro por tamanho
        content_length = len(document.content)
        if content_length < self.min_document_length:
            return 'too_short'
        if content_length > self.max_document_length:
            return 'too_long'
        
        # Filtro por score de qualidade
        if document.quality_score < self.min_document_quality_score:
            return 'low_quality_score'
        
        # Filtro por padroes de baixa qualidade
        if self._contains_low_quality_patterns(document.content):
            return 'low_quality_patterns'
        
        return None
    
    def _should_filter_chunk(self, chunk: ProcessedChunk) -> Optional[str]:
        """Verifica se um chunk deve ser filtrado"""
        # Filtro por tamanho
        if chunk.chunk_size < self.min_chunk_length:
            return 'too_short'
        if chunk.chunk_size > self.max_chunk_length:
            return 'too_long'
        
        # Filtro por score de qualidade
        if chunk.quality_score < self.min_chunk_quality_score:
            return 'low_quality_score'
        
        # Filtro por norma do embedding
        if chunk.embedding_norm < self.min_embedding_norm:
            return 'low_embedding_norm'
        
        return None
    
    def _contains_low_quality_patterns(self, text: str) -> bool:
        """Verifica se o texto contem padroes de baixa qualidade"""
        text_lower = text.lower()
        
        for pattern in self.low_quality_patterns:
            if re.search(pattern, text_lower):
                return True
        
        return False
    
    def _remove_duplicate_documents(self, documents: List[RawDocument]) -> Tuple[List[RawDocument], int]:
        """Remove documentos duplicados baseado em similaridade de conteudo"""
        if len(documents) <= 1:
            return documents, 0
        
        # Usar TF-IDF para calcular similaridade
        texts = [doc.content for doc in documents]
        
        try:
            vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
            tfidf_matrix = vectorizer.fit_transform(texts)
            
            # Calcular matriz de similaridade
            similarity_matrix = cosine_similarity(tfidf_matrix)
            
            # Encontrar duplicatas
            duplicates_to_remove = set()
            
            for i in range(len(documents)):
                if i in duplicates_to_remove:
                    continue
                    
                for j in range(i + 1, len(documents)):
                    if j in duplicates_to_remove:
                        continue
                        
                    if similarity_matrix[i][j] >= self.similarity_threshold:
                        # Manter o documento com maior score de qualidade
                        if documents[i].quality_score >= documents[j].quality_score:
                            duplicates_to_remove.add(j)
                        else:
                            duplicates_to_remove.add(i)
                            break
            
            # Remover duplicatas
            filtered_documents = [doc for i, doc in enumerate(documents) if i not in duplicates_to_remove]
            
            return filtered_documents, len(duplicates_to_remove)
            
        except Exception as e:
            print(f"Erro na deteccao de duplicatas de documentos: {e}")
            return documents, 0
    
    def _remove_duplicate_chunks(self, chunks: List[ProcessedChunk]) -> Tuple[List[ProcessedChunk], int]:
        """Remove chunks duplicados baseado em similaridade de embeddings"""
        if len(chunks) <= 1:
            return chunks, 0
        
        try:
            # Usar embeddings para calcular similaridade
            embeddings = np.array([chunk.embedding for chunk in chunks])
            
            # Calcular matriz de similaridade coseno
            similarity_matrix = cosine_similarity(embeddings)
            
            # Encontrar duplicatas
            duplicates_to_remove = set()
            
            for i in range(len(chunks)):
                if i in duplicates_to_remove:
                    continue
                    
                for j in range(i + 1, len(chunks)):
                    if j in duplicates_to_remove:
                        continue
                        
                    if similarity_matrix[i][j] >= self.similarity_threshold:
                        # Manter o chunk com maior score de qualidade
                        if chunks[i].quality_score >= chunks[j].quality_score:
                            duplicates_to_remove.add(j)
                        else:
                            duplicates_to_remove.add(i)
                            break
            
            # Remover duplicatas
            filtered_chunks = [chunk for i, chunk in enumerate(chunks) if i not in duplicates_to_remove]
            
            return filtered_chunks, len(duplicates_to_remove)
            
        except Exception as e:
            print(f"Erro na deteccao de duplicatas de chunks: {e}")
            return chunks, 0
    
    def calculate_document_quality_score(self, document: RawDocument) -> float:
        """Calcula score de qualidade avancado para um documento"""
        score = 0.5  # Score base
        
        # Tamanho do conteudo
        content_length = len(document.content)
        if 1000 <= content_length <= 10000:
            score += 0.2
        elif 500 <= content_length < 1000 or 10000 < content_length <= 20000:
            score += 0.1
        elif content_length < 200:
            score -= 0.3
        
        # Presenca de indicadores academicos
        academic_score = self._calculate_academic_score(document.content)
        score += academic_score * 0.2
        
        # Qualidade da estrutura do texto
        structure_score = self._calculate_structure_score(document.content)
        score += structure_score * 0.1
        
        # Presenca de metadados
        if document.authors:
            score += 0.05
        if document.publication_date:
            score += 0.05
        if document.keywords:
            score += 0.05
        if document.abstract:
            score += 0.05
        
        # Penalizar padroes de baixa qualidade
        if self._contains_low_quality_patterns(document.content):
            score -= 0.3
        
        return max(0.0, min(score, 1.0))
    
    def _calculate_academic_score(self, text: str) -> float:
        """Calcula score baseado em indicadores academicos"""
        text_lower = text.lower()
        
        found_indicators = 0
        for indicator in self.academic_indicators:
            if indicator in text_lower:
                found_indicators += 1
        
        return min(found_indicators / len(self.academic_indicators), 1.0)
    
    def _calculate_structure_score(self, text: str) -> float:
        """Calcula score baseado na estrutura do texto"""
        score = 0.0
        
        # Presenca de pontuacao
        punctuation_count = sum(1 for char in text if char in '.,!?;:')
        if punctuation_count > 0:
            score += 0.3
        
        # Razao de letras maiusculas (muito alto ou muito baixo e ruim)
        uppercase_ratio = sum(1 for char in text if char.isupper()) / len(text) if text else 0
        if 0.02 <= uppercase_ratio <= 0.15:
            score += 0.2
        
        # Presenca de paragrafos
        paragraph_count = len([p for p in text.split('\n\n') if p.strip()])
        if paragraph_count > 1:
            score += 0.3
        
        # Diversidade de vocabulario (aproximacao simples)
        words = text.lower().split()
        if words:
            unique_words = len(set(words))
            vocabulary_diversity = unique_words / len(words)
            if vocabulary_diversity > 0.3:
                score += 0.2
        
        return min(score, 1.0)
    
    def _print_filter_stats(self, stats: Dict[str, Any]):
        """Imprime estatisticas de filtragem"""
        total_filtered = stats['total_input'] - stats['total_output']
        
        if total_filtered > 0:
            print(f"  Filtrados: {total_filtered} itens")
            for reason, count in stats['filtered_reasons'].items():
                if count > 0:
                    percentage = (count / stats['total_input']) * 100
                    print(f"    {reason}: {count} ({percentage:.1f}%)")
    
    def get_filter_statistics(self, documents: List[RawDocument] = None, chunks: List[ProcessedChunk] = None) -> Dict[str, Any]:
        """Obtem estatisticas dos filtros aplicados"""
        stats = {
            'filter_config': {
                'min_document_length': self.min_document_length,
                'max_document_length': self.max_document_length,
                'min_document_quality_score': self.min_document_quality_score,
                'min_chunk_length': self.min_chunk_length,
                'max_chunk_length': self.max_chunk_length,
                'min_chunk_quality_score': self.min_chunk_quality_score,
                'similarity_threshold': self.similarity_threshold,
                'enable_duplicate_detection': self.enable_duplicate_detection
            }
        }
        
        if documents:
            quality_scores = [doc.quality_score for doc in documents]
            content_lengths = [len(doc.content) for doc in documents]
            
            stats['documents'] = {
                'total': len(documents),
                'avg_quality_score': np.mean(quality_scores) if quality_scores else 0,
                'avg_content_length': np.mean(content_lengths) if content_lengths else 0,
                'quality_score_distribution': {
                    'min': min(quality_scores) if quality_scores else 0,
                    'max': max(quality_scores) if quality_scores else 0,
                    'std': np.std(quality_scores) if quality_scores else 0
                }
            }
        
        if chunks:
            quality_scores = [chunk.quality_score for chunk in chunks]
            chunk_sizes = [chunk.chunk_size for chunk in chunks]
            embedding_norms = [chunk.embedding_norm for chunk in chunks]
            
            stats['chunks'] = {
                'total': len(chunks),
                'avg_quality_score': np.mean(quality_scores) if quality_scores else 0,
                'avg_chunk_size': np.mean(chunk_sizes) if chunk_sizes else 0,
                'avg_embedding_norm': np.mean(embedding_norms) if embedding_norms else 0
            }
        
        return stats
    
    def update_config(self, new_config: Dict[str, Any]):
        """Atualiza configuracao dos filtros"""
        self.config.update(new_config)
        
        # Atualizar atributos
        for key, value in new_config.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def reset_duplicate_cache(self):
        """Limpa cache de deteccao de duplicatas"""
        self.duplicate_cache.clear()