#!/usr/bin/env python3
"""
Coletor generico para APIs externas
"""

import requests
import time
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
from ..models.document import RawDocument

class APICollector:
    """Coletor generico para APIs externas"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.session = requests.Session()
        
        # Headers padrao
        default_headers = {
            'User-Agent': 'RAG-API-Collector/1.0',
            'Accept': 'application/json'
        }
        
        # Adicionar headers customizados
        custom_headers = self.config.get('headers', {})
        default_headers.update(custom_headers)
        
        self.session.headers.update(default_headers)
        
        # Rate limiting
        self.request_delay = self.config.get('request_delay', 1.0)
        self.max_retries = self.config.get('max_retries', 3)
        
        # APIs configuradas
        self.apis = self.config.get('apis', {})
    
    def collect_from_api(self, api_name: str, query: str, max_results: int = 10) -> List[RawDocument]:
        """Coleta dados de uma API especifica"""
        if api_name not in self.apis:
            print(f"API '{api_name}' nao configurada")
            return []
            
        api_config = self.apis[api_name]
        documents = []
        
        try:
            # Construir URL e parametros
            url = api_config.get('base_url', '')
            params = api_config.get('default_params', {}).copy()
            
            # Adicionar query e limite
            query_param = api_config.get('query_param', 'q')
            limit_param = api_config.get('limit_param', 'limit')
            
            params[query_param] = query
            params[limit_param] = max_results
            
            # Fazer requisicao
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Processar resultados usando parser customizado
            parser_func = api_config.get('parser_function')
            if parser_func and callable(parser_func):
                documents = parser_func(data, api_name)
            else:
                documents = self._default_parser(data, api_name)
                
            time.sleep(self.request_delay)
            
        except Exception as e:
            print(f"Erro ao coletar da API '{api_name}': {e}")
            
        return documents
    
    def collect_from_multiple_apis(self, query: str, api_names: List[str], max_per_api: int = 5) -> List[RawDocument]:
        """Coleta de multiplas APIs"""
        all_documents = []
        
        for api_name in api_names:
            if api_name in self.apis:
                print(f"Coletando da API: {api_name}")
                docs = self.collect_from_api(api_name, query, max_per_api)
                all_documents.extend(docs)
                print(f"{api_name}: {len(docs)} documentos")
            else:
                print(f"API '{api_name}' nao configurada")
                
        return all_documents
    
    def _default_parser(self, data: Dict[str, Any], api_name: str) -> List[RawDocument]:
        """Parser padrao para APIs genericas"""
        documents = []
        
        # Tentar encontrar lista de resultados
        results = []
        
        # Padroes comuns de estrutura de resposta
        if 'results' in data:
            results = data['results']
        elif 'data' in data:
            results = data['data']
        elif 'items' in data:
            results = data['items']
        elif isinstance(data, list):
            results = data
        else:
            print(f"Estrutura de resposta nao reconhecida para API '{api_name}'")
            return documents
            
        for item in results:
            try:
                # Extrair campos comuns
                title = item.get('title', item.get('name', item.get('subject', 'Sem titulo')))
                content = item.get('content', item.get('description', item.get('abstract', item.get('summary', ''))))
                
                if not content:
                    continue
                    
                # Criar documento
                document = RawDocument(
                    title=str(title),
                    content=str(content),
                    source_type=f'api_{api_name}',
                    url=item.get('url', item.get('link', '')),
                    authors=self._extract_authors(item),
                    publication_date=self._extract_date(item),
                    abstract=str(content)[:200] + '...' if len(str(content)) > 200 else str(content),
                    keywords=self._extract_keywords(item),
                    language=item.get('language', 'en'),
                    external_id=str(item.get('id', item.get('identifier', ''))),
                    source_metadata={
                        'api_name': api_name,
                        'raw_data': item
                    }
                )
                
                # Score de qualidade basico
                document.quality_score = self._calculate_api_quality_score(document)
                
                documents.append(document)
                
            except Exception as e:
                print(f"Erro ao processar item da API '{api_name}': {e}")
                continue
                
        return documents
    
    def _extract_authors(self, item: Dict[str, Any]) -> List[str]:
        """Extrai autores do item"""
        authors = []
        
        # Padroes comuns
        if 'authors' in item:
            if isinstance(item['authors'], list):
                authors = [str(author) for author in item['authors']]
            else:
                authors = [str(item['authors'])]
        elif 'author' in item:
            authors = [str(item['author'])]
        elif 'creator' in item:
            authors = [str(item['creator'])]
            
        return authors
    
    def _extract_date(self, item: Dict[str, Any]) -> Optional[datetime]:
        """Extrai data de publicacao do item"""
        date_fields = ['publication_date', 'published', 'date', 'created', 'timestamp']
        
        for field in date_fields:
            if field in item and item[field]:
                try:
                    date_str = str(item[field])
                    # Tentar varios formatos
                    for fmt in ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S']:
                        try:
                            return datetime.strptime(date_str[:len(fmt)], fmt)
                        except ValueError:
                            continue
                except Exception:
                    continue
                    
        return None
    
    def _extract_keywords(self, item: Dict[str, Any]) -> List[str]:
        """Extrai palavras-chave do item"""
        keywords = []
        
        # Padroes comuns
        if 'keywords' in item:
            if isinstance(item['keywords'], list):
                keywords = [str(kw) for kw in item['keywords']]
            else:
                keywords = str(item['keywords']).split(',')
        elif 'tags' in item:
            if isinstance(item['tags'], list):
                keywords = [str(tag) for tag in item['tags']]
            else:
                keywords = str(item['tags']).split(',')
        elif 'categories' in item:
            if isinstance(item['categories'], list):
                keywords = [str(cat) for cat in item['categories']]
                
        # Limpar e limitar
        keywords = [kw.strip() for kw in keywords if kw.strip()]
        return keywords[:10]
    
    def _calculate_api_quality_score(self, document: RawDocument) -> float:
        """Calcula score de qualidade para documentos de API"""
        score = 0.4  # Score base (APIs podem variar em qualidade)
        
        # Tamanho do conteudo
        if len(document.content) > 500:
            score += 0.2
        elif len(document.content) > 200:
            score += 0.1
            
        # Presenca de metadados
        if document.authors:
            score += 0.1
        if document.publication_date:
            score += 0.1
        if document.keywords:
            score += 0.1
        if document.url:
            score += 0.1
            
        return min(score, 1.0)
    
    def add_api_config(self, api_name: str, config: Dict[str, Any]):
        """Adiciona configuracao de uma nova API"""
        required_fields = ['base_url']
        
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Campo obrigatorio '{field}' nao encontrado na configuracao da API '{api_name}'")
                
        self.apis[api_name] = config
    
    def get_configured_apis(self) -> List[str]:
        """Retorna lista de APIs configuradas"""
        return list(self.apis.keys())
    
    def test_api_connection(self, api_name: str) -> bool:
        """Testa conexao com uma API"""
        if api_name not in self.apis:
            return False
            
        try:
            api_config = self.apis[api_name]
            url = api_config.get('base_url')
            
            # Fazer requisicao simples
            response = self.session.get(url, timeout=10)
            return response.status_code == 200
            
        except Exception:
            return False

# Exemplo de configuracao de APIs
EXAMPLE_API_CONFIGS = {
    'newsapi': {
        'base_url': 'https://newsapi.org/v2/everything',
        'default_params': {
            'apiKey': 'YOUR_API_KEY',
            'language': 'pt',
            'sortBy': 'relevancy'
        },
        'query_param': 'q',
        'limit_param': 'pageSize'
    },
    'reddit': {
        'base_url': 'https://www.reddit.com/search.json',
        'default_params': {
            'sort': 'relevance',
            'type': 'link'
        },
        'query_param': 'q',
        'limit_param': 'limit'
    }
}