#!/usr/bin/env python3
"""
Pipeline principal do sistema RAG
Integra coleta, processamento e busca de documentos
"""

from coletor_basico import ColetorBasico, Documento
from processador_documentos import ProcessadorDocumentos, Chunk
from typing import List, Dict, Any
import json
import os
from datetime import datetime

class RAGPipeline:
    """Pipeline completo do sistema RAG"""
    
    def __init__(self, modelo_embedding: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.coletor = ColetorBasico()
        self.processador = ProcessadorDocumentos(modelo_embedding)
        self.documentos = []
        self.chunks = []
        
    def executar_pipeline_completo(self, tema: str, max_docs_por_fonte: int = 5) -> Dict[str, Any]:
        """Executa pipeline completo: coleta -> processamento -> preparacao"""
        print(f"=== INICIANDO PIPELINE RAG ===")
        print(f"Tema: {tema}")
        print(f"Max documentos por fonte: {max_docs_por_fonte}")
        
        inicio = datetime.now()
        
        # Etapa 1: Coleta de documentos
        print("\n1. COLETANDO DOCUMENTOS...")
        self.documentos = self.coletor.coletar_por_tema(tema, max_docs_por_fonte)
        
        if not self.documentos:
            print("Nenhum documento coletado. Encerrando pipeline.")
            return {'erro': 'Nenhum documento coletado'}
            
        # Etapa 2: Processamento de documentos
        print("\n2. PROCESSANDO DOCUMENTOS...")
        self.chunks = self.processador.processar_documentos(self.documentos)
        
        if not self.chunks:
            print("Nenhum chunk gerado. Encerrando pipeline.")
            return {'erro': 'Nenhum chunk gerado'}
            
        # Etapa 3: Salvar resultados
        print("\n3. SALVANDO RESULTADOS...")
        self._salvar_resultados(tema)
        
        fim = datetime.now()
        tempo_execucao = (fim - inicio).total_seconds()
        
        # Gerar relatorio
        relatorio = self._gerar_relatorio(tema, tempo_execucao)
        
        print("\n=== PIPELINE CONCLUIDO ===")
        print(f"Tempo de execucao: {tempo_execucao:.2f} segundos")
        print(f"Documentos coletados: {len(self.documentos)}")
        print(f"Chunks gerados: {len(self.chunks)}")
        
        return relatorio
    
    def buscar(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Realiza busca nos documentos processados"""
        if not self.chunks:
            print("Nenhum documento processado. Execute o pipeline primeiro.")
            return []
            
        return self.processador.buscar_similares(query, top_k)
    
    def obter_contexto_para_query(self, query: str, max_chars: int = 2000) -> str:
        """Obtem contexto relevante para uma query"""
        if not self.chunks:
            return "Nenhum documento processado."
            
        return self.processador.obter_contexto(query, max_chars)
    
    def responder_pergunta(self, pergunta: str) -> Dict[str, Any]:
        """Responde uma pergunta usando o contexto coletado"""
        # Buscar contexto relevante
        contexto = self.obter_contexto_para_query(pergunta, max_chars=1500)
        
        if not contexto:
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
                'similaridade': resultado['similaridade']
            })
        
        # Resposta baseada no contexto (simplificada)
        resposta = f"Com base nos documentos coletados:\n\n{contexto[:800]}..."
        
        return {
            'pergunta': pergunta,
            'resposta': resposta,
            'contexto': contexto,
            'fontes': fontes
        }
    
    def _salvar_resultados(self, tema: str):
        """Salva resultados do pipeline"""
        # Criar pasta de resultados
        pasta_resultados = f"resultados_{tema.replace(' ', '_')}"
        os.makedirs(pasta_resultados, exist_ok=True)
        
        # Salvar documentos originais
        arquivo_docs = os.path.join(pasta_resultados, "documentos_originais.txt")
        self.coletor.salvar_documentos(self.documentos, arquivo_docs)
        
        # Salvar chunks processados
        arquivo_chunks = os.path.join(pasta_resultados, "chunks_processados.txt")
        self.processador.salvar_chunks(arquivo_chunks)
        
        print(f"Resultados salvos em: {pasta_resultados}/")
    
    def _gerar_relatorio(self, tema: str, tempo_execucao: float) -> Dict[str, Any]:
        """Gera relatorio do pipeline"""
        # Estatisticas dos documentos
        stats_docs = self.coletor.obter_estatisticas(self.documentos)
        
        # Estatisticas dos chunks
        stats_chunks = self.processador.obter_estatisticas()
        
        relatorio = {
            'tema': tema,
            'timestamp': datetime.now().isoformat(),
            'tempo_execucao_segundos': tempo_execucao,
            'documentos': {
                'total': len(self.documentos),
                'estatisticas': stats_docs
            },
            'chunks': {
                'total': len(self.chunks),
                'estatisticas': stats_chunks
            },
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
    
    def carregar_pipeline_existente(self, tema: str) -> bool:
        """Carrega pipeline de resultados existentes"""
        pasta_resultados = f"resultados_{tema.replace(' ', '_')}"
        arquivo_relatorio = os.path.join(pasta_resultados, "relatorio.json")
        
        if not os.path.exists(arquivo_relatorio):
            print(f"Nenhum pipeline existente encontrado para: {tema}")
            return False
            
        try:
            # Carregar relatorio
            with open(arquivo_relatorio, 'r', encoding='utf-8') as f:
                relatorio = json.load(f)
                
            print(f"Pipeline existente encontrado para: {tema}")
            print(f"Data: {relatorio.get('timestamp', 'N/A')}")
            print(f"Documentos: {relatorio.get('documentos', {}).get('total', 0)}")
            print(f"Chunks: {relatorio.get('chunks', {}).get('total', 0)}")
            
            # Aqui poderia recarregar os dados processados
            # Por simplicidade, retornamos apenas True
            return True
            
        except Exception as e:
            print(f"Erro ao carregar pipeline existente: {e}")
            return False
    
    def listar_pipelines_existentes(self) -> List[str]:
        """Lista pipelines existentes"""
        pipelines = []
        
        for item in os.listdir('.'):
            if os.path.isdir(item) and item.startswith('resultados_'):
                tema = item.replace('resultados_', '').replace('_', ' ')
                pipelines.append(tema)
                
        return pipelines

def exemplo_uso_completo():
    """Exemplo completo de uso do pipeline"""
    # Criar pipeline
    pipeline = RAGPipeline()
    
    # Executar pipeline completo
    tema = "inteligencia artificial"
    relatorio = pipeline.executar_pipeline_completo(tema, max_docs_por_fonte=3)
    
    if 'erro' in relatorio:
        print(f"Erro no pipeline: {relatorio['erro']}")
        return
    
    # Exemplos de busca
    print("\n=== EXEMPLOS DE BUSCA ===")
    
    perguntas = [
        "O que e inteligencia artificial?",
        "Como funciona machine learning?",
        "Quais sao as aplicacoes da IA?"
    ]
    
    for pergunta in perguntas:
        print(f"\nPergunta: {pergunta}")
        
        # Busca simples
        resultados = pipeline.buscar(pergunta, top_k=2)
        print(f"Encontrados {len(resultados)} resultados relevantes")
        
        for i, resultado in enumerate(resultados, 1):
            print(f"  {i}. [{resultado['fonte']}] Sim: {resultado['similaridade']:.3f}")
            print(f"     {resultado['texto'][:100]}...")
        
        # Resposta completa
        resposta_completa = pipeline.responder_pergunta(pergunta)
        print(f"\nResposta: {resposta_completa['resposta'][:200]}...")
    
    # Listar pipelines existentes
    print("\n=== PIPELINES EXISTENTES ===")
    pipelines_existentes = pipeline.listar_pipelines_existentes()
    for p in pipelines_existentes:
        print(f"  - {p}")

if __name__ == "__main__":
    exemplo_uso_completo()