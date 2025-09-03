#!/usr/bin/env python3
"""
RAG File Manager - Sistema CRUD completo para RAG baseado em arquivos
Expande as funcionalidades do FileStore com operações CRUD intuitivas
"""

import json
import pickle
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import sys
import re
from dataclasses import asdict

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.document import RawDocument, ProcessedChunk, SearchResult
from storage.file_store import FileStore

class RAGFileManager:
    """
    Gerenciador CRUD completo para sistema RAG baseado em arquivos
    Fornece operações intuitivas: Create, Read, Update, Delete, Search
    """
    
    def __init__(self, base_path: str = "rag_storage"):
        self.base_path = Path(base_path)
        self.file_store = FileStore(base_path)
        
    # ===== OPERAÇÕES CREATE (Criar) =====
    
    def criar_documento(self, titulo: str, conteudo: str, fonte: str, **kwargs) -> str:
        """
        Cria um novo documento no sistema
        
        Args:
            titulo: Título do documento
            conteudo: Conteúdo do documento
            fonte: Fonte do documento (wikipedia, arxiv, etc.)
            **kwargs: Metadados adicionais (url, autores, etc.)
            
        Returns:
            str: ID do documento criado
        """
        # Gerar ID único
        doc_id = f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(titulo) % 10000}"
        
        # Criar documento
        documento = RawDocument(
            title=titulo,
            content=conteudo,
            source_type=fonte,
            document_id=doc_id,
            url=kwargs.get('url', ''),
            authors=kwargs.get('autores', []),
            abstract=kwargs.get('resumo', ''),
            keywords=kwargs.get('palavras_chave', []),
            language=kwargs.get('idioma', 'pt'),
            source_metadata=kwargs.get('metadados', {})
        )
        
        # Salvar
        if self.file_store.save_document(documento):
            print(f"Documento criado: {doc_id}")
            return doc_id
        else:
            raise Exception(f"Erro ao criar documento: {titulo}")
    
    def criar_chunk(self, conteudo: str, doc_id: str, embedding: Optional[List[float]] = None, **kwargs) -> str:
        """
        Cria um novo chunk no sistema
        
        Args:
            conteudo: Conteúdo do chunk
            doc_id: ID do documento pai
            embedding: Vetor de embedding (opcional)
            **kwargs: Metadados adicionais
            
        Returns:
            str: ID do chunk criado
        """
        # Gerar ID único
        chunk_id = f"chunk_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(conteudo) % 10000}"
        
        # Criar chunk
        chunk = ProcessedChunk(
            chunk_id=chunk_id,
            document_id=doc_id,
            content=conteudo,
            embedding=embedding or [],
            chunk_index=kwargs.get('indice', 0),
            start_char=kwargs.get('inicio_char', 0),
            end_char=kwargs.get('fim_char', len(conteudo)),
            metadata=kwargs.get('metadados', {})
        )
        
        # Salvar
        if self.file_store.save_chunk(chunk):
            print(f"Chunk criado: {chunk_id}")
            return chunk_id
        else:
            raise Exception(f"Erro ao criar chunk para documento: {doc_id}")
    
    # ===== OPERAÇÕES READ (Ler) =====
    
    def ler_documento(self, doc_id: str) -> Optional[RawDocument]:
        """
        Lê um documento pelo ID
        
        Args:
            doc_id: ID do documento
            
        Returns:
            RawDocument ou None se não encontrado
        """
        return self.file_store.load_document(doc_id)
    
    def ler_chunk(self, chunk_id: str) -> Optional[ProcessedChunk]:
        """
        Lê um chunk pelo ID
        
        Args:
            chunk_id: ID do chunk
            
        Returns:
            ProcessedChunk ou None se não encontrado
        """
        return self.file_store.load_chunk(chunk_id)
    
    def listar_documentos(self, limite: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Lista todos os documentos com informações básicas
        
        Args:
            limite: Número máximo de documentos (opcional)
            
        Returns:
            Lista de dicionários com informações dos documentos
        """
        metadata = self.file_store._load_metadata()
        documentos = []
        
        count = 0
        for doc_id in metadata["document_index"]:
            if limite and count >= limite:
                break
                
            doc = self.ler_documento(doc_id)
            if doc:
                documentos.append({
                    'id': doc.document_id,
                    'titulo': doc.title,
                    'fonte': doc.source_type,
                    'tamanho': len(doc.content),
                    'data_coleta': doc.collection_timestamp.isoformat() if doc.collection_timestamp else None,
                    'url': doc.url
                })
                count += 1
        
        return documentos
    
    def listar_chunks(self, doc_id: Optional[str] = None, limite: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Lista chunks, opcionalmente filtrados por documento
        
        Args:
            doc_id: ID do documento para filtrar (opcional)
            limite: Número máximo de chunks (opcional)
            
        Returns:
            Lista de dicionários com informações dos chunks
        """
        metadata = self.file_store._load_metadata()
        chunks = []
        
        count = 0
        for chunk_id in metadata["chunk_index"]:
            if limite and count >= limite:
                break
                
            chunk = self.ler_chunk(chunk_id)
            if chunk and (not doc_id or chunk.document_id == doc_id):
                chunks.append({
                    'id': chunk.chunk_id,
                    'documento_id': chunk.document_id,
                    'conteudo_preview': chunk.content[:100] + '...' if len(chunk.content) > 100 else chunk.content,
                    'tamanho': len(chunk.content),
                    'tem_embedding': len(chunk.embedding) > 0,
                    'indice': chunk.chunk_index
                })
                count += 1
        
        return chunks
    
    # ===== OPERAÇÕES UPDATE (Atualizar) =====
    
    def atualizar_documento(self, doc_id: str, **kwargs) -> bool:
        """
        Atualiza campos de um documento existente
        
        Args:
            doc_id: ID do documento
            **kwargs: Campos a serem atualizados
            
        Returns:
            bool: True se atualizado com sucesso
        """
        documento = self.ler_documento(doc_id)
        if not documento:
            print(f"Documento não encontrado: {doc_id}")
            return False
        
        # Atualizar campos
        if 'titulo' in kwargs:
            documento.title = kwargs['titulo']
        if 'conteudo' in kwargs:
            documento.content = kwargs['conteudo']
        if 'fonte' in kwargs:
            documento.source_type = kwargs['fonte']
        if 'url' in kwargs:
            documento.url = kwargs['url']
        if 'autores' in kwargs:
            documento.authors = kwargs['autores']
        if 'resumo' in kwargs:
            documento.abstract = kwargs['resumo']
        if 'palavras_chave' in kwargs:
            documento.keywords = kwargs['palavras_chave']
        if 'metadados' in kwargs:
            documento.source_metadata.update(kwargs['metadados'])
        
        # Salvar
        if self.file_store.save_document(documento):
            print(f"Documento atualizado: {doc_id}")
            return True
        else:
            print(f"Erro ao atualizar documento: {doc_id}")
            return False
    
    def atualizar_chunk(self, chunk_id: str, **kwargs) -> bool:
        """
        Atualiza campos de um chunk existente
        
        Args:
            chunk_id: ID do chunk
            **kwargs: Campos a serem atualizados
            
        Returns:
            bool: True se atualizado com sucesso
        """
        chunk = self.ler_chunk(chunk_id)
        if not chunk:
            print(f"Chunk não encontrado: {chunk_id}")
            return False
        
        # Atualizar campos
        if 'conteudo' in kwargs:
            chunk.content = kwargs['conteudo']
        if 'embedding' in kwargs:
            chunk.embedding = kwargs['embedding']
        if 'metadados' in kwargs:
            chunk.metadata.update(kwargs['metadados'])
        if 'indice' in kwargs:
            chunk.chunk_index = kwargs['indice']
        
        # Salvar
        if self.file_store.save_chunk(chunk):
            print(f"Chunk atualizado: {chunk_id}")
            return True
        else:
            print(f"Erro ao atualizar chunk: {chunk_id}")
            return False
    
    # ===== OPERAÇÕES DELETE (Excluir) =====
    
    def excluir_documento(self, doc_id: str, excluir_chunks: bool = True) -> bool:
        """
        Exclui um documento e opcionalmente seus chunks
        
        Args:
            doc_id: ID do documento
            excluir_chunks: Se deve excluir chunks relacionados
            
        Returns:
            bool: True se excluído com sucesso
        """
        try:
            # Excluir chunks relacionados se solicitado
            if excluir_chunks:
                chunks_excluidos = self.excluir_chunks_por_documento(doc_id)
                print(f"Chunks excluídos: {chunks_excluidos}")
            
            # Excluir arquivo do documento
            metadata = self.file_store._load_metadata()
            filename = metadata["document_index"].get(doc_id)
            
            if filename:
                filepath = self.file_store.docs_dir / filename
                if filepath.exists():
                    filepath.unlink()
                
                # Atualizar metadata
                del metadata["document_index"][doc_id]
                metadata["total_documents"] = len(metadata["document_index"])
                self.file_store._save_metadata(metadata)
                
                print(f"Documento excluído: {doc_id}")
                return True
            else:
                print(f"Documento não encontrado: {doc_id}")
                return False
                
        except Exception as e:
            print(f"Erro ao excluir documento {doc_id}: {e}")
            return False
    
    def excluir_chunk(self, chunk_id: str) -> bool:
        """
        Exclui um chunk específico
        
        Args:
            chunk_id: ID do chunk
            
        Returns:
            bool: True se excluído com sucesso
        """
        try:
            # Excluir arquivo do chunk
            metadata = self.file_store._load_metadata()
            filename = metadata["chunk_index"].get(chunk_id)
            
            if filename:
                filepath = self.file_store.chunks_dir / filename
                if filepath.exists():
                    filepath.unlink()
                
                # Atualizar metadata
                del metadata["chunk_index"][chunk_id]
                metadata["total_chunks"] = len(metadata["chunk_index"])
                self.file_store._save_metadata(metadata)
                
                print(f"Chunk excluído: {chunk_id}")
                return True
            else:
                print(f"Chunk não encontrado: {chunk_id}")
                return False
                
        except Exception as e:
            print(f"Erro ao excluir chunk {chunk_id}: {e}")
            return False
    
    def excluir_chunks_por_documento(self, doc_id: str) -> int:
        """
        Exclui todos os chunks de um documento
        
        Args:
            doc_id: ID do documento
            
        Returns:
            int: Número de chunks excluídos
        """
        chunks_para_excluir = []
        metadata = self.file_store._load_metadata()
        
        # Encontrar chunks do documento
        for chunk_id in metadata["chunk_index"]:
            chunk = self.ler_chunk(chunk_id)
            if chunk and chunk.document_id == doc_id:
                chunks_para_excluir.append(chunk_id)
        
        # Excluir chunks
        excluidos = 0
        for chunk_id in chunks_para_excluir:
            if self.excluir_chunk(chunk_id):
                excluidos += 1
        
        return excluidos
    
    # ===== OPERAÇÕES SEARCH (Buscar) =====
    
    def buscar_documentos(self, termo: str, campo: str = 'titulo', limite: int = 10) -> List[Dict[str, Any]]:
        """
        Busca documentos por termo em campo específico
        
        Args:
            termo: Termo de busca
            campo: Campo para buscar ('titulo', 'conteudo', 'fonte', 'autor')
            limite: Número máximo de resultados
            
        Returns:
            Lista de documentos encontrados
        """
        resultados = []
        metadata = self.file_store._load_metadata()
        
        count = 0
        for doc_id in metadata["document_index"]:
            if count >= limite:
                break
                
            doc = self.ler_documento(doc_id)
            if not doc:
                continue
            
            # Verificar se o termo está no campo especificado
            encontrado = False
            termo_lower = termo.lower()
            
            if campo == 'titulo' and termo_lower in doc.title.lower():
                encontrado = True
            elif campo == 'conteudo' and termo_lower in doc.content.lower():
                encontrado = True
            elif campo == 'fonte' and termo_lower in doc.source_type.lower():
                encontrado = True
            elif campo == 'autor' and any(termo_lower in autor.lower() for autor in doc.authors):
                encontrado = True
            
            if encontrado:
                resultados.append({
                    'id': doc.document_id,
                    'titulo': doc.title,
                    'fonte': doc.source_type,
                    'preview': doc.content[:200] + '...' if len(doc.content) > 200 else doc.content,
                    'score': 1.0,  # Score simples para busca textual
                    'url': doc.url
                })
                count += 1
        
        return resultados
    
    def buscar_chunks(self, termo: str, limite: int = 10) -> List[Dict[str, Any]]:
        """
        Busca chunks por termo no conteúdo
        
        Args:
            termo: Termo de busca
            limite: Número máximo de resultados
            
        Returns:
            Lista de chunks encontrados
        """
        resultados = []
        metadata = self.file_store._load_metadata()
        
        count = 0
        termo_lower = termo.lower()
        
        for chunk_id in metadata["chunk_index"]:
            if count >= limite:
                break
                
            chunk = self.ler_chunk(chunk_id)
            if not chunk:
                continue
            
            if termo_lower in chunk.content.lower():
                resultados.append({
                    'id': chunk.chunk_id,
                    'documento_id': chunk.document_id,
                    'conteudo': chunk.content,
                    'score': 1.0,
                    'indice': chunk.chunk_index
                })
                count += 1
        
        return resultados
    
    # ===== OPERAÇÕES UTILITÁRIAS =====
    
    def obter_estatisticas(self) -> Dict[str, Any]:
        """
        Obtém estatísticas completas do sistema
        
        Returns:
            Dicionário com estatísticas detalhadas
        """
        stats = self.file_store.get_statistics()
        
        # Adicionar estatísticas por fonte
        fontes = {}
        metadata = self.file_store._load_metadata()
        
        for doc_id in metadata["document_index"]:
            doc = self.ler_documento(doc_id)
            if doc:
                fonte = doc.source_type
                if fonte not in fontes:
                    fontes[fonte] = 0
                fontes[fonte] += 1
        
        stats['documentos_por_fonte'] = fontes
        return stats
    
    def verificar_integridade(self) -> Dict[str, Any]:
        """
        Verifica integridade dos dados armazenados
        
        Returns:
            Relatório de integridade
        """
        relatorio = {
            'documentos_ok': 0,
            'documentos_erro': 0,
            'chunks_ok': 0,
            'chunks_erro': 0,
            'chunks_orfaos': 0,
            'erros': []
        }
        
        metadata = self.file_store._load_metadata()
        
        # Verificar documentos
        for doc_id in metadata["document_index"]:
            doc = self.ler_documento(doc_id)
            if doc:
                relatorio['documentos_ok'] += 1
            else:
                relatorio['documentos_erro'] += 1
                relatorio['erros'].append(f"Documento não carregável: {doc_id}")
        
        # Verificar chunks
        docs_existentes = set(metadata["document_index"].keys())
        
        for chunk_id in metadata["chunk_index"]:
            chunk = self.ler_chunk(chunk_id)
            if chunk:
                relatorio['chunks_ok'] += 1
                # Verificar se documento pai existe
                if chunk.document_id not in docs_existentes:
                    relatorio['chunks_orfaos'] += 1
                    relatorio['erros'].append(f"Chunk órfão: {chunk_id} (doc: {chunk.document_id})")
            else:
                relatorio['chunks_erro'] += 1
                relatorio['erros'].append(f"Chunk não carregável: {chunk_id}")
        
        return relatorio
    
    def limpar_tudo(self) -> bool:
        """
        Remove todos os dados do sistema
        
        Returns:
            bool: True se limpeza foi bem-sucedida
        """
        return self.file_store.clear_all()
    
    def fechar(self):
        """
        Fecha o gerenciador
        """
        self.file_store.close()
        print("RAGFileManager fechado")