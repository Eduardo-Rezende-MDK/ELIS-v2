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