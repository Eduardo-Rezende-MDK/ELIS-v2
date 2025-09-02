#!/usr/bin/env python3
"""
Processador de documentos com chunking e embeddings
"""

import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional, Tuple
import re
import nltk
from nltk.tokenize import sent_tokenize
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.document import RawDocument, ProcessedChunk

# Download necessario do NLTK
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')

class DocumentProcessor:
    """Processador avancado de documentos"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Configuracoes de embedding
        self.embedding_model_name = self.config.get('embedding_model', 'sentence-transformers/all-MiniLM-L6-v2')
        self.device = self.config.get('device', 'cpu')
        self.batch_size = self.config.get('batch_size', 32)
        
        # Configuracoes de chunking
        self.chunk_size = self.config.get('chunk_size', 512)
        self.chunk_overlap = self.config.get('chunk_overlap', 50)
        self.min_chunk_size = self.config.get('min_chunk_size', 100)
        self.max_chunk_size = self.config.get('max_chunk_size', 1000)
        
        # Configuracoes de limpeza
        self.remove_html = self.config.get('remove_html', True)
        self.remove_urls = self.config.get('remove_urls', True)
        self.normalize_whitespace = self.config.get('normalize_whitespace', True)
        self.min_text_length = self.config.get('min_text_length', 50)
        
        # Carregar modelo de embeddings
        print(f"Carregando modelo de embeddings: {self.embedding_model_name}")
        self.embedding_model = SentenceTransformer(self.embedding_model_name, device=self.device)
        
        # Cache de embeddings
        self.embedding_cache = {}
        
    def clean_text(self, text: str) -> str:
        """Limpa e normaliza texto"""
        if not text:
            return ""
            
        cleaned = text
        
        # Remover HTML se configurado
        if self.remove_html:
            cleaned = re.sub(r'<[^>]+>', '', cleaned)
            
        # Remover URLs se configurado
        if self.remove_urls:
            cleaned = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', cleaned)
            
        # Remover emails
        cleaned = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', cleaned)
        
        # Normalizar espacos se configurado
        if self.normalize_whitespace:
            cleaned = re.sub(r'\s+', ' ', cleaned)
            
        # Remover caracteres especiais excessivos
        cleaned = re.sub(r'[^\w\s.,!?;:()\[\]{}"\'-]', '', cleaned)
        
        return cleaned.strip()
    
    def chunk_text(self, text: str, strategy: str = 'sentence') -> List[str]:
        """Divide texto em chunks usando diferentes estrategias"""
        if not text or len(text) < self.min_text_length:
            return []
            
        if strategy == 'sentence':
            return self._chunk_by_sentences(text)
        elif strategy == 'paragraph':
            return self._chunk_by_paragraphs(text)
        elif strategy == 'fixed_size':
            return self._chunk_by_fixed_size(text)
        elif strategy == 'semantic':
            return self._chunk_by_semantic_similarity(text)
        else:
            return self._chunk_by_sentences(text)  # Default
    
    def _chunk_by_sentences(self, text: str) -> List[str]:
        """Chunking por sentencas"""
        try:
            # Tentar portugues primeiro
            sentences = sent_tokenize(text, language='portuguese')
        except LookupError:
            try:
                # Fallback para ingles
                sentences = sent_tokenize(text, language='english')
            except LookupError:
                # Fallback manual
                sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            # Verificar se adicionar a sentenca excede o tamanho maximo
            potential_chunk = current_chunk + " " + sentence if current_chunk else sentence
            
            if len(potential_chunk) <= self.chunk_size:
                current_chunk = potential_chunk
            else:
                # Salvar chunk atual se nao estiver vazio
                if current_chunk and len(current_chunk) >= self.min_chunk_size:
                    chunks.append(current_chunk.strip())
                
                # Iniciar novo chunk
                current_chunk = sentence
        
        # Adicionar ultimo chunk
        if current_chunk and len(current_chunk) >= self.min_chunk_size:
            chunks.append(current_chunk.strip())
        
        # Aplicar overlap se configurado
        if self.chunk_overlap > 0 and len(chunks) > 1:
            chunks = self._apply_overlap(chunks)
            
        return chunks
    
    def _chunk_by_paragraphs(self, text: str) -> List[str]:
        """Chunking por paragrafos"""
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            potential_chunk = current_chunk + "\n\n" + paragraph if current_chunk else paragraph
            
            if len(potential_chunk) <= self.chunk_size:
                current_chunk = potential_chunk
            else:
                if current_chunk and len(current_chunk) >= self.min_chunk_size:
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph
        
        if current_chunk and len(current_chunk) >= self.min_chunk_size:
            chunks.append(current_chunk.strip())
            
        return chunks
    
    def _chunk_by_fixed_size(self, text: str) -> List[str]:
        """Chunking por tamanho fixo"""
        chunks = []
        
        for i in range(0, len(text), self.chunk_size - self.chunk_overlap):
            chunk = text[i:i + self.chunk_size]
            if len(chunk) >= self.min_chunk_size:
                chunks.append(chunk)
                
        return chunks
    
    def _chunk_by_semantic_similarity(self, text: str) -> List[str]:
        """Chunking baseado em similaridade semantica (implementacao simplificada)"""
        # Por enquanto, usar chunking por sentencas
        # Uma implementacao completa usaria embeddings para agrupar sentencas similares
        return self._chunk_by_sentences(text)
    
    def _apply_overlap(self, chunks: List[str]) -> List[str]:
        """Aplica overlap entre chunks"""
        if len(chunks) <= 1:
            return chunks
            
        overlapped_chunks = [chunks[0]]  # Primeiro chunk sem modificacao
        
        for i in range(1, len(chunks)):
            # Pegar ultimas palavras do chunk anterior
            prev_words = chunks[i-1].split()[-self.chunk_overlap:]
            overlap_text = " ".join(prev_words)
            
            # Adicionar ao chunk atual
            overlapped_chunk = overlap_text + " " + chunks[i]
            overlapped_chunks.append(overlapped_chunk)
            
        return overlapped_chunks
    
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """Gera embeddings para lista de textos"""
        if not texts:
            return np.array([])
            
        # Verificar cache
        cached_embeddings = []
        texts_to_process = []
        
        for text in texts:
            text_hash = hash(text)
            if text_hash in self.embedding_cache:
                cached_embeddings.append(self.embedding_cache[text_hash])
            else:
                cached_embeddings.append(None)
                texts_to_process.append((len(cached_embeddings) - 1, text))
        
        # Processar textos nao cacheados
        if texts_to_process:
            batch_texts = [text for _, text in texts_to_process]
            batch_embeddings = self.embedding_model.encode(
                batch_texts,
                batch_size=self.batch_size,
                show_progress_bar=len(batch_texts) > 10
            )
            
            # Atualizar cache e resultado
            for (idx, text), embedding in zip(texts_to_process, batch_embeddings):
                text_hash = hash(text)
                self.embedding_cache[text_hash] = embedding
                cached_embeddings[idx] = embedding
        
        return np.array(cached_embeddings)
    
    def process_document(self, document: RawDocument, chunking_strategy: str = 'sentence') -> List[ProcessedChunk]:
        """Processa um documento completo"""
        # Limpar texto
        cleaned_text = self.clean_text(document.content)
        
        if len(cleaned_text) < self.min_text_length:
            return []
        
        # Fazer chunking
        chunk_texts = self.chunk_text(cleaned_text, chunking_strategy)
        
        if not chunk_texts:
            return []
        
        # Gerar embeddings
        embeddings = self.generate_embeddings(chunk_texts)
        
        # Criar objetos ProcessedChunk
        processed_chunks = []
        
        for i, (chunk_text, embedding) in enumerate(zip(chunk_texts, embeddings)):
            chunk = ProcessedChunk(
                text=chunk_text,
                embedding=embedding,
                document_id=document.document_id,
                chunk_index=i,
                source_type=document.source_type,
                document_title=document.title,
                chunk_size=len(chunk_text),
                overlap_size=self.chunk_overlap if i > 0 else 0,
                metadata={
                    'chunking_strategy': chunking_strategy,
                    'original_document_length': len(document.content),
                    'cleaned_document_length': len(cleaned_text),
                    'document_language': document.language,
                    'document_quality_score': document.quality_score
                }
            )
            
            # Calcular score de qualidade do chunk
            chunk.quality_score = self._calculate_chunk_quality_score(chunk, document)
            
            processed_chunks.append(chunk)
        
        # Estabelecer links entre chunks adjacentes
        for i, chunk in enumerate(processed_chunks):
            if i > 0:
                chunk.previous_chunk_id = processed_chunks[i-1].chunk_id
            if i < len(processed_chunks) - 1:
                chunk.next_chunk_id = processed_chunks[i+1].chunk_id
        
        return processed_chunks
    
    def process_documents(self, documents: List[RawDocument], chunking_strategy: str = 'sentence') -> List[ProcessedChunk]:
        """Processa lista de documentos"""
        all_chunks = []
        
        print(f"Processando {len(documents)} documentos...")
        
        for i, document in enumerate(documents, 1):
            print(f"Processando documento {i}/{len(documents)}: {document.title[:50]}...")
            
            try:
                chunks = self.process_document(document, chunking_strategy)
                all_chunks.extend(chunks)
                print(f"  Gerados {len(chunks)} chunks")
                
            except Exception as e:
                print(f"  Erro ao processar documento: {e}")
                continue
        
        print(f"\nTotal de chunks processados: {len(all_chunks)}")
        return all_chunks
    
    def _calculate_chunk_quality_score(self, chunk: ProcessedChunk, original_document: RawDocument) -> float:
        """Calcula score de qualidade para um chunk"""
        score = 0.5  # Score base
        
        # Tamanho do chunk
        if self.min_chunk_size <= len(chunk.text) <= self.max_chunk_size:
            score += 0.2
        elif len(chunk.text) < self.min_chunk_size:
            score -= 0.2
            
        # Qualidade do documento original
        score += original_document.quality_score * 0.3
        
        # Norma do embedding (embeddings muito pequenos podem indicar problemas)
        if chunk.embedding_norm > 0.1:
            score += 0.1
            
        # Presenca de pontuacao (indica texto bem estruturado)
        punctuation_count = sum(1 for char in chunk.text if char in '.,!?;:')
        if punctuation_count > 0:
            score += 0.1
            
        return min(score, 1.0)
    
    def get_processing_statistics(self, chunks: List[ProcessedChunk]) -> Dict[str, Any]:
        """Obtem estatisticas do processamento"""
        if not chunks:
            return {}
            
        chunk_sizes = [chunk.chunk_size for chunk in chunks]
        quality_scores = [chunk.quality_score for chunk in chunks]
        embedding_norms = [chunk.embedding_norm for chunk in chunks]
        
        # Distribuicao por fonte
        source_distribution = {}
        for chunk in chunks:
            source_distribution[chunk.source_type] = source_distribution.get(chunk.source_type, 0) + 1
        
        # Distribuicao por documento
        document_distribution = {}
        for chunk in chunks:
            document_distribution[chunk.document_id] = document_distribution.get(chunk.document_id, 0) + 1
        
        return {
            'total_chunks': len(chunks),
            'avg_chunk_size': np.mean(chunk_sizes) if chunk_sizes else 0,
            'min_chunk_size': min(chunk_sizes) if chunk_sizes else 0,
            'max_chunk_size': max(chunk_sizes) if chunk_sizes else 0,
            'avg_quality_score': np.mean(quality_scores) if quality_scores else 0,
            'avg_embedding_norm': np.mean(embedding_norms) if embedding_norms else 0,
            'source_distribution': source_distribution,
            'document_distribution': document_distribution,
            'unique_documents': len(document_distribution),
            'chunks_per_document': len(chunks) / len(document_distribution) if document_distribution else 0
        }
    
    def clear_embedding_cache(self):
        """Limpa cache de embeddings"""
        self.embedding_cache.clear()
        print("Cache de embeddings limpo")
    
    def get_cache_size(self) -> int:
        """Retorna tamanho do cache de embeddings"""
        return len(self.embedding_cache)