#!/usr/bin/env python3
"""
Coletor de fontes academicas (ArXiv, Semantic Scholar, PubMed)
"""

import arxiv
import requests
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
from ..models.document import RawDocument

class AcademicSourceCollector:
    """Coletor especializado para fontes academicas"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'RAG-Academic-Collector/1.0'
        })
        
        # Rate limiting
        self.request_delay = self.config.get('request_delay', 1.0)
        self.max_retries = self.config.get('max_retries', 3)
        
    def collect_arxiv(self, query: str, max_results: int = 10) -> List[RawDocument]:
        """Coleta artigos do ArXiv"""
        documents = []
        
        try:
            # Configurar cliente ArXiv
            client = arxiv.Client()
            
            # Criar query de busca
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.Relevance
            )
            
            # Executar busca
            for result in client.results(search):
                try:
                    # Extrair autores
                    authors = [author.name for author in result.authors]
                    
                    # Extrair categorias como keywords
                    keywords = [cat for cat in result.categories]
                    
                    # Criar documento
                    document = RawDocument(
                        title=result.title.strip(),
                        content=result.summary.strip(),
                        source_type='arxiv',
                        url=result.entry_id,
                        authors=authors,
                        publication_date=result.published,
                        abstract=result.summary.strip(),
                        keywords=keywords,
                        language='en',  # ArXiv e principalmente em ingles
                        external_id=result.get_short_id(),
                        source_metadata={
                            'arxiv_id': result.get_short_id(),
                            'categories': result.categories,
                            'primary_category': result.primary_category,
                            'updated': result.updated.isoformat() if result.updated else None,
                            'journal_ref': result.journal_ref,
                            'doi': result.doi,
                            'comment': result.comment
                        }
                    )
                    
                    # Calcular score de qualidade basico
                    document.quality_score = self._calculate_arxiv_quality_score(document)
                    
                    if document.content and len(document.content) > 100:
                        documents.append(document)
                        
                    time.sleep(self.request_delay)
                    
                except Exception as e:
                    print(f"Erro ao processar resultado ArXiv: {e}")
                    continue
                    
        except Exception as e:
            print(f"Erro na busca ArXiv: {e}")
            
        return documents
    
    def collect_semantic_scholar(self, query: str, max_results: int = 10) -> List[RawDocument]:
        """Coleta artigos do Semantic Scholar"""
        documents = []
        
        try:
            # API do Semantic Scholar
            url = "https://api.semanticscholar.org/graph/v1/paper/search"
            
            params = {
                'query': query,
                'limit': max_results,
                'fields': 'paperId,title,abstract,authors,year,url,citationCount,publicationDate,journal,externalIds'
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            for paper in data.get('data', []):
                try:
                    # Extrair autores
                    authors = []
                    if paper.get('authors'):
                        authors = [author.get('name', '') for author in paper['authors']]
                    
                    # Extrair data de publicacao
                    pub_date = None
                    if paper.get('publicationDate'):
                        try:
                            pub_date = datetime.fromisoformat(paper['publicationDate'])
                        except ValueError:
                            pass
                    
                    # Criar documento
                    document = RawDocument(
                        title=paper.get('title', '').strip(),
                        content=paper.get('abstract', '').strip(),
                        source_type='semantic_scholar',
                        url=paper.get('url', ''),
                        authors=authors,
                        publication_date=pub_date,
                        abstract=paper.get('abstract', '').strip(),
                        keywords=[],  # Semantic Scholar nao retorna keywords diretamente
                        language='en',  # Assumir ingles por padrao
                        external_id=paper.get('paperId', ''),
                        source_metadata={
                            'paper_id': paper.get('paperId'),
                            'citation_count': paper.get('citationCount', 0),
                            'year': paper.get('year'),
                            'journal': paper.get('journal', {}).get('name', '') if paper.get('journal') else '',
                            'external_ids': paper.get('externalIds', {})
                        }
                    )
                    
                    # Calcular score de qualidade
                    document.quality_score = self._calculate_semantic_scholar_quality_score(document)
                    
                    if document.content and len(document.content) > 100:
                        documents.append(document)
                        
                    time.sleep(self.request_delay)
                    
                except Exception as e:
                    print(f"Erro ao processar resultado Semantic Scholar: {e}")
                    continue
                    
        except Exception as e:
            print(f"Erro na busca Semantic Scholar: {e}")
            
        return documents
    
    def collect_pubmed(self, query: str, max_results: int = 10) -> List[RawDocument]:
        """Coleta artigos do PubMed (implementacao basica)"""
        documents = []
        
        try:
            # API do PubMed (E-utilities)
            search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            
            search_params = {
                'db': 'pubmed',
                'term': query,
                'retmax': max_results,
                'retmode': 'json'
            }
            
            # Buscar IDs
            search_response = self.session.get(search_url, params=search_params)
            search_response.raise_for_status()
            
            search_data = search_response.json()
            ids = search_data.get('esearchresult', {}).get('idlist', [])
            
            if not ids:
                return documents
            
            # Obter detalhes dos artigos
            fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
            
            fetch_params = {
                'db': 'pubmed',
                'id': ','.join(ids),
                'retmode': 'xml'
            }
            
            fetch_response = self.session.get(fetch_url, params=fetch_params)
            fetch_response.raise_for_status()
            
            # Processar XML (implementacao simplificada)
            # Para uma implementacao completa, seria necessario usar BeautifulSoup ou xml.etree
            print(f"PubMed: Encontrados {len(ids)} artigos (processamento XML nao implementado)")
            
        except Exception as e:
            print(f"Erro na busca PubMed: {e}")
            
        return documents
    
    def collect_all_sources(self, query: str, max_per_source: int = 5) -> List[RawDocument]:
        """Coleta de todas as fontes academicas"""
        all_documents = []
        
        print(f"Coletando fontes academicas para: {query}")
        
        # ArXiv
        print("Coletando do ArXiv...")
        arxiv_docs = self.collect_arxiv(query, max_per_source)
        all_documents.extend(arxiv_docs)
        print(f"ArXiv: {len(arxiv_docs)} documentos")
        
        # Semantic Scholar
        print("Coletando do Semantic Scholar...")
        ss_docs = self.collect_semantic_scholar(query, max_per_source)
        all_documents.extend(ss_docs)
        print(f"Semantic Scholar: {len(ss_docs)} documentos")
        
        # PubMed (desabilitado por enquanto)
        # print("Coletando do PubMed...")
        # pubmed_docs = self.collect_pubmed(query, max_per_source)
        # all_documents.extend(pubmed_docs)
        # print(f"PubMed: {len(pubmed_docs)} documentos")
        
        print(f"Total academico: {len(all_documents)} documentos")
        
        return all_documents
    
    def _calculate_arxiv_quality_score(self, document: RawDocument) -> float:
        """Calcula score de qualidade para documentos do ArXiv"""
        score = 0.5  # Score base
        
        # Tamanho do abstract
        if len(document.content) > 500:
            score += 0.2
        elif len(document.content) > 200:
            score += 0.1
            
        # Numero de autores
        if len(document.authors) > 1:
            score += 0.1
            
        # Presenca de DOI
        if document.source_metadata.get('doi'):
            score += 0.1
            
        # Categoria principal (algumas sao mais relevantes)
        primary_cat = document.source_metadata.get('primary_category', '')
        if any(cat in primary_cat for cat in ['cs.AI', 'cs.CL', 'cs.LG', 'stat.ML']):
            score += 0.1
            
        return min(score, 1.0)
    
    def _calculate_semantic_scholar_quality_score(self, document: RawDocument) -> float:
        """Calcula score de qualidade para documentos do Semantic Scholar"""
        score = 0.5  # Score base
        
        # Numero de citacoes
        citations = document.source_metadata.get('citation_count', 0)
        if citations > 100:
            score += 0.3
        elif citations > 10:
            score += 0.2
        elif citations > 0:
            score += 0.1
            
        # Presenca de journal
        if document.source_metadata.get('journal'):
            score += 0.1
            
        # Tamanho do abstract
        if len(document.content) > 300:
            score += 0.1
            
        return min(score, 1.0)
    
    def get_source_statistics(self, documents: List[RawDocument]) -> Dict[str, Any]:
        """Obtem estatisticas dos documentos coletados"""
        if not documents:
            return {}
            
        stats = {
            'total_documents': len(documents),
            'by_source': {},
            'by_language': {},
            'avg_quality_score': 0.0,
            'avg_content_length': 0.0,
            'total_authors': 0
        }
        
        total_quality = 0.0
        total_length = 0
        total_authors = 0
        
        for doc in documents:
            # Por fonte
            stats['by_source'][doc.source_type] = stats['by_source'].get(doc.source_type, 0) + 1
            
            # Por idioma
            stats['by_language'][doc.language] = stats['by_language'].get(doc.language, 0) + 1
            
            # Metricas
            total_quality += doc.quality_score
            total_length += len(doc.content)
            total_authors += len(doc.authors)
        
        stats['avg_quality_score'] = total_quality / len(documents)
        stats['avg_content_length'] = total_length / len(documents)
        stats['avg_authors_per_doc'] = total_authors / len(documents)
        
        return stats