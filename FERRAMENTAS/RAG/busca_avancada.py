#!/usr/bin/env python3
"""
Módulo de Busca Avançada para Sistema RAG
Fornece funcionalidades de pesquisa sofisticadas além das operações CRUD básicas
"""

import re
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import Counter
import math
from pathlib import Path

class BuscaAvancada:
    """
    Sistema de busca avançada para RAG com múltiplos algoritmos e filtros
    """
    
    def __init__(self, rag_manager):
        self.rag_manager = rag_manager
        self.stop_words = {
            'pt': {'a', 'o', 'e', 'de', 'do', 'da', 'em', 'um', 'uma', 'para', 'com', 'por', 'que', 'se', 'na', 'no', 'os', 'as', 'dos', 'das', 'ao', 'à', 'pelo', 'pela', 'pelos', 'pelas', 'este', 'esta', 'estes', 'estas', 'esse', 'essa', 'esses', 'essas', 'aquele', 'aquela', 'aqueles', 'aquelas', 'seu', 'sua', 'seus', 'suas', 'meu', 'minha', 'meus', 'minhas', 'nosso', 'nossa', 'nossos', 'nossas', 'vosso', 'vossa', 'vossos', 'vossas', 'dele', 'dela', 'deles', 'delas', 'mais', 'menos', 'muito', 'muita', 'muitos', 'muitas', 'pouco', 'pouca', 'poucos', 'poucas', 'todo', 'toda', 'todos', 'todas', 'outro', 'outra', 'outros', 'outras', 'mesmo', 'mesma', 'mesmos', 'mesmas', 'também', 'ainda', 'já', 'só', 'apenas', 'mas', 'porém', 'contudo', 'entretanto', 'todavia', 'quando', 'onde', 'como', 'porque', 'então', 'assim', 'bem', 'mal', 'sim', 'não', 'nem', 'ou', 'seja', 'estar', 'ser', 'ter', 'haver', 'fazer', 'dizer', 'dar', 'ir', 'ver', 'saber', 'poder', 'querer', 'ficar', 'vir', 'chegar', 'passar', 'levar', 'trazer', 'colocar', 'pôr', 'tirar', 'encontrar', 'achar', 'pensar', 'acreditar', 'sentir', 'ouvir', 'falar', 'contar', 'mostrar', 'seguir', 'começar', 'acabar', 'continuar', 'parar', 'deixar', 'ficar', 'tornar', 'voltar', 'sair', 'entrar', 'subir', 'descer', 'abrir', 'fechar', 'ganhar', 'perder', 'vender', 'comprar', 'pagar', 'custar', 'valer', 'servir', 'usar', 'precisar', 'gostar', 'amar', 'odiar', 'preferir', 'escolher', 'decidir', 'tentar', 'conseguir', 'permitir', 'proibir', 'mandar', 'pedir', 'perguntar', 'responder', 'explicar', 'ensinar', 'aprender', 'estudar', 'trabalhar', 'jogar', 'brincar', 'correr', 'andar', 'caminhar', 'voar', 'nadar', 'dormir', 'acordar', 'comer', 'beber', 'cozinhar', 'lavar', 'limpar', 'vestir', 'calçar', 'sentar', 'levantar', 'deitar', 'morrer', 'nascer', 'crescer', 'viver', 'morar', 'habitar', 'existir', 'acontecer', 'ocorrer', 'realizar', 'criar', 'construir', 'destruir', 'quebrar', 'consertar', 'arrumar', 'organizar', 'preparar', 'terminar', 'completar', 'iniciar', 'receber', 'enviar', 'mandar', 'chamar', 'gritar', 'sussurrar', 'cantar', 'dançar', 'rir', 'chorar', 'sorrir', 'beijar', 'abraçar', 'tocar', 'pegar', 'soltar', 'segurar', 'empurrar', 'puxar', 'carregar', 'levantar', 'baixar', 'subir', 'descer', 'entrar', 'sair', 'chegar', 'partir', 'voltar', 'retornar', 'ir', 'vir', 'ficar', 'permanecer', 'continuar', 'parar', 'cessar', 'terminar', 'acabar', 'começar', 'iniciar', 'principiar'}
        }
    
    def busca_fuzzy(self, termo: str, campo: str = 'titulo', limite: int = 10, tolerancia: int = 2) -> List[Dict[str, Any]]:
        """
        Busca com tolerância a erros de digitação (fuzzy search)
        
        Args:
            termo: Termo de busca
            campo: Campo para buscar
            limite: Número máximo de resultados
            tolerancia: Número máximo de caracteres diferentes permitidos
            
        Returns:
            Lista de documentos encontrados com score de similaridade
        """
        resultados = []
        metadata = self.rag_manager.file_store._load_metadata()
        
        for doc_id in metadata["document_index"]:
            doc = self.rag_manager.ler_documento(doc_id)
            if not doc:
                continue
            
            # Obter texto do campo
            texto_campo = ""
            if campo == 'titulo':
                texto_campo = doc.title
            elif campo == 'conteudo':
                texto_campo = doc.content
            elif campo == 'fonte':
                texto_campo = doc.source_type
            elif campo == 'autor':
                texto_campo = ' '.join(doc.authors)
            
            # Calcular distância de Levenshtein
            palavras = texto_campo.lower().split()
            melhor_score = 0
            
            for palavra in palavras:
                distancia = self._levenshtein_distance(termo.lower(), palavra)
                if distancia <= tolerancia:
                    score = 1 - (distancia / max(len(termo), len(palavra)))
                    melhor_score = max(melhor_score, score)
            
            if melhor_score > 0:
                resultados.append({
                    'id': doc.document_id,
                    'titulo': doc.title,
                    'fonte': doc.source_type,
                    'preview': doc.content[:200] + '...' if len(doc.content) > 200 else doc.content,
                    'score': melhor_score,
                    'url': doc.url,
                    'tipo_busca': 'fuzzy'
                })
        
        # Ordenar por score e limitar
        resultados.sort(key=lambda x: x['score'], reverse=True)
        return resultados[:limite]
    
    def busca_por_palavras_chave(self, palavras: List[str], operador: str = 'AND', limite: int = 10) -> List[Dict[str, Any]]:
        """
        Busca usando múltiplas palavras-chave com operadores lógicos
        
        Args:
            palavras: Lista de palavras-chave
            operador: 'AND', 'OR' ou 'NOT'
            limite: Número máximo de resultados
            
        Returns:
            Lista de documentos encontrados
        """
        resultados = []
        metadata = self.rag_manager.file_store._load_metadata()
        
        # Remover stop words
        palavras_filtradas = [p.lower() for p in palavras if p.lower() not in self.stop_words['pt']]
        
        for doc_id in metadata["document_index"]:
            doc = self.rag_manager.ler_documento(doc_id)
            if not doc:
                continue
            
            texto_completo = f"{doc.title} {doc.content} {doc.abstract}".lower()
            
            # Verificar presença das palavras
            palavras_encontradas = []
            for palavra in palavras_filtradas:
                if palavra in texto_completo:
                    palavras_encontradas.append(palavra)
            
            # Aplicar operador lógico
            incluir = False
            if operador == 'AND':
                incluir = len(palavras_encontradas) == len(palavras_filtradas)
            elif operador == 'OR':
                incluir = len(palavras_encontradas) > 0
            elif operador == 'NOT':
                incluir = len(palavras_encontradas) == 0
            
            if incluir:
                # Calcular score baseado na frequência das palavras
                score = len(palavras_encontradas) / len(palavras_filtradas) if palavras_filtradas else 0
                
                resultados.append({
                    'id': doc.document_id,
                    'titulo': doc.title,
                    'fonte': doc.source_type,
                    'preview': doc.content[:200] + '...' if len(doc.content) > 200 else doc.content,
                    'score': score,
                    'palavras_encontradas': palavras_encontradas,
                    'url': doc.url,
                    'tipo_busca': f'palavras_chave_{operador}'
                })
        
        # Ordenar por score
        resultados.sort(key=lambda x: x['score'], reverse=True)
        return resultados[:limite]
    
    def busca_por_data(self, data_inicio: Optional[datetime] = None, data_fim: Optional[datetime] = None, limite: int = 10) -> List[Dict[str, Any]]:
        """
        Busca documentos por intervalo de datas
        
        Args:
            data_inicio: Data de início (opcional)
            data_fim: Data de fim (opcional)
            limite: Número máximo de resultados
            
        Returns:
            Lista de documentos no intervalo de datas
        """
        resultados = []
        metadata = self.rag_manager.file_store._load_metadata()
        
        for doc_id in metadata["document_index"]:
            doc = self.rag_manager.ler_documento(doc_id)
            if not doc or not doc.collection_timestamp:
                continue
            
            data_doc = doc.collection_timestamp
            
            # Verificar se está no intervalo
            incluir = True
            if data_inicio and data_doc < data_inicio:
                incluir = False
            if data_fim and data_doc > data_fim:
                incluir = False
            
            if incluir:
                resultados.append({
                    'id': doc.document_id,
                    'titulo': doc.title,
                    'fonte': doc.source_type,
                    'data_coleta': data_doc.isoformat(),
                    'preview': doc.content[:200] + '...' if len(doc.content) > 200 else doc.content,
                    'url': doc.url,
                    'tipo_busca': 'por_data'
                })
        
        # Ordenar por data (mais recente primeiro)
        resultados.sort(key=lambda x: x['data_coleta'], reverse=True)
        return resultados[:limite]
    
    def busca_por_tamanho(self, tamanho_min: int = 0, tamanho_max: Optional[int] = None, limite: int = 10) -> List[Dict[str, Any]]:
        """
        Busca documentos por tamanho do conteúdo
        
        Args:
            tamanho_min: Tamanho mínimo em caracteres
            tamanho_max: Tamanho máximo em caracteres (opcional)
            limite: Número máximo de resultados
            
        Returns:
            Lista de documentos no intervalo de tamanho
        """
        resultados = []
        metadata = self.rag_manager.file_store._load_metadata()
        
        for doc_id in metadata["document_index"]:
            doc = self.rag_manager.ler_documento(doc_id)
            if not doc:
                continue
            
            tamanho = len(doc.content)
            
            # Verificar se está no intervalo
            incluir = tamanho >= tamanho_min
            if tamanho_max and tamanho > tamanho_max:
                incluir = False
            
            if incluir:
                resultados.append({
                    'id': doc.document_id,
                    'titulo': doc.title,
                    'fonte': doc.source_type,
                    'tamanho': tamanho,
                    'preview': doc.content[:200] + '...' if len(doc.content) > 200 else doc.content,
                    'url': doc.url,
                    'tipo_busca': 'por_tamanho'
                })
        
        # Ordenar por tamanho (maior primeiro)
        resultados.sort(key=lambda x: x['tamanho'], reverse=True)
        return resultados[:limite]
    
    def busca_combinada(self, filtros: Dict[str, Any], limite: int = 10) -> List[Dict[str, Any]]:
        """
        Busca combinando múltiplos filtros
        
        Args:
            filtros: Dicionário com filtros a aplicar
                - termo: termo de busca textual
                - fonte: lista de fontes permitidas
                - data_inicio/data_fim: intervalo de datas
                - tamanho_min/tamanho_max: intervalo de tamanho
                - palavras_chave: lista de palavras obrigatórias
            limite: Número máximo de resultados
            
        Returns:
            Lista de documentos que atendem todos os filtros
        """
        resultados = []
        metadata = self.rag_manager.file_store._load_metadata()
        
        for doc_id in metadata["document_index"]:
            doc = self.rag_manager.ler_documento(doc_id)
            if not doc:
                continue
            
            # Aplicar todos os filtros
            incluir = True
            score = 1.0
            
            # Filtro por termo
            if 'termo' in filtros and filtros['termo']:
                termo = filtros['termo'].lower()
                texto_completo = f"{doc.title} {doc.content}".lower()
                if termo not in texto_completo:
                    incluir = False
                else:
                    # Calcular score baseado na frequência
                    freq = texto_completo.count(termo)
                    score *= min(1.0, freq / 10)  # Normalizar frequência
            
            # Filtro por fonte
            if 'fontes' in filtros and filtros['fontes']:
                if doc.source_type not in filtros['fontes']:
                    incluir = False
            
            # Filtro por data
            if incluir and doc.collection_timestamp:
                if 'data_inicio' in filtros and filtros['data_inicio']:
                    if doc.collection_timestamp < filtros['data_inicio']:
                        incluir = False
                if 'data_fim' in filtros and filtros['data_fim']:
                    if doc.collection_timestamp > filtros['data_fim']:
                        incluir = False
            
            # Filtro por tamanho
            if incluir:
                tamanho = len(doc.content)
                if 'tamanho_min' in filtros and tamanho < filtros['tamanho_min']:
                    incluir = False
                if 'tamanho_max' in filtros and filtros['tamanho_max'] and tamanho > filtros['tamanho_max']:
                    incluir = False
            
            # Filtro por palavras-chave
            if incluir and 'palavras_chave' in filtros and filtros['palavras_chave']:
                texto_completo = f"{doc.title} {doc.content}".lower()
                palavras_encontradas = 0
                for palavra in filtros['palavras_chave']:
                    if palavra.lower() in texto_completo:
                        palavras_encontradas += 1
                
                if palavras_encontradas < len(filtros['palavras_chave']):
                    incluir = False
                else:
                    score *= palavras_encontradas / len(filtros['palavras_chave'])
            
            if incluir:
                resultados.append({
                    'id': doc.document_id,
                    'titulo': doc.title,
                    'fonte': doc.source_type,
                    'tamanho': len(doc.content),
                    'data_coleta': doc.collection_timestamp.isoformat() if doc.collection_timestamp else None,
                    'preview': doc.content[:200] + '...' if len(doc.content) > 200 else doc.content,
                    'score': score,
                    'url': doc.url,
                    'tipo_busca': 'combinada'
                })
        
        # Ordenar por score
        resultados.sort(key=lambda x: x['score'], reverse=True)
        return resultados[:limite]
    
    def busca_similar_por_conteudo(self, doc_id: str, limite: int = 5) -> List[Dict[str, Any]]:
        """
        Encontra documentos similares baseado no conteúdo
        
        Args:
            doc_id: ID do documento de referência
            limite: Número máximo de resultados
            
        Returns:
            Lista de documentos similares
        """
        doc_referencia = self.rag_manager.ler_documento(doc_id)
        if not doc_referencia:
            return []
        
        # Extrair palavras-chave do documento de referência
        palavras_ref = self._extrair_palavras_chave(doc_referencia.content)
        
        resultados = []
        metadata = self.rag_manager.file_store._load_metadata()
        
        for outro_doc_id in metadata["document_index"]:
            if outro_doc_id == doc_id:  # Pular o próprio documento
                continue
                
            doc = self.rag_manager.ler_documento(outro_doc_id)
            if not doc:
                continue
            
            # Extrair palavras-chave do documento atual
            palavras_doc = self._extrair_palavras_chave(doc.content)
            
            # Calcular similaridade usando Jaccard
            similaridade = self._jaccard_similarity(palavras_ref, palavras_doc)
            
            if similaridade > 0.1:  # Threshold mínimo
                resultados.append({
                    'id': doc.document_id,
                    'titulo': doc.title,
                    'fonte': doc.source_type,
                    'similaridade': similaridade,
                    'preview': doc.content[:200] + '...' if len(doc.content) > 200 else doc.content,
                    'url': doc.url,
                    'tipo_busca': 'similar_conteudo'
                })
        
        # Ordenar por similaridade
        resultados.sort(key=lambda x: x['similaridade'], reverse=True)
        return resultados[:limite]
    
    def estatisticas_busca(self) -> Dict[str, Any]:
        """
        Gera estatísticas úteis para buscas
        
        Returns:
            Dicionário com estatísticas do corpus
        """
        metadata = self.rag_manager.file_store._load_metadata()
        
        # Contadores
        fontes = Counter()
        tamanhos = []
        palavras_mais_comuns = Counter()
        total_docs = 0
        
        for doc_id in metadata["document_index"]:
            doc = self.rag_manager.ler_documento(doc_id)
            if not doc:
                continue
            
            total_docs += 1
            fontes[doc.source_type] += 1
            tamanhos.append(len(doc.content))
            
            # Extrair palavras para estatísticas
            palavras = self._extrair_palavras_chave(doc.content, limite=None)
            palavras_mais_comuns.update(palavras)
        
        # Calcular estatísticas
        tamanho_medio = sum(tamanhos) / len(tamanhos) if tamanhos else 0
        tamanho_min = min(tamanhos) if tamanhos else 0
        tamanho_max = max(tamanhos) if tamanhos else 0
        
        return {
            'total_documentos': total_docs,
            'fontes_disponiveis': dict(fontes),
            'tamanho_medio_caracteres': int(tamanho_medio),
            'tamanho_min_caracteres': tamanho_min,
            'tamanho_max_caracteres': tamanho_max,
            'palavras_mais_comuns': dict(palavras_mais_comuns.most_common(20)),
            'total_palavras_unicas': len(palavras_mais_comuns)
        }
    
    # ===== MÉTODOS AUXILIARES =====
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """
        Calcula distância de Levenshtein entre duas strings
        """
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def _extrair_palavras_chave(self, texto: str, limite: Optional[int] = 50) -> List[str]:
        """
        Extrai palavras-chave relevantes de um texto
        """
        # Limpar e normalizar texto
        texto_limpo = re.sub(r'[^\w\s]', ' ', texto.lower())
        palavras = texto_limpo.split()
        
        # Remover stop words e palavras muito curtas
        palavras_filtradas = [
            palavra for palavra in palavras 
            if len(palavra) > 2 and palavra not in self.stop_words['pt']
        ]
        
        # Contar frequências
        contador = Counter(palavras_filtradas)
        
        # Retornar palavras mais comuns
        if limite:
            return [palavra for palavra, _ in contador.most_common(limite)]
        else:
            return list(contador.keys())
    
    def _jaccard_similarity(self, set1: List[str], set2: List[str]) -> float:
        """
        Calcula similaridade de Jaccard entre duas listas de palavras
        """
        s1 = set(set1)
        s2 = set(set2)
        
        if not s1 and not s2:
            return 1.0
        
        intersecao = len(s1.intersection(s2))
        uniao = len(s1.union(s2))
        
        return intersecao / uniao if uniao > 0 else 0.0