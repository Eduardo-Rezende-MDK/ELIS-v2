#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integrador MCP-RAG - ELIS v2
Unifica busca de contexto entre MCP e RAG
Conforme RELATORIO_INTEGRACAO_RAG_MCP_REGRAS.md
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Adicionar caminhos necessários
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(str(Path(__file__).parent.parent / "GERENCIADOR_REGRAS"))

class IntegradorMCPRAG:
    """
    Integrador entre MCP e RAG para transmissão unificada de contexto
    
    Responsabilidades:
    - Migrar regras do JSON para RAG
    - Receber requests do MCP
    - Buscar contexto relevante no RAG
    - Combinar dados de múltiplas fontes
    - Formatar resposta estruturada
    """
    
    def __init__(self):
        self.rag = None
        self.gerenciador_regras = None
        self._inicializar_componentes()
    
    def _inicializar_componentes(self):
        """Inicializa componentes RAG e Gerenciador de Regras"""
        try:
            # Inicializar RAG
            from rag_elis import RAGElis
            self.rag = RAGElis()
            
            # Inicializar Gerenciador de Regras
            from gerenciador_simples import GerenciadorRegras
            self.gerenciador_regras = GerenciadorRegras()
            
        except Exception as e:
            print(f"Aviso: Erro ao inicializar componentes: {e}")
    
    def migrar_regras_json_para_rag(self) -> Dict[str, Any]:
        """
        Migra regras do JSON para o RAG
        
        Returns:
            Dict com resultado da migração
        """
        try:
            if not self.gerenciador_regras or not self.rag:
                return {
                    'status': 'erro',
                    'erro': 'Componentes não inicializados'
                }
            
            # Obter regras do JSON
            regras_json = self.gerenciador_regras.regras
            
            migradas = 0
            erros = []
            
            for i, regra in enumerate(regras_json):
                try:
                    if isinstance(regra, dict):
                        # Formato refatorado
                        self.rag.registrar_regra(
                            titulo=regra.get('titulo', f"Regra {i+1}"),
                            descricao=regra.get('descricao', ''),
                            categoria=regra.get('categoria', 'geral'),
                            aplicacao=regra.get('aplicacao', ''),
                            validacao=regra.get('validacao', '')
                        )
                    else:
                        # Formato texto simples
                        self.rag.registrar_regra(
                            titulo=f"Regra {i+1}",
                            descricao=str(regra),
                            categoria='geral',
                            aplicacao='',
                            validacao=''
                        )
                    migradas += 1
                    
                except Exception as e:
                    erros.append(f"Erro na regra {i+1}: {str(e)}")
            
            return {
                'status': 'sucesso',
                'regras_migradas': migradas,
                'erros': erros,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'erro',
                'erro': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def buscar_contexto_unificado(self, query: str = "", session_id: str = "") -> Dict[str, Any]:
        """
        Busca contexto unificado combinando RAG + Regras + Histórico
        
        Args:
            query: Query ou contexto da IA
            session_id: ID da sessão atual
            
        Returns:
            Dict com contexto estruturado
        """
        try:
            contexto = {
                'timestamp': datetime.now().isoformat(),
                'query': query,
                'session_id': session_id,
                'regras': [],
                'historico_sessao': [],
                'solucoes_relevantes': [],
                'metadados': {
                    'fonte': 'IntegradorMCPRAG',
                    'versao': '1.0'
                }
            }
            
            # 1. Buscar regras (prioridade: RAG, fallback: JSON)
            contexto['regras'] = self._buscar_regras(query)
            
            # 2. Buscar histórico da sessão
            if session_id:
                contexto['historico_sessao'] = self._buscar_historico_sessao(session_id)
            
            # 3. Buscar soluções relevantes
            if query:
                contexto['solucoes_relevantes'] = self._buscar_solucoes_relevantes(query)
            
            # 4. Adicionar estatísticas
            contexto['metadados']['estatisticas'] = self._obter_estatisticas()
            
            return contexto
            
        except Exception as e:
            return {
                'status': 'erro',
                'erro': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _buscar_regras(self, query: str = "") -> List[Dict[str, Any]]:
        """Busca regras no RAG ou fallback para JSON"""
        try:
            if self.rag:
                # Tentar buscar no RAG primeiro
                if query:
                    regras_rag = self.rag.buscar_regras(query, limite=10)
                    if regras_rag:
                        return [{
                            'fonte': 'RAG',
                            'titulo': regra.get('titulo', ''),
                            'descricao': regra.get('descricao', ''),
                            'categoria': regra.get('categoria', ''),
                            'score': regra.get('score', 0)
                        } for regra in regras_rag]
            
            # Fallback para JSON
            if self.gerenciador_regras:
                regras_texto = self.gerenciador_regras.listar_regras()
                return [{
                    'fonte': 'JSON',
                    'conteudo': regras_texto,
                    'timestamp': datetime.now().isoformat()
                }]
            
            return [{'erro': 'Nenhuma fonte de regras disponível'}]
            
        except Exception as e:
            return [{'erro': f'Erro ao buscar regras: {str(e)}'}]
    
    def _buscar_historico_sessao(self, session_id: str) -> List[Dict[str, Any]]:
        """Busca histórico da sessão no RAG"""
        try:
            if not self.rag:
                return [{'erro': 'RAG não disponível'}]
            
            historico = self.rag.buscar_historico_sessao(session_id, limite=5)
            
            return [{
                'acao': item.get('acao', ''),
                'timestamp': item.get('timestamp', ''),
                'detalhes': item.get('detalhes', {}),
                'score': item.get('score', 0)
            } for item in historico]
            
        except Exception as e:
            return [{'erro': f'Erro ao buscar histórico: {str(e)}'}]
    
    def _buscar_solucoes_relevantes(self, query: str) -> List[Dict[str, Any]]:
        """Busca soluções relevantes no RAG"""
        try:
            if not self.rag:
                return [{'erro': 'RAG não disponível'}]
            
            solucoes = self.rag.buscar_solucoes(query, limite=3)
            
            return [{
                'erro': item.get('erro', ''),
                'solucao': item.get('solucao', ''),
                'contexto': item.get('contexto', {}),
                'score': item.get('score', 0)
            } for item in solucoes]
            
        except Exception as e:
            return [{'erro': f'Erro ao buscar soluções: {str(e)}'}]
    
    def _obter_estatisticas(self) -> Dict[str, Any]:
        """Obtém estatísticas dos componentes"""
        try:
            stats = {
                'rag_disponivel': self.rag is not None,
                'gerenciador_disponivel': self.gerenciador_regras is not None
            }
            
            if self.rag:
                try:
                    stats_rag = self.rag.obter_estatisticas()
                    stats['rag_stats'] = stats_rag
                except:
                    stats['rag_stats'] = {'erro': 'Não foi possível obter estatísticas'}
            
            return stats
            
        except Exception as e:
            return {'erro': f'Erro ao obter estatísticas: {str(e)}'}
    
    def sincronizar_regras(self) -> Dict[str, Any]:
        """
        Sincroniza regras entre JSON e RAG (bidirecional)
        
        Returns:
            Dict com resultado da sincronização
        """
        try:
            # Primeiro, migrar do JSON para RAG
            resultado_migracao = self.migrar_regras_json_para_rag()
            
            # TODO: Implementar sincronização reversa (RAG -> JSON) se necessário
            
            return {
                'status': 'sucesso',
                'migracao_json_rag': resultado_migracao,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'erro',
                'erro': str(e),
                'timestamp': datetime.now().isoformat()
            }

# Função de conveniência para uso direto
def obter_contexto_integrado(query: str = "", session_id: str = "") -> Dict[str, Any]:
    """
    Função de conveniência para obter contexto integrado
    
    Args:
        query: Query ou contexto da IA
        session_id: ID da sessão atual
        
    Returns:
        Dict com contexto estruturado
    """
    integrador = IntegradorMCPRAG()
    return integrador.buscar_contexto_unificado(query, session_id)

if __name__ == "__main__":
    # Teste básico
    print("🔧 Testando IntegradorMCPRAG...")
    
    integrador = IntegradorMCPRAG()
    
    # Teste de migração
    print("\n📋 Testando migração de regras...")
    resultado_migracao = integrador.migrar_regras_json_para_rag()
    print(json.dumps(resultado_migracao, indent=2, ensure_ascii=False))
    
    # Teste de busca de contexto
    print("\n🔍 Testando busca de contexto...")
    contexto = integrador.buscar_contexto_unificado(
        query="erro de importação Python",
        session_id="teste_001"
    )
    print(json.dumps(contexto, indent=2, ensure_ascii=False))
    
    print("\n✅ Teste concluído!")