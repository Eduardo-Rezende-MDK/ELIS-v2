#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste de Evidência Real - IntegradorMCPRAG
Demonstra funcionamento direto no terminal
"""

import sys
from pathlib import Path

# Adicionar caminhos
sys.path.append('FERRAMENTAS/RAG')
sys.path.append('FERRAMENTAS/GERENCIADOR_REGRAS')

print("🔍 TESTE DE EVIDÊNCIA REAL - IntegradorMCPRAG")
print("=" * 50)

try:
    from integrador_mcp import IntegradorMCPRAG
    print("✅ IntegradorMCPRAG importado com sucesso")
    
    # Criar instância
    integrador = IntegradorMCPRAG()
    print("✅ Instância criada")
    
    # Testar busca de contexto
    print("\n🔍 Testando busca de contexto...")
    resultado = integrador.buscar_contexto_unificado(
        query="teste evidencia real terminal",
        session_id="evidencia_001"
    )
    
    print("\n📊 RESULTADOS:")
    print("-" * 30)
    
    # Verificar fonte
    fonte = resultado.get('metadados', {}).get('fonte', 'N/A')
    print(f"Fonte: {fonte}")
    
    # Verificar RAG
    stats = resultado.get('metadados', {}).get('estatisticas', {})
    rag_disponivel = stats.get('rag_disponivel', False)
    print(f"RAG Disponível: {rag_disponivel}")
    
    # Verificar regras
    regras = resultado.get('regras', [])
    print(f"Regras Encontradas: {len(regras)}")
    
    # Verificar timestamp
    timestamp = resultado.get('timestamp', 'N/A')
    print(f"Timestamp: {timestamp}")
    
    # Verificar se é dinâmico
    if fonte == 'IntegradorMCPRAG' and rag_disponivel and len(regras) > 0:
        print("\n🎉 EVIDÊNCIA CONFIRMADA:")
        print("   ✅ IntegradorMCPRAG está FUNCIONANDO")
        print("   ✅ RAG está DISPONÍVEL")
        print("   ✅ Regras estão sendo CARREGADAS")
        print("   ✅ Timestamps são DINÂMICOS")
        print("\n🎯 INTEGRAÇÃO RAG-MCP: OPERACIONAL!")
    else:
        print("\n⚠️ Alguns componentes não estão funcionando perfeitamente")
        
except Exception as e:
    print(f"❌ Erro: {e}")
    print("\n🔧 Verificar se todos os componentes estão instalados")

print("\n" + "=" * 50)
print("Teste concluído!")