#!/usr/bin/env python3
"""
Sistema RAG específico para ELIS v2
Focado em: ERRO/SOLUÇÃO, Histórico de Sessão e Regras do Sistema
"""

import json
import pickle
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import hashlib
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from models.document import RawDocument, ProcessedChunk
from storage.vector_store import RAGVectorStore
from processing.document_processor import DocumentProcessor

class RAGElis:
    """
    Sistema RAG específico para ELIS v2
    Gerencia três tipos de dados:
    1. Registros de ERRO/SOLUÇÃO
    2. Histórico de Sessão
    3. Regras do Sistema
    """
    
    def __init__(self, base_path: str = "rag_elis_storage"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Inicializar componentes
        self.vector_store = RAGVectorStore({
            'storage_path': str(self.base_path),
            'embedding_dim': 384
        })
        self.document_processor = DocumentProcessor()
        
        # Contadores para IDs únicos
        self.error_counter = self._load_counter('error_counter')
        self.session_counter = self._load_counter('session_counter')
        self.rule_counter = self._load_counter('rule_counter')
    
    def _load_counter(self, counter_name: str) -> int:
        """Carrega contador de um arquivo"""
        counter_file = self.base_path / f"{counter_name}.txt"
        if counter_file.exists():
            try:
                return int(counter_file.read_text().strip())
            except:
                return 1
        return 1
    
    def _save_counter(self, counter_name: str, value: int):
        """Salva contador em arquivo"""
        counter_file = self.base_path / f"{counter_name}.txt"
        counter_file.write_text(str(value))
    
    def _generate_id(self, prefix: str, content: str) -> str:
        """Gera ID único baseado no conteúdo"""
        hash_obj = hashlib.md5(content.encode())
        return f"{prefix}_{hash_obj.hexdigest()[:8]}"
    
    # ===== REGISTRO DE ERRO/SOLUÇÃO =====
    
    def registrar_erro_solucao(self, erro: str, solucao: str, contexto: Dict[str, Any] = None) -> str:
        """
        Registra um par ERRO/SOLUÇÃO no sistema RAG
        
        Args:
            erro: Descrição do erro
            solucao: Solução aplicada
            contexto: Contexto adicional (arquivo, linha, função, etc.)
            
        Returns:
            str: ID do registro criado
        """
        try:
            # Gerar ID único
            content_for_id = f"{erro}_{solucao}"
            doc_id = self._generate_id("erro", content_for_id)
            
            # Preparar conteúdo estruturado
            conteudo = f"ERRO: {erro}\n\nSOLUÇÃO: {solucao}"
            
            if contexto:
                conteudo += "\n\nCONTEXTO:\n"
                for chave, valor in contexto.items():
                    conteudo += f"- {chave}: {valor}\n"
            
            # Criar documento
            documento = RawDocument(
                title=f"Erro/Solução #{self.error_counter}",
                content=conteudo,
                source_type="erro_solucao",
                document_id=doc_id,
                keywords=["erro", "solução", "debug"],
                source_metadata={
                    'erro': erro,
                    'solucao': solucao,
                    'contexto': contexto or {},
                    'timestamp': datetime.now().isoformat(),
                    'tipo': 'erro_solucao'
                }
            )
            
            # Processar e armazenar
            chunks = self.document_processor.process_documents([documento])
            if chunks:
                self.vector_store.add_chunks(chunks)
                
                # Incrementar contador
                self.error_counter += 1
                self._save_counter('error_counter', self.error_counter)
                
                print(f"Erro/Solução registrado: {doc_id}")
                return doc_id
            else:
                raise Exception("Falha ao processar documento")
                
        except Exception as e:
            print(f"Erro ao registrar erro/solução: {e}")
            return ""
    
    def buscar_solucoes(self, erro_query: str, limite: int = 5) -> List[Dict[str, Any]]:
        """
        Busca soluções para um erro específico
        
        Args:
            erro_query: Descrição do erro para buscar
            limite: Número máximo de resultados
            
        Returns:
            Lista de soluções encontradas
        """
        try:
            # Processar query
            query_doc = RawDocument(
                title="Query",
                content=erro_query,
                source_type="query",
                document_id="temp_query"
            )
            
            query_chunks = self.document_processor.process_documents([query_doc])
            if not query_chunks or not query_chunks[0].embedding:
                return []
            
            # Buscar no vector store
            resultados = self.vector_store.search(
                query_chunks[0].embedding,
                top_k=limite,
                filters={'source_type': 'erro_solucao'}
            )
            
            # Formatar resultados
            solucoes = []
            for resultado in resultados:
                chunk = resultado.chunk
                metadata = chunk.source_metadata
                
                solucoes.append({
                    'id': chunk.document_id,
                    'erro': metadata.get('erro', ''),
                    'solucao': metadata.get('solucao', ''),
                    'contexto': metadata.get('contexto', {}),
                    'timestamp': metadata.get('timestamp', ''),
                    'score': resultado.score,
                    'conteudo_completo': chunk.content
                })
            
            return solucoes
            
        except Exception as e:
            print(f"Erro ao buscar soluções: {e}")
            return []
    
    # ===== HISTÓRICO DE SESSÃO =====
    
    def registrar_sessao(self, sessao_id: str, acao: str, detalhes: Dict[str, Any] = None) -> str:
        """
        Registra uma ação de sessão no histórico
        
        Args:
            sessao_id: ID da sessão
            acao: Ação realizada
            detalhes: Detalhes adicionais da ação
            
        Returns:
            str: ID do registro criado
        """
        try:
            # Gerar ID único
            content_for_id = f"{sessao_id}_{acao}_{datetime.now().isoformat()}"
            doc_id = self._generate_id("sessao", content_for_id)
            
            # Preparar conteúdo
            conteudo = f"SESSÃO: {sessao_id}\n\nAÇÃO: {acao}\n\nTIMESTAMP: {datetime.now().isoformat()}"
            
            if detalhes:
                conteudo += "\n\nDETALHES:\n"
                for chave, valor in detalhes.items():
                    conteudo += f"- {chave}: {valor}\n"
            
            # Criar documento
            documento = RawDocument(
                title=f"Sessão {sessao_id} - {acao}",
                content=conteudo,
                source_type="historico_sessao",
                document_id=doc_id,
                keywords=["sessão", "histórico", acao],
                source_metadata={
                    'sessao_id': sessao_id,
                    'acao': acao,
                    'detalhes': detalhes or {},
                    'timestamp': datetime.now().isoformat(),
                    'tipo': 'historico_sessao'
                }
            )
            
            # Processar e armazenar
            chunks = self.document_processor.process_documents([documento])
            if chunks:
                self.vector_store.add_chunks(chunks)
                
                # Incrementar contador
                self.session_counter += 1
                self._save_counter('session_counter', self.session_counter)
                
                print(f"Sessão registrada: {doc_id}")
                return doc_id
            else:
                raise Exception("Falha ao processar documento")
                
        except Exception as e:
            print(f"Erro ao registrar sessão: {e}")
            return ""
    
    def buscar_historico_sessao(self, sessao_id: str = None, acao: str = None, limite: int = 10) -> List[Dict[str, Any]]:
        """
        Busca no histórico de sessões
        
        Args:
            sessao_id: ID da sessão (opcional)
            acao: Tipo de ação (opcional)
            limite: Número máximo de resultados
            
        Returns:
            Lista de registros de sessão
        """
        try:
            # Construir query
            query_parts = []
            if sessao_id:
                query_parts.append(f"sessão {sessao_id}")
            if acao:
                query_parts.append(f"ação {acao}")
            
            if not query_parts:
                query_parts.append("histórico sessão")
            
            query_text = " ".join(query_parts)
            
            # Processar query
            query_doc = RawDocument(
                title="Query",
                content=query_text,
                source_type="query",
                document_id="temp_query"
            )
            
            query_chunks = self.document_processor.process_documents([query_doc])
            if not query_chunks or not query_chunks[0].embedding:
                return []
            
            # Buscar no vector store
            resultados = self.vector_store.search(
                query_chunks[0].embedding,
                top_k=limite,
                filters={'source_type': 'historico_sessao'}
            )
            
            # Formatar resultados
            historico = []
            for resultado in resultados:
                chunk = resultado.chunk
                metadata = chunk.source_metadata
                
                # Filtrar por sessão se especificado
                if sessao_id and metadata.get('sessao_id') != sessao_id:
                    continue
                
                # Filtrar por ação se especificado
                if acao and metadata.get('acao') != acao:
                    continue
                
                historico.append({
                    'id': chunk.document_id,
                    'sessao_id': metadata.get('sessao_id', ''),
                    'acao': metadata.get('acao', ''),
                    'detalhes': metadata.get('detalhes', {}),
                    'timestamp': metadata.get('timestamp', ''),
                    'score': resultado.score,
                    'conteudo_completo': chunk.content
                })
            
            # Ordenar por timestamp (mais recente primeiro)
            historico.sort(key=lambda x: x['timestamp'], reverse=True)
            
            return historico
            
        except Exception as e:
            print(f"Erro ao buscar histórico: {e}")
            return []
    
    # ===== REGRAS DO SISTEMA =====
    
    def registrar_regra(self, titulo: str, descricao: str, categoria: str = "geral", 
                       aplicacao: str = "", validacao: str = "") -> str:
        """
        Registra uma regra do sistema no RAG
        
        Args:
            titulo: Título da regra
            descricao: Descrição completa da regra
            categoria: Categoria da regra
            aplicacao: Como aplicar a regra
            validacao: Como validar a regra
            
        Returns:
            str: ID da regra criada
        """
        try:
            # Gerar ID único
            content_for_id = f"{titulo}_{categoria}"
            doc_id = self._generate_id("regra", content_for_id)
            
            # Preparar conteúdo estruturado
            conteudo = f"REGRA: {titulo}\n\nCATEGORIA: {categoria}\n\nDESCRIÇÃO: {descricao}"
            
            if aplicacao:
                conteudo += f"\n\nAPLICAÇÃO: {aplicacao}"
            
            if validacao:
                conteudo += f"\n\nVALIDAÇÃO: {validacao}"
            
            # Criar documento
            documento = RawDocument(
                title=f"Regra: {titulo}",
                content=conteudo,
                source_type="regra_sistema",
                document_id=doc_id,
                keywords=["regra", categoria, "sistema"],
                source_metadata={
                    'titulo': titulo,
                    'descricao': descricao,
                    'categoria': categoria,
                    'aplicacao': aplicacao,
                    'validacao': validacao,
                    'timestamp': datetime.now().isoformat(),
                    'tipo': 'regra_sistema'
                }
            )
            
            # Processar e armazenar
            chunks = self.document_processor.process_documents([documento])
            if chunks:
                self.vector_store.add_chunks(chunks)
                
                # Incrementar contador
                self.rule_counter += 1
                self._save_counter('rule_counter', self.rule_counter)
                
                print(f"Regra registrada: {doc_id}")
                return doc_id
            else:
                raise Exception("Falha ao processar documento")
                
        except Exception as e:
            print(f"Erro ao registrar regra: {e}")
            return ""
    
    def buscar_regras(self, query: str, categoria: str = None, limite: int = 5) -> List[Dict[str, Any]]:
        """
        Busca regras do sistema
        
        Args:
            query: Termo de busca
            categoria: Categoria específica (opcional)
            limite: Número máximo de resultados
            
        Returns:
            Lista de regras encontradas
        """
        try:
            # Processar query
            query_doc = RawDocument(
                title="Query",
                content=query,
                source_type="query",
                document_id="temp_query"
            )
            
            query_chunks = self.document_processor.process_documents([query_doc])
            if not query_chunks or not query_chunks[0].embedding:
                return []
            
            # Buscar no vector store
            filtros = {'source_type': 'regra_sistema'}
            if categoria:
                filtros['categoria'] = categoria
            
            resultados = self.vector_store.search(
                query_chunks[0].embedding,
                top_k=limite,
                filters=filtros
            )
            
            # Formatar resultados
            regras = []
            for resultado in resultados:
                chunk = resultado.chunk
                metadata = chunk.source_metadata
                
                regras.append({
                    'id': chunk.document_id,
                    'titulo': metadata.get('titulo', ''),
                    'descricao': metadata.get('descricao', ''),
                    'categoria': metadata.get('categoria', ''),
                    'aplicacao': metadata.get('aplicacao', ''),
                    'validacao': metadata.get('validacao', ''),
                    'timestamp': metadata.get('timestamp', ''),
                    'score': resultado.score,
                    'conteudo_completo': chunk.content
                })
            
            return regras
            
        except Exception as e:
            print(f"Erro ao buscar regras: {e}")
            return []
    
    def migrar_regras_existentes(self, arquivo_regras: str) -> int:
        """
        Migra regras existentes de um arquivo para o RAG
        
        Args:
            arquivo_regras: Caminho para o arquivo de regras
            
        Returns:
            int: Número de regras migradas
        """
        try:
            regras_path = Path(arquivo_regras)
            if not regras_path.exists():
                print(f"Arquivo não encontrado: {arquivo_regras}")
                return 0
            
            # Ler conteúdo do arquivo
            conteudo = regras_path.read_text(encoding='utf-8')
            
            # Dividir em regras (assumindo separação por linhas vazias ou numeração)
            regras_texto = []
            if '===' in conteudo:
                regras_texto = conteudo.split('===')
            elif '\n\n' in conteudo:
                regras_texto = conteudo.split('\n\n')
            else:
                # Tratar como uma única regra
                regras_texto = [conteudo]
            
            migradas = 0
            for i, regra_texto in enumerate(regras_texto):
                regra_texto = regra_texto.strip()
                if not regra_texto:
                    continue
                
                # Extrair título (primeira linha)
                linhas = regra_texto.split('\n')
                titulo = linhas[0].strip() if linhas else f"Regra {i+1}"
                descricao = '\n'.join(linhas[1:]).strip() if len(linhas) > 1 else regra_texto
                
                # Registrar regra
                if self.registrar_regra(titulo, descricao, "migrada"):
                    migradas += 1
            
            print(f"Migradas {migradas} regras de {arquivo_regras}")
            return migradas
            
        except Exception as e:
            print(f"Erro ao migrar regras: {e}")
            return 0
    
    # ===== MÉTODOS UTILITÁRIOS =====
    
    def obter_estatisticas(self) -> Dict[str, Any]:
        """
        Obtém estatísticas do sistema RAG ELIS
        
        Returns:
            Dicionário com estatísticas detalhadas
        """
        try:
            stats_vector = self.vector_store.get_statistics()
            
            # Contar por tipo
            tipos = {'erro_solucao': 0, 'historico_sessao': 0, 'regra_sistema': 0}
            
            for chunk in self.vector_store.chunks:
                source_type = chunk.source_type
                if source_type in tipos:
                    tipos[source_type] += 1
            
            return {
                'total_registros': len(self.vector_store.chunks),
                'por_tipo': tipos,
                'contadores': {
                    'erro_counter': self.error_counter,
                    'session_counter': self.session_counter,
                    'rule_counter': self.rule_counter
                },
                'vector_store_stats': stats_vector,
                'storage_path': str(self.base_path)
            }
            
        except Exception as e:
            print(f"Erro ao obter estatísticas: {e}")
            return {}
    
    def limpar_tudo(self) -> bool:
        """
        Remove todos os dados do sistema RAG ELIS
        
        Returns:
            bool: True se limpeza foi bem-sucedida
        """
        try:
            # Limpar vector store
            self.vector_store.clear_all()
            
            # Resetar contadores
            self.error_counter = 1
            self.session_counter = 1
            self.rule_counter = 1
            
            self._save_counter('error_counter', 1)
            self._save_counter('session_counter', 1)
            self._save_counter('rule_counter', 1)
            
            print("Sistema RAG ELIS limpo com sucesso")
            return True
            
        except Exception as e:
            print(f"Erro ao limpar sistema: {e}")
            return False
    
    def fechar(self):
        """
        Fecha o sistema RAG ELIS
        """
        self.vector_store.close()
        print("Sistema RAG ELIS fechado")