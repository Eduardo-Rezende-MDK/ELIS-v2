#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Função para reiniciar o ambiente MCP do ELIS v2
Limpa cache Python e recarrega módulos
"""

import os
import sys
import glob
import importlib
import subprocess
from pathlib import Path

def limpar_cache_python():
    """
    Remove todos os arquivos .pyc e pastas __pycache__
    """
    print("🗑️ Limpando cache Python...")
    
    # Diretório atual (MCP)
    current_dir = Path(__file__).parent
    
    # Remove arquivos .pyc
    pyc_files = list(current_dir.rglob("*.pyc"))
    for pyc_file in pyc_files:
        try:
            pyc_file.unlink()
            print(f"   Removido: {pyc_file.name}")
        except Exception as e:
            print(f"   Erro ao remover {pyc_file}: {e}")
    
    # Remove pastas __pycache__
    pycache_dirs = list(current_dir.rglob("__pycache__"))
    for pycache_dir in pycache_dirs:
        try:
            import shutil
            shutil.rmtree(pycache_dir)
            print(f"   Removido diretório: {pycache_dir}")
        except Exception as e:
            print(f"   Erro ao remover {pycache_dir}: {e}")
    
    print("✅ Cache Python limpo!")

def recarregar_modulos():
    """
    Recarrega os módulos principais do MCP
    """
    print("🔄 Recarregando módulos...")
    
    modulos_para_recarregar = ['mcp_rules', 'mcp_server_stdio']
    
    for modulo in modulos_para_recarregar:
        try:
            if modulo in sys.modules:
                importlib.reload(sys.modules[modulo])
                print(f"   ✅ {modulo} recarregado")
            else:
                # Tenta importar se não estiver carregado
                __import__(modulo)
                print(f"   ✅ {modulo} importado")
        except Exception as e:
            print(f"   ❌ Erro ao recarregar {modulo}: {e}")
    
    print("✅ Módulos recarregados!")

def verificar_processos_mcp():
    """
    Verifica se há processos MCP rodando
    """
    print("🔍 Verificando processos MCP...")
    
    try:
        # Comando PowerShell para verificar processos
        cmd = 'Get-Process | Where-Object {$_.ProcessName -like "*mcp*" -or $_.CommandLine -like "*mcp*"}'
        result = subprocess.run(['powershell', '-Command', cmd], 
                              capture_output=True, text=True, timeout=10)
        
        if result.stdout.strip():
            print("   ⚠️ Processos MCP encontrados:")
            print(result.stdout)
        else:
            print("   ✅ Nenhum processo MCP ativo")
            
    except Exception as e:
        print(f"   ❌ Erro ao verificar processos: {e}")

def testar_mcp():
    """
    Testa as funções do MCP após reinicialização
    """
    print("🧪 Testando funções MCP...")
    
    try:
        # Importa e testa mcp_rules
        import mcp_rules
        resultado = mcp_rules.iarules()
        print(f"   ✅ Regras IA: {resultado}")
        
        # Testa função live
        live_result = mcp_rules.live()
        print(f"   ✅ Live test: {live_result}")
        
    except Exception as e:
        print(f"   ❌ Erro nos testes: {e}")

def reiniciar_ambiente_completo():
    """
    Função principal para reiniciar completamente o ambiente MCP
    """
    print("🚀 Iniciando reinicialização do ambiente ELIS MCP...")
    print("=" * 50)
    
    # Passo 1: Verificar processos
    verificar_processos_mcp()
    print()
    
    # Passo 2: Limpar cache
    limpar_cache_python()
    print()
    
    # Passo 3: Recarregar módulos
    recarregar_modulos()
    print()
    
    # Passo 4: Testar funcionamento
    testar_mcp()
    print()
    
    print("=" * 50)
    print("✅ Reinicialização do ambiente concluída!")
    print("🎯 Ambiente MCP pronto para uso")

if __name__ == "__main__":
    reiniciar_ambiente_completo()