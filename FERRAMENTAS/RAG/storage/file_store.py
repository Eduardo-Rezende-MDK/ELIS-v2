#!/usr/bin/env python3
"""
Sistema de persistência baseado em arquivos como alternativa ao SQLite híbrido
Usa JSON para metadados e pickle para objetos Python
"""

import json
import pickle
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.document import RawDocument, ProcessedChunk, SearchResult

class FileStore:
    """Sistema de persistência baseado em arquivos"""
    
    def __init__(self, base_path: str = "file_storage"):
        self.base_path = Path(base_path)
        self.chunks_dir = self.base_path / "chunks"
        self.docs_dir = self.base_path / "documents"
        self.metadata_file = self.base_path / "metadata.json"
        
        # Criar diretórios
        self.chunks_dir.mkdir(parents=True, exist_ok=True)
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        
        # Inicializar metadata
        self._init_metadata()
    
    def _init_metadata(self):
        """Inicializa arquivo de metadados"""
        if not self.metadata_file.exists():
            metadata = {
                "created_at": datetime.now().isoformat(),
                "total_chunks": 0,
                "total_documents": 0,
                "last_updated": datetime.now().isoformat(),
                "chunk_index": {},  # chunk_id -> arquivo
                "document_index": {}  # doc_id -> arquivo
            }
            self._save_metadata(metadata)
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Carrega metadados do arquivo"""
        with open(self.metadata_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_metadata(self, metadata: Dict[str, Any]):
        """Salva metadados no arquivo"""
        metadata["last_updated"] = datetime.now().isoformat()
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    def save_chunk(self, chunk: ProcessedChunk) -> bool:
        """Salva um chunk em arquivo"""
        try:
            # Nome do arquivo baseado no chunk_id
            filename = f"chunk_{chunk.chunk_id}.pkl"
            filepath = self.chunks_dir / filename
            
            # Salvar chunk em pickle
            with open(filepath, 'wb') as f:
                pickle.dump(chunk, f)
            
            # Atualizar metadata
            metadata = self._load_metadata()
            metadata["chunk_index"][chunk.chunk_id] = filename
            metadata["total_chunks"] = len(metadata["chunk_index"])
            self._save_metadata(metadata)
            
            return True
            
        except Exception as e:
            print(f"Erro ao salvar chunk {chunk.chunk_id}: {e}")
            return False
    
    def load_chunk(self, chunk_id: str) -> Optional[ProcessedChunk]:
        """Carrega um chunk do arquivo"""
        try:
            metadata = self._load_metadata()
            filename = metadata["chunk_index"].get(chunk_id)
            
            if not filename:
                return None
            
            filepath = self.chunks_dir / filename
            if not filepath.exists():
                return None
            
            with open(filepath, 'rb') as f:
                return pickle.load(f)
                
        except Exception as e:
            print(f"Erro ao carregar chunk {chunk_id}: {e}")
            return None
    
    def load_all_chunks(self) -> List[ProcessedChunk]:
        """Carrega todos os chunks"""
        chunks = []
        metadata = self._load_metadata()
        
        for chunk_id in metadata["chunk_index"]:
            chunk = self.load_chunk(chunk_id)
            if chunk:
                chunks.append(chunk)
        
        return chunks
    
    def save_document(self, document: RawDocument) -> bool:
        """Salva um documento em arquivo"""
        try:
            # Nome do arquivo baseado no document_id
            filename = f"doc_{document.document_id}.pkl"
            filepath = self.docs_dir / filename
            
            # Salvar documento em pickle
            with open(filepath, 'wb') as f:
                pickle.dump(document, f)
            
            # Atualizar metadata
            metadata = self._load_metadata()
            metadata["document_index"][document.document_id] = filename
            metadata["total_documents"] = len(metadata["document_index"])
            self._save_metadata(metadata)
            
            return True
            
        except Exception as e:
            print(f"Erro ao salvar documento {document.document_id}: {e}")
            return False
    
    def load_document(self, document_id: str) -> Optional[RawDocument]:
        """Carrega um documento do arquivo"""
        try:
            metadata = self._load_metadata()
            filename = metadata["document_index"].get(document_id)
            
            if not filename:
                return None
            
            filepath = self.docs_dir / filename
            if not filepath.exists():
                return None
            
            with open(filepath, 'rb') as f:
                return pickle.load(f)
                
        except Exception as e:
            print(f"Erro ao carregar documento {document_id}: {e}")
            return None
    
    def chunk_exists(self, chunk_id: str) -> bool:
        """Verifica se um chunk existe"""
        metadata = self._load_metadata()
        return chunk_id in metadata["chunk_index"]
    
    def document_exists(self, document_id: str) -> bool:
        """Verifica se um documento existe"""
        metadata = self._load_metadata()
        return document_id in metadata["document_index"]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtém estatísticas do armazenamento"""
        metadata = self._load_metadata()
        
        return {
            "total_chunks": metadata["total_chunks"],
            "total_documents": metadata["total_documents"],
            "created_at": metadata["created_at"],
            "last_updated": metadata["last_updated"],
            "storage_path": str(self.base_path),
            "chunks_files": len(list(self.chunks_dir.glob("*.pkl"))),
            "docs_files": len(list(self.docs_dir.glob("*.pkl")))
        }
    
    def clear_all(self) -> bool:
        """Remove todos os dados"""
        try:
            # Remover todos os arquivos de chunks
            for file in self.chunks_dir.glob("*.pkl"):
                file.unlink()
            
            # Remover todos os arquivos de documentos
            for file in self.docs_dir.glob("*.pkl"):
                file.unlink()
            
            # Reinicializar metadata
            self._init_metadata()
            
            print("FileStore limpo com sucesso")
            return True
            
        except Exception as e:
            print(f"Erro ao limpar FileStore: {e}")
            return False
    
    def close(self):
        """Método de fechamento (compatibilidade)"""
        print("FileStore fechado")