#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste das Funções MCP - ELIS v2
Script para verificar quais funções estão disponíveis no servidor MCP
"""

import json
import subprocess
import sys
from pathlib import Path

def test_mcp_server():
    """Testa o servidor MCP e lista as funções disponíveis"""
    print("🔍 TESTANDO SERVIDOR MCP - ELIS v2")
    print("=" * 40)
    
    # Importa as funções diretamente
    try:
        from mcp_rules import live, iarules
        print("✅ Importação das funções: OK")
        print(f"📋 Função live: {live.__doc__.strip() if live.__doc__ else 'Sem documentação'}")
        print(f"📋 Função iarules: {iarules.__doc__.strip() if iarules.__doc__ else 'Sem documentação'}")
        
        # Testa as funções
        print("\n🧪 TESTANDO FUNÇÕES:")
        print("-" * 20)
        
        # Teste live
        try:
            result_live = live()
            print(f"✅ live(): {result_live}")
        except Exception as e:
            print(f"❌ live(): Erro - {e}")
        
        # Teste iarules
        try:
            result_iarules = iarules()
            print(f"✅ iarules(): {result_iarules}")
        except Exception as e:
            print(f"❌ iarules(): Erro - {e}")
            
    except ImportError as e:
        print(f"❌ Erro na importação: {e}")
    
    # Verifica o servidor MCP
    print("\n🖥️ VERIFICANDO SERVIDOR MCP:")
    print("-" * 30)
    
    try:
        from mcp_server_stdio import MCPServer
        server = MCPServer()
        print(f"✅ Servidor MCP criado")
        print(f"📋 Funções registradas: {list(server.tools.keys())}")
        
        for tool_name, tool_info in server.tools.items():
            print(f"  🔧 {tool_name}: {tool_info['description']}")
            
    except Exception as e:
        print(f"❌ Erro no servidor MCP: {e}")
    
    print("\n" + "=" * 40)
    print("✅ Teste finalizado!")

if __name__ == "__main__":
    test_mcp_server()