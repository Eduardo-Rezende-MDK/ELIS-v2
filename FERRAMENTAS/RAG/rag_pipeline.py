#!/usr/bin/env python3
"""
Pipeline principal do sistema RAG - Arquitetura Modular
Integra coleta, processamento e busca usando nova estrutura
"""

from sources.web_collector import WebSourceCollector
from sources.academic_collector import AcademicSourceCollector
from processing.document_processor import DocumentProcessor
from processing.quality_filters import QualityFilter
from storage.vector_store import RAGVectorStore
from models.document import RawDocument, ProcessedChunk, SearchResult
from typing import List, Dict, Any, Optional
import json
import os
from datetime import datetime

class RAGPipeline:
    """Pipeline completo do sistema RAG com arquitetura modular"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Inicializar componentes
        self.web_collector = WebSourceCollector()
        self.academic_collector = AcademicSourceCollector()
        self.document_processor = DocumentProcessor()
        self.quality_filter = QualityFilter()
        self.vector_store = RAGVectorStore()
        
        # Estado do pipeline
        self.raw_documents = []
        self.processed_chunks = []
        
        # Restaurar estado se dados existirem
        self._restore_pipeline_state()
    
    def _restore_pipeline_state(self):
        """Restaura o estado do pipeline a partir de dados persistidos"""
        try:
            # Verificar se existem dados no SQLite
            stats = self.vector_store.sqlite_manager.get_statistics()
            chunks_count = stats.get('chunks', {}).get('total', 0)
            
            if chunks_count > 0:
                # Criar chunks dummy para indicar que há dados (embeddings estão no FAISS)
                from models.document import ProcessedChunk
                import numpy as np
                
                # Criar um chunk dummy por cada chunk no banco
                self.processed_chunks = []
                for i in range(chunks_count):
                    dummy_chunk = ProcessedChunk(
                        text=f"chunk_{i}",
                        embedding=np.array([1.0]),  # Embedding dummy não vazio
                        document_id=f"doc_{i}",
                        chunk_index=i,
                        source_type="restored",
                        document_title="Restored Data"
                    )
                    self.processed_chunks.append(dummy_chunk)
                
                print(f"Estado do pipeline restaurado: {len(self.processed_chunks)} chunks carregados")
            
        except Exception as e:
            print(f"Erro ao restaurar estado do pipeline: {e}")
            # Manter listas vazias em caso de erro
            self.processed_chunks = []
        
    def executar_pipeline_completo(self, tema: str, max_docs_por_fonte: int = 5) -> Dict[str, Any]:
        """Executa pipeline completo: coleta -> processamento -> armazenamento"""
        print(f"=== INICIANDO PIPELINE RAG MODULAR ===")
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
            
            # Adicionar novos chunks aos existentes (manter acumulação)
            chunks_anteriores = len(self.processed_chunks)
            self.processed_chunks.extend(new_chunks)
            print(f"Chunks anteriores: {chunks_anteriores}, Novos: {len(new_chunks)}, Total: {len(self.processed_chunks)}")
            
            # Etapa 5: Armazenamento vetorial
            print("\n5. ARMAZENANDO NO VECTOR STORE...")
            success = self.vector_store.add_chunks(new_chunks)
            
            if not success:
                return {'erro': 'Falha no armazenamento vetorial'}
                
            # Etapa 6: Salvar resultados
            print("\n6. SALVANDO RESULTADOS...")
            self._salvar_resultados(tema)
            
            # Salvar indice FAISS
            self.vector_store.save_index()
            
            fim = datetime.now()
            tempo_execucao = (fim - inicio).total_seconds()
            
            # Gerar relatorio
            relatorio = self._gerar_relatorio(tema, tempo_execucao, filter_stats, chunk_filter_stats)
            
            print("\n=== PIPELINE CONCLUIDO ===")
            print(f"Tempo de execucao: {tempo_execucao:.2f} segundos")
            print(f"Documentos processados: {len(self.raw_documents)}")
            print(f"Chunks armazenados: {len(new_chunks)}")
            print(f"Total de chunks no sistema: {len(self.processed_chunks)}")
            
            return relatorio
            
        except Exception as e:
            print(f"Erro no pipeline: {e}")
            return {'erro': str(e)}
    
    def _coletar_documentos(self, tema: str, max_docs_por_fonte: int) -> List[RawDocument]:
        """Coleta documentos de multiplas fontes"""
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
        """Realiza busca semantica nos documentos processados"""
        if not self.processed_chunks:
            print("Nenhum documento processado. Execute o pipeline primeiro.")
            return []
            
        try:
            # Gerar embedding da query
            query_embedding = self.document_processor.generate_embeddings([query])[0]
            
            # Buscar no vector store
            search_results = self.vector_store.search(query_embedding, top_k, filters)
            
            # Converter para formato compativel
            results = []
            for result in search_results:
                results.append({
                    'texto': result.chunk.text,
                    'similaridade': result.score,
                    'fonte': result.chunk.source_type,
                    'documento': result.chunk.document_title,
                    'chunk_id': result.chunk.chunk_id,
                    'quality_score': result.chunk.quality_score
                })
                
            return results
            
        except Exception as e:
            print(f"Erro na busca: {e}")
            return []
    
    def obter_contexto_para_query(self, query: str, max_chars: int = 2000) -> str:
        """Obtem contexto relevante para uma query"""
        resultados = self.buscar(query, top_k=5)
        
        if not resultados:
            return "Nenhum contexto relevante encontrado."
            
        contexto_parts = []
        chars_count = 0
        
        for resultado in resultados:
            texto = resultado['texto']
            if chars_count + len(texto) <= max_chars:
                contexto_parts.append(f"[{resultado['fonte']}] {texto}")
                chars_count += len(texto)
            else:
                # Adicionar parte do texto que cabe
                remaining_chars = max_chars - chars_count
                if remaining_chars > 100:
                    contexto_parts.append(f"[{resultado['fonte']}] {texto[:remaining_chars]}...")
                break
                
        return "\n\n".join(contexto_parts)
    
    def responder_pergunta(self, pergunta: str) -> Dict[str, Any]:
        """Responde uma pergunta usando o contexto coletado"""
        # Buscar contexto relevante
        contexto = self.obter_contexto_para_query(pergunta, max_chars=1500)
        
        if not contexto or contexto == "Nenhum contexto relevante encontrado.":
            return {
                'pergunta': pergunta,
                'resposta': 'Nao foi possivel encontrar informacoes relevantes.',
                'contexto': '',
                'fontes': []
            }
        
        # Buscar fontes
        resultados = self.buscar(pergunta, top_k=3)
        fontes = []
        for resultado in resultados:
            fontes.append({
                'documento': resultado['documento'],
                'fonte': resultado['fonte'],
                'similaridade': resultado['similaridade'],
                'quality_score': resultado['quality_score']
            })
        
        # Resposta baseada no contexto
        resposta = f"Com base nos documentos coletados:\n\n{contexto[:800]}..."
        
        return {
            'pergunta': pergunta,
            'resposta': resposta,
            'contexto': contexto,
            'fontes': fontes
        }
    
    def _salvar_resultados(self, tema: str):
        """Salva resultados do pipeline"""
        # Criar pasta RESULTADOS se não existir
        base_results_dir = "RESULTADOS"
        os.makedirs(base_results_dir, exist_ok=True)
        
        # Criar subpasta do tema dentro de RESULTADOS
        pasta_resultados = os.path.join(base_results_dir, f"resultados_{tema.replace(' ', '_')}")
        os.makedirs(pasta_resultados, exist_ok=True)
        
        # Salvar documentos originais
        arquivo_docs = os.path.join(pasta_resultados, "documentos_originais.txt")
        with open(arquivo_docs, 'w', encoding='utf-8') as f:
            for i, doc in enumerate(self.raw_documents, 1):
                f.write(f"=== DOCUMENTO {i} ===\n")
                f.write(f"Titulo: {doc.title}\n")
                f.write(f"Fonte: {doc.source_type}\n")
                f.write(f"URL: {doc.url}\n")
                f.write(f"Qualidade: {doc.quality_score:.3f}\n")
                f.write(f"Conteudo:\n{doc.content}\n\n")
        
        # Salvar chunks processados
        arquivo_chunks = os.path.join(pasta_resultados, "chunks_processados.txt")
        with open(arquivo_chunks, 'w', encoding='utf-8') as f:
            for i, chunk in enumerate(self.processed_chunks, 1):
                f.write(f"=== CHUNK {i} ===\n")
                f.write(f"Documento: {chunk.document_title}\n")
                f.write(f"Fonte: {chunk.source_type}\n")
                f.write(f"Tamanho: {chunk.chunk_size} chars\n")
                f.write(f"Qualidade: {chunk.quality_score:.3f}\n")
                f.write(f"Texto:\n{chunk.text}\n\n")
        
        print(f"Documentos salvos em: {arquivo_docs}")
        print(f"Chunks salvos em: {arquivo_chunks}")
    
    def _gerar_relatorio(self, tema: str, tempo_execucao: float, 
                        filter_stats: Dict[str, Any], chunk_filter_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Gera relatorio detalhado do pipeline"""
        # Estatisticas do processamento
        processing_stats = self.document_processor.get_processing_statistics(self.processed_chunks)
        
        # Estatisticas do vector store
        vector_stats = self.vector_store.get_statistics()
        
        relatorio = {
            'tema': tema,
            'timestamp': datetime.now().isoformat(),
            'tempo_execucao_segundos': tempo_execucao,
            'documentos': {
                'total_coletados': len(self.raw_documents),
                'filtros_aplicados': filter_stats
            },
            'chunks': {
                'total_processados': len(self.processed_chunks),
                'estatisticas_processamento': processing_stats,
                'filtros_aplicados': chunk_filter_stats
            },
            'vector_store': vector_stats,
            'status': 'concluido'
        }
        
        # Salvar relatorio
        pasta_resultados = f"resultados_{tema.replace(' ', '_')}"
        arquivo_relatorio = os.path.join(pasta_resultados, "relatorio.json")
        
        try:
            with open(arquivo_relatorio, 'w', encoding='utf-8') as f:
                json.dump(relatorio, f, indent=2, ensure_ascii=False)
            print(f"Relatorio salvo em: {arquivo_relatorio}")
        except Exception as e:
            print(f"Erro ao salvar relatorio: {e}")
            
        return relatorio
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtem estatisticas completas do sistema"""
        vector_stats = self.vector_store.get_statistics()
        
        return {
            'basic_stats': {
                'documentos_carregados': len(self.raw_documents),
                'chunks_processados': len(self.processed_chunks),
                'total_chunks': vector_stats['basic_stats']['total_chunks'],
                'total_documents': vector_stats['basic_stats']['total_documents']
            },
            'vector_store_stats': vector_stats,
            'processing_stats': self.document_processor.get_processing_statistics(self.processed_chunks) if self.processed_chunks else {},
            'source_distribution': vector_stats.get('source_distribution', {}),
            'quality_metrics': vector_stats.get('quality_metrics', {}),
            'index_info': vector_stats.get('index_info', {})
        }
    
    def close(self):
        """Fecha todas as conexões e libera recursos"""
        try:
            # Fechar vector store
            if hasattr(self, 'vector_store') and self.vector_store:
                self.vector_store.close()
            
            # Limpar referências
            self.raw_documents = []
            self.processed_chunks = []
            
            # Forçar garbage collection
            import gc
            gc.collect()
            
            print("Pipeline fechado")
        except Exception as e:
            print(f"Erro ao fechar pipeline: {e}")
    
    def __del__(self):
        """Destrutor para garantir fechamento de conexões"""
        try:
            self.close()
        except:
            pass

def exemplo_uso_modular():
    """Exemplo de uso da nova arquitetura modular"""
    # Criar pipeline
    pipeline = RAGPipeline()
    
    # Executar pipeline completo
    tema = "inteligencia artificial"
    relatorio = pipeline.executar_pipeline_completo(tema, max_docs_por_fonte=3)
    
    if 'erro' in relatorio:
        print(f"Erro no pipeline: {relatorio['erro']}")
        return
    
    # Exemplos de busca
    print("\n=== EXEMPLOS DE BUSCA SEMANTICA ===")
    
    perguntas = [
        "O que e inteligencia artificial?",
        "Como funciona machine learning?",
        "Quais sao as aplicacoes da IA?"
    ]
    
    for pergunta in perguntas:
        print(f"\nPergunta: {pergunta}")
        
        # Busca semantica
        resultados = pipeline.buscar(pergunta, top_k=2)
        print(f"Encontrados {len(resultados)} resultados relevantes")
        
        for i, resultado in enumerate(resultados, 1):
            print(f"  {i}. [{resultado['fonte']}] Similaridade: {resultado['similaridade']:.3f}")
            print(f"     Qualidade: {resultado['quality_score']:.3f}")
            print(f"     {resultado['texto'][:100]}...")
    
    # Estatisticas finais
    print("\n=== ESTATISTICAS DO SISTEMA ===")
    stats = pipeline.get_statistics()
    print(f"Documentos: {stats['documentos_carregados']}")
    print(f"Chunks: {stats['chunks_processados']}")
    print(f"Cache embeddings: {stats['cache_size']} entradas")

if __name__ == "__main__":
    exemplo_uso_modular()