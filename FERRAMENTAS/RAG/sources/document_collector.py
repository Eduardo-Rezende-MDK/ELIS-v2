#!/usr/bin/env python3
"""
Coletor de documentos locais (PDFs, TXT, DOCX)
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.document import RawDocument

class DocumentCollector:
    """Coletor para documentos locais"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.supported_extensions = self.config.get('supported_extensions', ['.txt', '.md'])
        
    def collect_from_directory(self, directory_path: str, recursive: bool = True) -> List[RawDocument]:
        """Coleta documentos de um diretorio"""
        documents = []
        
        try:
            path = Path(directory_path)
            
            if not path.exists() or not path.is_dir():
                print(f"Diretorio nao encontrado: {directory_path}")
                return documents
                
            # Buscar arquivos
            if recursive:
                files = path.rglob('*')
            else:
                files = path.glob('*')
                
            for file_path in files:
                if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                    try:
                        document = self._process_file(file_path)
                        if document:
                            documents.append(document)
                    except Exception as e:
                        print(f"Erro ao processar arquivo {file_path}: {e}")
                        continue
                        
        except Exception as e:
            print(f"Erro ao coletar documentos do diretorio: {e}")
            
        return documents
    
    def collect_single_file(self, file_path: str) -> Optional[RawDocument]:
        """Coleta um unico arquivo"""
        try:
            path = Path(file_path)
            
            if not path.exists() or not path.is_file():
                print(f"Arquivo nao encontrado: {file_path}")
                return None
                
            return self._process_file(path)
            
        except Exception as e:
            print(f"Erro ao processar arquivo: {e}")
            return None
    
    def _process_file(self, file_path: Path) -> Optional[RawDocument]:
        """Processa um arquivo individual"""
        try:
            # Ler conteudo baseado na extensao
            if file_path.suffix.lower() in ['.txt', '.md']:
                content = self._read_text_file(file_path)
            else:
                print(f"Tipo de arquivo nao suportado: {file_path.suffix}")
                return None
                
            if not content or len(content.strip()) < 50:
                return None
                
            # Obter metadados do arquivo
            stat = file_path.stat()
            
            # Criar documento
            document = RawDocument(
                title=file_path.stem,
                content=content.strip(),
                source_type='local_file',
                url=str(file_path.absolute()),
                authors=[],
                publication_date=datetime.fromtimestamp(stat.st_mtime),
                abstract=content[:200] + '...' if len(content) > 200 else content,
                keywords=self._extract_keywords_from_filename(file_path.stem),
                language='pt',  # Assumir portugues por padrao
                external_id=str(file_path.absolute()),
                source_metadata={
                    'file_path': str(file_path.absolute()),
                    'file_size': stat.st_size,
                    'file_extension': file_path.suffix,
                    'created_time': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    'modified_time': datetime.fromtimestamp(stat.st_mtime).isoformat()
                }
            )
            
            # Calcular score de qualidade
            document.quality_score = self._calculate_file_quality_score(document)
            
            return document
            
        except Exception as e:
            print(f"Erro ao processar arquivo {file_path}: {e}")
            return None
    
    def _read_text_file(self, file_path: Path) -> str:
        """Le arquivo de texto"""
        encodings = ['utf-8', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
                
        raise ValueError(f"Nao foi possivel decodificar o arquivo {file_path}")
    
    def _extract_keywords_from_filename(self, filename: str) -> List[str]:
        """Extrai palavras-chave do nome do arquivo"""
        # Separar por underscores, hifens e espacos
        words = filename.replace('_', ' ').replace('-', ' ').split()
        
        # Filtrar palavras muito pequenas
        keywords = [word.lower() for word in words if len(word) > 2]
        
        return keywords[:5]  # Maximo 5 keywords
    
    def _calculate_file_quality_score(self, document: RawDocument) -> float:
        """Calcula score de qualidade para arquivos locais"""
        score = 0.5  # Score base
        
        # Tamanho do conteudo
        content_length = len(document.content)
        if content_length > 2000:
            score += 0.2
        elif content_length > 500:
            score += 0.1
        elif content_length < 100:
            score -= 0.2
            
        # Extensao do arquivo
        file_ext = document.source_metadata.get('file_extension', '').lower()
        if file_ext in ['.md', '.txt']:
            score += 0.1
            
        # Tamanho do arquivo
        file_size = document.source_metadata.get('file_size', 0)
        if file_size > 1024:  # Maior que 1KB
            score += 0.1
            
        # Presenca de keywords
        if len(document.keywords) > 2:
            score += 0.1
            
        return min(score, 1.0)
    
    def get_supported_extensions(self) -> List[str]:
        """Retorna extensoes suportadas"""
        return self.supported_extensions
    
    def add_supported_extension(self, extension: str):
        """Adiciona nova extensao suportada"""
        if extension not in self.supported_extensions:
            self.supported_extensions.append(extension)