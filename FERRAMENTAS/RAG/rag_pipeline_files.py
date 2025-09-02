#!/usr/bin/env python3
"""
Pipeline RAG alternativo usando persistência baseada em arquivos
Mais simples que o sistema híbrido SQLite+FAISS
"""

from sources.web_collector import WebSourceCollector
from sources.academic_collector import AcademicSourceCollector
from processing.document_processor import DocumentProcessor
from processing.quality_filters import QualityFilter
from storage.file_store import FileStore
from models.document import RawDocument, ProcessedChunk, SearchResult
from typing import List, Dict, Any, Optional
import json
import os
import numpy as np
from datetime import datetime
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity

class RAGPipelineFiles:
    """Pipeline RAG com persistência baseada em arquivos"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Inicializar componentes
        self.web_collector = WebSourceCollector()
        self.academic_collector = AcademicSourceCollector()
        self.document_processor = DocumentProcessor()
        self.quality_filter = QualityFilter()
        self.file_store = FileStore()
        
        # Estado do pipeline
        self.raw_documents = []
        self.processed_chunks = []
        
        # Restaurar estado se dados existirem
        self._restore_pipeline_state()
    
    def _restore_pipeline_state(self):
        """Restaura o estado do pipeline a partir de arquivos"""
        try:
            stats = self.file_store.get_statistics()
            chunks_count = stats.get('total_chunks', 0)
            
            if chunks_count > 0:
                # Carregar todos os chunks dos arquivos
                self.processed_chunks = self.file_store.load_all_chunks()
                print(f"Estado do pipeline restaurado: {len(self.processed_chunks)} chunks carregados")
            
        except Exception as e:
            print(f"Erro ao restaurar estado do pipeline: {e}")
            self.processed_chunks = []
    
    def executar_pipeline_completo(self, tema: str, max_docs_por_fonte: int = 5) -> Dict[str, Any]:
        """Executa pipeline completo: coleta -> processamento -> armazenamento"""
        print(f"=== INICIANDO PIPELINE RAG COM ARQUIVOS ===")
        print(f"Tema: {tema}")
        print(f"Max documentos por fonte: {max_docs_por_fonte}")
        
        inicio = datetime.now()
        
        try:
            # Etapa 1: Coleta de documentos
            print("\n1. COLETANDO DOCUMENTOS...")
            self.raw_documents = self._coletar_documentos(tema, max_docs_por_fonte)
            
            if not self.raw_documents:
                return {'erro': 'Nenhum documento coletado'}
            
            # Etapa 2: Filtros de qualidade
            print("\n2. APLICANDO FILTROS DE QUALIDADE...")
            self.raw_documents, filter_stats = self.quality_filter.filter_documents(self.raw_documents)
            
            if not self.raw_documents:
                return {'erro': 'Todos os documentos foram filtrados'}
            
            # Etapa 3: Processamento de documentos
            print("\n3. PROCESSANDO DOCUMENTOS...")
            new_chunks = self.document_processor.process_documents(self.raw_documents)
            
            if not new_chunks:
                return {'erro': 'Nenhum chunk gerado'}
            
            # Etapa 4: Filtros de qualidade para chunks
            print("\n4. FILTRANDO CHUNKS...")
            new_chunks, chunk_filter_stats = self.quality_filter.filter_chunks(new_chunks)
            
            # Etapa 5: Verificar duplicatas e salvar
            print("\n5. SALVANDO CHUNKS...")
            chunks_salvos = 0
            chunks_duplicados = 0
            
            for chunk in new_chunks:
                if not self.file_store.chunk_exists(chunk.chunk_id):
                    if self.file_store.save_chunk(chunk):
                        chunks_salvos += 1
                        self.processed_chunks.append(chunk)
                else:
                    chunks_duplicados += 1
            
            print(f"Chunks salvos: {chunks_salvos}")
            print(f"Chunks duplicados ignorados: {chunks_duplicados}")
            
            # Etapa 6: Salvar documentos
            print("\n6. SALVANDO DOCUMENTOS...")
            docs_salvos = 0
            for doc in self.raw_documents:
                if not self.file_store.document_exists(doc.document_id):
                    if self.file_store.save_document(doc):
                        docs_salvos += 1
            
            print(f"Documentos salvos: {docs_salvos}")
            
            # Etapa 7: Salvar resultados
            print("\n7. SALVANDO RESULTADOS...")
            self._salvar_resultados(tema)
            
            fim = datetime.now()
            tempo_execucao = (fim - inicio).total_seconds()
            
            # Gerar relatório
            relatorio = self._gerar_relatorio(tema, tempo_execucao, filter_stats, chunk_filter_stats, chunks_salvos)
            
            print("\n=== PIPELINE CONCLUIDO ===")
            print(f"Tempo de execucao: {tempo_execucao:.2f} segundos")
            print(f"Documentos processados: {len(self.raw_documents)}")
            print(f"Chunks novos salvos: {chunks_salvos}")
            print(f"Total de chunks no sistema: {len(self.processed_chunks)}")
            
            return relatorio
            
        except Exception as e:
            print(f"Erro no pipeline: {e}")
            return {'erro': str(e)}
    
    def _coletar_documentos(self, tema: str, max_docs_por_fonte: int) -> List[RawDocument]:
        """Coleta documentos de múltiplas fontes"""
        all_documents = []
        
        # Coletar da Wikipedia
        print("Coletando da Wikipedia...")
        try:
            wiki_docs = self.web_collector.collect_wikipedia(tema, max_docs_por_fonte, language='pt')
            all_documents.extend(wiki_docs)
            print(f"Wikipedia: {len(wiki_docs)} documentos")
        except Exception as e:
            print(f"Erro na coleta Wikipedia: {e}")
        
        # Coletar do ArXiv
        print("Coletando do ArXiv...")
        try:
            arxiv_docs = self.academic_collector.collect_arxiv(tema, max_docs_por_fonte)
            all_documents.extend(arxiv_docs)
            print(f"ArXiv: {len(arxiv_docs)} documentos")
        except Exception as e:
            print(f"Erro na coleta ArXiv: {e}")
        
        print(f"Total coletado: {len(all_documents)} documentos")
        return all_documents
    
    def buscar(self, query: str, top_k: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Realiza busca semântica nos chunks armazenados"""
        if not self.processed_chunks:
            print("Nenhum chunk disponível para busca")
            return []
        
        try:
            # Gerar embedding da query
            query_embedding = self.document_processor.generate_embeddings([query])[0]
            
            # Calcular similaridades
            resultados = []
            
            for chunk in self.processed_chunks:
                if len(chunk.embedding) == 0:
                    continue  # Pular chunks sem embedding
                
                # Calcular similaridade coseno
                similarity = cosine_similarity(
                    query_embedding.reshape(1, -1),
                    chunk.embedding.reshape(1, -1)
                )[0][0]
                
                # Aplicar filtros se fornecidos
                if filters and not self._apply_filters(filters, chunk):
                    continue
                
                resultados.append({
                    'texto': chunk.text,
                    'similaridade': float(similarity),
                    'fonte': chunk.source_type,
                    'documento': chunk.document_title,
                    'chunk_id': chunk.chunk_id,
                    'quality_score': chunk.quality_score
                })
            
            # Ordenar por similaridade e retornar top_k
            resultados.sort(key=lambda x: x['similaridade'], reverse=True)
            return resultados[:top_k]
            
        except Exception as e:
            print(f"Erro na busca: {e}")
            return []
    
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
            min_score = filters['quality_score']
            if chunk.quality_score < min_score:
                return False
        
        return True
    
    def _salvar_resultados(self, tema: str):
        """Salva resultados em arquivos de texto"""
        tema_safe = tema.replace(' ', '_').replace('/', '_')
        
        # Criar pasta RESULTADOS se não existir
        base_results_dir = Path("RESULTADOS")
        base_results_dir.mkdir(exist_ok=True)
        
        # Criar subpasta do tema dentro de RESULTADOS
        results_dir = base_results_dir / f"resultados_{tema_safe}"
        results_dir.mkdir(exist_ok=True)
        
        # Salvar documentos originais
        with open(results_dir / "documentos_originais.txt", 'w', encoding='utf-8') as f:
            for i, doc in enumerate(self.raw_documents, 1):
                f.write(f"=== DOCUMENTO {i} ===\n")
                f.write(f"Título: {doc.title}\n")
                f.write(f"Fonte: {doc.source_type}\n")
                f.write(f"URL: {doc.url}\n")
                f.write(f"Conteúdo: {doc.content[:500]}...\n\n")
        
        # Salvar chunks processados
        with open(results_dir / "chunks_processados.txt", 'w', encoding='utf-8') as f:
            for i, chunk in enumerate(self.processed_chunks, 1):
                f.write(f"=== CHUNK {i} ===\n")
                f.write(f"ID: {chunk.chunk_id}\n")
                f.write(f"Documento: {chunk.document_title}\n")
                f.write(f"Fonte: {chunk.source_type}\n")
                f.write(f"Qualidade: {chunk.quality_score:.3f}\n")
                f.write(f"Texto: {chunk.text}\n\n")
    
    def _gerar_relatorio(self, tema: str, tempo_execucao: float, 
                        filter_stats: Dict[str, Any], chunk_filter_stats: Dict[str, Any],
                        chunks_salvos: int) -> Dict[str, Any]:
        """Gera relatório da execução"""
        stats = self.file_store.get_statistics()
        
        return {
            'tema': tema,
            'tempo_execucao': tempo_execucao,
            'documentos_coletados': len(self.raw_documents),
            'chunks_novos': chunks_salvos,
            'total_chunks': stats['total_chunks'],
            'total_documentos': stats['total_documents'],
            'filtros_documentos': filter_stats,
            'filtros_chunks': chunk_filter_stats,
            'storage_stats': stats
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtém estatísticas do sistema"""
        file_stats = self.file_store.get_statistics()
        
        return {
            'chunks_em_memoria': len(self.processed_chunks),
            'documentos_em_memoria': len(self.raw_documents),
            'file_storage': file_stats
        }
    
    def close(self):
        """Fecha o pipeline"""
        self.file_store.close()
        print("Pipeline baseado em arquivos fechado")
    
    def __del__(self):
        """Destrutor"""
        try:
            self.close()
        except:
            pass

def exemplo_uso_files():
    """Exemplo de uso do pipeline baseado em arquivos"""
    pipeline = RAGPipelineFiles()
    
    # Executar pipeline
    resultado = pipeline.executar_pipeline_completo("Dom Quixote", max_docs_por_fonte=2)
    
    if 'erro' not in resultado:
        # Testar busca
        print("\n=== TESTANDO BUSCA ===")
        resultados = pipeline.buscar("Dom Quixote cavaleiro", top_k=3)
        
        for i, res in enumerate(resultados, 1):
            print(f"{i}. Score: {res['similaridade']:.3f} - {res['texto'][:100]}...")
    
    pipeline.close()

if __name__ == "__main__":
    exemplo_uso_files()