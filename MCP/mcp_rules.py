#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Rules - Model Context Protocol
Sistema básico MCP usando Python
"""

import random

def live():
    """
    Função LIVE - Retorna número aleatório de 3 dígitos
    
    Returns:
        str: Número aleatório formato 000-999
    """
    # Gera 3 dígitos aleatórios (0-9 cada)
    digit1 = random.randint(0, 9)
    digit2 = random.randint(0, 9)
    digit3 = random.randint(0, 9)
    
    return f"{digit1}{digit2}{digit3}"

def iarules_bkp():
    """
    Função IA_RULES - BACKUP - Retorna as regras da IA do projeto
    
    Returns:
        str: Texto com as regras da IA
    """
    import datetime
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    return f"minhas regras v5 [REFRESH:{timestamp}]"

def iarules():
    """
    Função IA_RULES - Retorna as regras da IA do projeto
    
    Returns:
        str: Texto com as regras da IA
    """
    import sys
    import os
    from pathlib import Path
    
    # Adiciona o caminho do gerenciador de regras ao sys.path
    gerenciador_path = Path(__file__).parent.parent / "FERRAMENTAS" / "GERENCIADOR_REGRAS"
    sys.path.insert(0, str(gerenciador_path))
    
    try:
        from gerenciador_simples import listar_regras
        return listar_regras()
    except ImportError:
        # Fallback caso não consiga importar
        return "Respostas objetivas, máximo 3 parágrafos, sem emojis ou imagens"

def IA_MEDIADOR(prompt_dev: str):
    """Função IA_MEDIADOR - Otimiza prompts do desenvolvedor de forma simples"""
    import sys
    import os
    from pathlib import Path
    from datetime import datetime
    
    try:
        # Registrar início
        registrar_evento('INICIO', {'prompt': prompt_dev})
        
        # Adicionar caminho do AssistentePrompts
        assistente_path = Path(__file__).parent.parent / "FERRAMENTAS" / "ASSISTENTE_PROMPTS"
        sys.path.insert(0, str(assistente_path))
        
        # Usar AssistentePrompts existente
        from assistente_prompts import AssistentePrompts
        assistente = AssistentePrompts()
        
        # Analisar e otimizar
        resultado = assistente.processar_prompt(prompt_dev)
        
        # Verificar clareza (Regra 3)
        if resultado['analise']['score'] < 85:
            return {
                'status': 'erro_clareza',
                'score': resultado['analise']['score'],
                'perguntas': resultado.get('perguntas', []),
                'acao': 'solicitar_mais_informacoes',
                'prompt_original': prompt_dev
            }
        
        # Aplicar regras de pré-processamento
        prompt_otimizado = aplicar_regras_pre(resultado.get('prompt_otimizado', prompt_dev))
        
        # Registrar sucesso
        registrar_evento('COMPLETO', {
            'prompt_original': prompt_dev,
            'prompt_otimizado': prompt_otimizado,
            'score': resultado['analise']['score']
        })
        
        return {
            'status': 'sucesso',
            'prompt_otimizado': prompt_otimizado,
            'score': resultado['analise']['score'],
            'melhorias': resultado.get('sugestao', ''),
            'prompt_original': prompt_dev
        }
        
    except Exception as e:
        return {
            'status': 'erro',
            'erro': str(e),
            'prompt_original': prompt_dev
        }

def aplicar_regras_pre(prompt: str) -> str:
    """Aplica regras de pré-processamento"""
    import sys
    from pathlib import Path
    
    try:
        # Regra 2: Remover emojis
        removedor_path = Path(__file__).parent.parent / "FERRAMENTAS" / "REMOVEDOR_EMOJIS"
        sys.path.insert(0, str(removedor_path))
        
        from removedor_emojis import RemovedorEmojis
        removedor = RemovedorEmojis()
        prompt_limpo = removedor.remover_emojis(prompt)
        
        # Regra 5: Garantir objetividade (máximo 3 parágrafos)
        paragrafos = prompt_limpo.split('\n\n')
        if len(paragrafos) > 3:
            prompt_limpo = '\n\n'.join(paragrafos[:3])
        
        return prompt_limpo
        
    except Exception:
        # Se falhar, retorna prompt original
        return prompt

def get_context(query: str = "", session_id: str = ""):
    """Função GET_CONTEXT - Retorna contexto completo do sistema
    
    Args:
        query (str): Query ou contexto da IA
        session_id (str): ID da sessão atual
        
    Returns:
        dict: Contexto estruturado com regras, histórico e soluções
    """
    import sys
    from pathlib import Path
    from datetime import datetime
    
    try:
        # Inicializar resposta estruturada
        contexto = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'session_id': session_id,
            'regras': [],
            'historico_sessao': [],
            'solucoes_relevantes': [],
            'metadados': {}
        }
        
        # 1. Buscar regras do sistema
        try:
            gerenciador_path = Path(__file__).parent.parent / "FERRAMENTAS" / "GERENCIADOR_REGRAS"
            sys.path.insert(0, str(gerenciador_path))
            from gerenciador_simples import listar_regras
            contexto['regras'] = listar_regras().split('\n')
        except Exception:
            contexto['regras'] = ["Regras não disponíveis"]
        
        # 2. Buscar contexto integrado via IntegradorMCPRAG
        try:
            # Usar IntegradorMCPRAG para busca unificada
            integrador_path = Path(__file__).parent.parent / "FERRAMENTAS" / "RAG"
            sys.path.insert(0, str(integrador_path))
            
            from integrador_mcp import IntegradorMCPRAG
            integrador = IntegradorMCPRAG()
            
            # Buscar contexto unificado
            contexto_integrado = integrador.buscar_contexto_unificado(query, session_id)
            
            # Mesclar resultados
            if 'regras' in contexto_integrado:
                # Manter regras do gerenciador como principal, adicionar do RAG como extra
                contexto['regras_rag'] = contexto_integrado['regras']
            
            if 'historico_sessao' in contexto_integrado:
                contexto['historico_sessao'] = contexto_integrado['historico_sessao']
            
            if 'solucoes_relevantes' in contexto_integrado:
                contexto['solucoes_relevantes'] = contexto_integrado['solucoes_relevantes']
            
            # Adicionar metadados do integrador
            if 'metadados' in contexto_integrado:
                contexto['metadados']['integrador'] = contexto_integrado['metadados']
                
        except Exception as e:
            contexto['metadados']['integrador_error'] = str(e)
            # Fallback para versão simplificada
            if session_id:
                contexto['historico_sessao'] = [{
                    'acao': 'get_context_fallback',
                    'timestamp': datetime.now().isoformat(),
                    'detalhes': {'session_id': session_id, 'erro_integrador': str(e)}
                }]
            
            if query:
                contexto['solucoes_relevantes'] = [{
                    'erro': 'Integrador indisponível para: ' + query,
                    'solucao': 'Usando fallback básico',
                    'score': 0.5
                }]
        
        # 3. Adicionar metadados do sistema
        contexto['metadados'].update({
            'sistema': 'ELIS v2',
            'mcp_version': '1.0',
            'funcoes_disponiveis': ['live', 'iarules', 'IA_MEDIADOR', 'get_context']
        })
        
        return contexto
        
    except Exception as e:
        return {
            'status': 'erro',
            'erro': str(e),
            'timestamp': datetime.now().isoformat()
        }

def registrar_evento(tipo: str, dados: dict):
    """Registra eventos simples (versão simplificada)"""
    from datetime import datetime
    
    # Por enquanto, apenas log simples
    # RAG será integrado na próxima fase
    try:
        timestamp = datetime.now().isoformat()
        # Log básico para debug (opcional)
        # print(f"[{timestamp}] Evento {tipo}: {dados}")
        pass
    except Exception:
        # Não falhar nunca
        pass