#!/usr/bin/env python3
"""
Coletor de fontes web (Wikipedia, sites institucionais)
"""

import requests
from bs4 import BeautifulSoup
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.document import RawDocument

class WebSourceCollector:
    """Coletor especializado para fontes web"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'RAG-Web-Collector/1.0 (Educational Purpose)'
        })
        
        # Rate limiting
        self.request_delay = self.config.get('request_delay', 1.0)
        self.max_retries = self.config.get('max_retries', 3)
        
        # Configuracoes da Wikipedia
        self.wikipedia_languages = self.config.get('wikipedia_languages', ['pt', 'en'])
        
    def collect_wikipedia(self, query: str, max_results: int = 10, language: str = 'pt') -> List[RawDocument]:
        """Coleta artigos da Wikipedia"""
        documents = []
        
        try:
            # Buscar artigos relacionados na Wikipedia
            search_url = f"https://{language}.wikipedia.org/w/api.php"
            search_params = {
                'action': 'query',
                'format': 'json',
                'list': 'search',
                'srsearch': query,
                'srlimit': max_results
            }
            
            response = self.session.get(search_url, params=search_params)
            response.raise_for_status()
            
            search_results = response.json()
            
            for item in search_results.get('query', {}).get('search', []):
                try:
                    title = item.get('title', '')
                    
                    # Obter conteudo do artigo usando API de extratos
                    content_params = {
                        'action': 'query',
                        'format': 'json',
                        'prop': 'extracts|info',
                        'titles': title,
                        'exintro': False,  # Pegar artigo completo
                        'explaintext': True,
                        'exsectionformat': 'plain',
                        'inprop': 'url'
                    }
                    
                    content_response = self.session.get(search_url, params=content_params)
                    content_response.raise_for_status()
                    
                    content_data = content_response.json()
                    pages = content_data.get('query', {}).get('pages', {})
                    
                    # Pegar a primeira pagina (unica)
                    page_data = next(iter(pages.values()), {})
                    content = page_data.get('extract', '')
                    page_url = page_data.get('fullurl', '')
                    
                    if not content or len(content) < 100:
                        continue
                    
                    # Extrair snippet da busca como abstract
                    snippet = item.get('snippet', '').replace('<span class="searchmatch">', '').replace('</span>', '')
                    
                    # Criar documento
                    document = RawDocument(
                        title=title,
                        content=content,
                        source_type='wikipedia',
                        url=page_url or f"https://{language}.wikipedia.org/wiki/{title.replace(' ', '_')}",
                        authors=[],  # Wikipedia nao tem autores especificos
                        publication_date=None,
                        abstract=snippet,
                        keywords=self._extract_wikipedia_keywords(content),
                        language=language,
                        external_id=str(page_data.get('pageid', '')),
                        source_metadata={
                            'wikipedia_language': language,
                            'page_id': page_data.get('pageid'),
                            'search_snippet': snippet,
                            'word_count': item.get('wordcount', 0),
                            'size': item.get('size', 0),
                            'timestamp': item.get('timestamp', '')
                        }
                    )
                    
                    # Calcular score de qualidade
                    document.quality_score = self._calculate_wikipedia_quality_score(document)
                    
                    documents.append(document)
                    time.sleep(self.request_delay)
                    
                except Exception as e:
                    print(f"Erro ao processar artigo Wikipedia '{title}': {e}")
                    continue
                    
        except Exception as e:
            print(f"Erro na busca Wikipedia ({language}): {e}")
            
        return documents
    
    def collect_institutional_sites(self, query: str, domains: List[str], max_per_domain: int = 3) -> List[RawDocument]:
        """Coleta de sites institucionais brasileiros"""
        documents = []
        
        # Dominios institucionais brasileiros
        default_domains = [
            'usp.br',
            'unicamp.br', 
            'unesp.br',
            'ufmg.br',
            'ufrj.br',
            'unb.br',
            'ufsc.br',
            'puc-rio.br'
        ]
        
        search_domains = domains or default_domains
        
        for domain in search_domains:
            try:
                # Usar Google Search API ou DuckDuckGo para buscar no dominio
                # Por simplicidade, vamos simular a busca
                print(f"Buscando em {domain} (funcionalidade limitada)")
                
                # Aqui seria implementada a busca real nos sites
                # Por enquanto, retornamos lista vazia
                
                time.sleep(self.request_delay)
                
            except Exception as e:
                print(f"Erro ao buscar em {domain}: {e}")
                continue
                
        return documents
    
    def collect_news_sites(self, query: str, max_results: int = 5) -> List[RawDocument]:
        """Coleta de sites de noticias (implementacao basica)"""
        documents = []
        
        # Sites de noticias brasileiros
        news_sites = [
            'g1.globo.com',
            'folha.uol.com.br',
            'estadao.com.br',
            'bbc.com/portuguese'
        ]
        
        print(f"Coleta de noticias nao implementada completamente")
        
        return documents
    
    def collect_all_web_sources(self, query: str, max_per_source: int = 5) -> List[RawDocument]:
        """Coleta de todas as fontes web"""
        all_documents = []
        
        print(f"Coletando fontes web para: {query}")
        
        # Wikipedia em portugues
        print("Coletando da Wikipedia (PT)...")
        wiki_pt_docs = self.collect_wikipedia(query, max_per_source, 'pt')
        all_documents.extend(wiki_pt_docs)
        print(f"Wikipedia PT: {len(wiki_pt_docs)} documentos")
        
        # Wikipedia em ingles (se configurado)
        if 'en' in self.wikipedia_languages and max_per_source > 0:
            print("Coletando da Wikipedia (EN)...")
            wiki_en_docs = self.collect_wikipedia(query, max_per_source // 2, 'en')
            all_documents.extend(wiki_en_docs)
            print(f"Wikipedia EN: {len(wiki_en_docs)} documentos")
        
        # Sites institucionais (desabilitado por enquanto)
        # print("Coletando de sites institucionais...")
        # inst_docs = self.collect_institutional_sites(query, [], max_per_source)
        # all_documents.extend(inst_docs)
        # print(f"Sites institucionais: {len(inst_docs)} documentos")
        
        print(f"Total web: {len(all_documents)} documentos")
        
        return all_documents
    
    def _extract_wikipedia_keywords(self, content: str, max_keywords: int = 10) -> List[str]:
        """Extrai palavras-chave do conteudo da Wikipedia"""
        if not content:
            return []
            
        # Implementacao simples: pegar palavras mais frequentes
        words = content.lower().split()
        
        # Filtrar palavras muito comuns
        stop_words = {
            'o', 'a', 'os', 'as', 'um', 'uma', 'de', 'da', 'do', 'das', 'dos',
            'e', 'ou', 'mas', 'por', 'para', 'com', 'em', 'na', 'no', 'nas', 'nos',
            'que', 'se', 'como', 'mais', 'muito', 'sua', 'seu', 'suas', 'seus',
            'foi', 'ser', 'tem', 'ter', 'esta', 'este', 'essa', 'esse', 'isso',
            'the', 'and', 'or', 'but', 'for', 'with', 'in', 'on', 'at', 'to',
            'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had'
        }
        
        # Contar frequencia das palavras
        word_freq = {}
        for word in words:
            word = word.strip('.,!?;:()[]{}"').lower()
            if len(word) > 3 and word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Pegar as mais frequentes
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        keywords = [word for word, freq in sorted_words[:max_keywords]]
        
        return keywords
    
    def _calculate_wikipedia_quality_score(self, document: RawDocument) -> float:
        """Calcula score de qualidade para documentos da Wikipedia"""
        score = 0.6  # Score base (Wikipedia e geralmente confiavel)
        
        # Tamanho do conteudo
        content_length = len(document.content)
        if content_length > 5000:
            score += 0.2
        elif content_length > 2000:
            score += 0.1
        elif content_length < 500:
            score -= 0.2
            
        # Numero de palavras-chave extraidas
        if len(document.keywords) > 5:
            score += 0.1
            
        # Presenca de abstract/snippet
        if document.abstract and len(document.abstract) > 50:
            score += 0.1
            
        # Idioma (preferencia por portugues)
        if document.language == 'pt':
            score += 0.05
            
        return min(score, 1.0)
    
    def get_source_statistics(self, documents: List[RawDocument]) -> Dict[str, Any]:
        """Obtem estatisticas dos documentos web coletados"""
        if not documents:
            return {}
            
        stats = {
            'total_documents': len(documents),
            'by_source': {},
            'by_language': {},
            'avg_quality_score': 0.0,
            'avg_content_length': 0.0,
            'total_keywords': 0
        }
        
        total_quality = 0.0
        total_length = 0
        total_keywords = 0
        
        for doc in documents:
            # Por fonte
            stats['by_source'][doc.source_type] = stats['by_source'].get(doc.source_type, 0) + 1
            
            # Por idioma
            stats['by_language'][doc.language] = stats['by_language'].get(doc.language, 0) + 1
            
            # Metricas
            total_quality += doc.quality_score
            total_length += len(doc.content)
            total_keywords += len(doc.keywords)
        
        stats['avg_quality_score'] = total_quality / len(documents)
        stats['avg_content_length'] = total_length / len(documents)
        stats['avg_keywords_per_doc'] = total_keywords / len(documents)
        
        return stats
    
    def clean_html_content(self, html_content: str) -> str:
        """Limpa conteudo HTML"""
        if not html_content:
            return ""
            
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remover scripts e styles
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extrair texto
            text = soup.get_text()
            
            # Limpar espacos excessivos
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
            
        except Exception as e:
            print(f"Erro ao limpar HTML: {e}")
            return html_content