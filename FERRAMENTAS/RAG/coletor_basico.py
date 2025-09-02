#!/usr/bin/env python3
"""
Coletor basico de dados para sistema RAG
Coleta dados da Wikipedia e ArXiv
"""

import requests
import arxiv
from bs4 import BeautifulSoup
import time
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class Documento:
    """Classe para representar um documento coletado"""
    titulo: str
    conteudo: str
    fonte: str
    url: str = ""
    autor: str = ""
    data: str = ""
    
class ColetorBasico:
    """Coletor basico multi-fonte"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'RAG-Coletor/1.0'
        })
        
    def coletar_wikipedia(self, termo: str, max_resultados: int = 5) -> List[Documento]:
        """Coleta artigos da Wikipedia"""
        documentos = []
        
        try:
            # Buscar artigos relacionados na Wikipedia em portugues
            search_url = "https://pt.wikipedia.org/w/api.php"
            params = {
                'action': 'query',
                'format': 'json',
                'list': 'search',
                'srsearch': termo,
                'srlimit': max_resultados
            }
            
            response = self.session.get(search_url, params=params)
            response.raise_for_status()
            
            resultados = response.json()
            
            for item in resultados.get('query', {}).get('search', []):
                titulo = item.get('title', '')
                
                # Obter conteudo do artigo usando API de extratos
                content_url = "https://pt.wikipedia.org/w/api.php"
                content_params = {
                    'action': 'query',
                    'format': 'json',
                    'prop': 'extracts',
                    'titles': titulo,
                    'exintro': True,
                    'explaintext': True
                }
                
                try:
                    content_response = self.session.get(content_url, params=content_params)
                    content_response.raise_for_status()
                    
                    content_data = content_response.json()
                    pages = content_data.get('query', {}).get('pages', {})
                    
                    # Pegar a primeira pagina (unica)
                    page_data = next(iter(pages.values()), {})
                    conteudo = page_data.get('extract', '')
                    
                    documento = Documento(
                        titulo=titulo,
                        conteudo=conteudo,
                        fonte='wikipedia',
                        url=f"https://pt.wikipedia.org/wiki/{titulo.replace(' ', '_')}",
                        data=''
                    )
                    
                    if documento.conteudo and len(documento.conteudo) > 100:
                        documentos.append(documento)
                        
                    time.sleep(0.5)  # Rate limiting
                    
                except Exception as e:
                    print(f"Erro ao obter conteudo de {titulo}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Erro na busca Wikipedia: {e}")
            
        return documentos
    
    def coletar_arxiv(self, termo: str, max_resultados: int = 5) -> List[Documento]:
        """Coleta artigos do ArXiv"""
        documentos = []
        
        try:
            # Configurar cliente ArXiv
            client = arxiv.Client()
            
            # Criar query de busca
            search = arxiv.Search(
                query=termo,
                max_results=max_resultados,
                sort_by=arxiv.SortCriterion.Relevance
            )
            
            # Executar busca
            for result in client.results(search):
                documento = Documento(
                    titulo=result.title,
                    conteudo=result.summary,
                    fonte='arxiv',
                    url=result.entry_id,
                    autor=', '.join([author.name for author in result.authors]),
                    data=result.published.strftime('%Y-%m-%d') if result.published else ''
                )
                
                if documento.conteudo and len(documento.conteudo) > 100:
                    documentos.append(documento)
                    
                time.sleep(0.5)  # Rate limiting
                
        except Exception as e:
            print(f"Erro na busca ArXiv: {e}")
            
        return documentos
    
    def coletar_por_tema(self, tema: str, max_por_fonte: int = 5) -> List[Documento]:
        """Coleta documentos de todas as fontes para um tema"""
        todos_documentos = []
        
        print(f"Coletando dados sobre: {tema}")
        
        # Coletar da Wikipedia
        print("Coletando da Wikipedia...")
        docs_wiki = self.coletar_wikipedia(tema, max_por_fonte)
        todos_documentos.extend(docs_wiki)
        print(f"Wikipedia: {len(docs_wiki)} documentos")
        
        # Coletar do ArXiv
        print("Coletando do ArXiv...")
        docs_arxiv = self.coletar_arxiv(tema, max_por_fonte)
        todos_documentos.extend(docs_arxiv)
        print(f"ArXiv: {len(docs_arxiv)} documentos")
        
        print(f"Total coletado: {len(todos_documentos)} documentos")
        
        return todos_documentos
    
    def salvar_documentos(self, documentos: List[Documento], arquivo: str = "documentos_coletados.txt"):
        """Salva documentos em arquivo texto"""
        try:
            with open(arquivo, 'w', encoding='utf-8') as f:
                for i, doc in enumerate(documentos, 1):
                    f.write(f"=== DOCUMENTO {i} ===\n")
                    f.write(f"Titulo: {doc.titulo}\n")
                    f.write(f"Fonte: {doc.fonte}\n")
                    f.write(f"URL: {doc.url}\n")
                    f.write(f"Autor: {doc.autor}\n")
                    f.write(f"Data: {doc.data}\n")
                    f.write(f"Conteudo:\n{doc.conteudo}\n")
                    f.write("\n" + "="*50 + "\n\n")
                    
            print(f"Documentos salvos em: {arquivo}")
            
        except Exception as e:
            print(f"Erro ao salvar documentos: {e}")
    
    def obter_estatisticas(self, documentos: List[Documento]) -> Dict[str, Any]:
        """Obtem estatisticas dos documentos coletados"""
        if not documentos:
            return {}
            
        fontes = {}
        total_chars = 0
        
        for doc in documentos:
            fontes[doc.fonte] = fontes.get(doc.fonte, 0) + 1
            total_chars += len(doc.conteudo)
            
        return {
            'total_documentos': len(documentos),
            'distribuicao_fontes': fontes,
            'total_caracteres': total_chars,
            'media_caracteres_por_doc': total_chars // len(documentos) if documentos else 0
        }

def exemplo_uso():
    """Exemplo de uso do coletor"""
    coletor = ColetorBasico()
    
    # Exemplo: coletar sobre inteligencia artificial
    tema = "inteligencia artificial"
    documentos = coletor.coletar_por_tema(tema, max_por_fonte=3)
    
    # Salvar documentos
    coletor.salvar_documentos(documentos, "dados_ia.txt")
    
    # Mostrar estatisticas
    stats = coletor.obter_estatisticas(documentos)
    print("\nEstatisticas:")
    for chave, valor in stats.items():
        print(f"  {chave}: {valor}")

if __name__ == "__main__":
    exemplo_uso()