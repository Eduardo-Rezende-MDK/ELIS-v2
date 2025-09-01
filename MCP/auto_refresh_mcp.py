#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto Refresh MCP - Automatiza o refresh do MCP no Trae AI
Simula o processo de refresh das configurações MCP
"""

import os
import sys
import time
import json
import subprocess
import importlib
from pathlib import Path

def kill_mcp_processes():
    """
    Mata todos os processos MCP ativos
    """
    print("🔪 Finalizando processos MCP...")
    
    try:
        # PowerShell command para matar processos MCP
        cmd = '''Get-Process | Where-Object {$_.ProcessName -like "*mcp*" -or $_.CommandLine -like "*mcp*"} | Stop-Process -Force'''
        result = subprocess.run(['powershell', '-Command', cmd], 
                              capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            print("   ✅ Processos MCP finalizados")
        else:
            print("   ⚠️ Nenhum processo MCP encontrado ou já finalizado")
            
    except Exception as e:
        print(f"   ❌ Erro ao finalizar processos: {e}")

def clear_all_cache():
    """
    Limpa todo o cache Python do projeto
    """
    print("🗑️ Limpando cache completo...")
    
    # Diretório raiz do projeto
    project_root = Path(__file__).parent.parent
    
    # Remove todos os .pyc e __pycache__ recursivamente
    cache_removed = 0
    
    for pyc_file in project_root.rglob("*.pyc"):
        try:
            pyc_file.unlink()
            cache_removed += 1
        except Exception as e:
            print(f"   ⚠️ Erro ao remover {pyc_file}: {e}")
    
    for pycache_dir in project_root.rglob("__pycache__"):
        try:
            import shutil
            shutil.rmtree(pycache_dir)
            cache_removed += 1
        except Exception as e:
            print(f"   ⚠️ Erro ao remover {pycache_dir}: {e}")
    
    print(f"   ✅ {cache_removed} itens de cache removidos")

def reload_mcp_config():
    """
    Recarrega a configuração MCP
    """
    print("📋 Recarregando configuração MCP...")
    
    config_file = Path(__file__).parent / "mcp_config.json"
    
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print("   ✅ Configuração MCP carregada")
            return config
        except Exception as e:
            print(f"   ❌ Erro ao carregar config: {e}")
    else:
        print("   ⚠️ Arquivo de configuração não encontrado")
    
    return None

def force_module_reload():
    """
    Força o reload de todos os módulos MCP
    """
    print("🔄 Forçando reload dos módulos...")
    
    # Lista de módulos para recarregar
    modules_to_reload = [
        'mcp_rules',
        'mcp_server_stdio',
        'test_mcp_functions'
    ]
    
    # Remove módulos do sys.modules para forçar reimportação
    for module_name in modules_to_reload:
        if module_name in sys.modules:
            del sys.modules[module_name]
            print(f"   🗑️ {module_name} removido do cache")
    
    # Reimporta os módulos
    for module_name in modules_to_reload:
        try:
            module = __import__(module_name)
            print(f"   ✅ {module_name} reimportado")
        except Exception as e:
            print(f"   ❌ Erro ao reimportar {module_name}: {e}")

def restart_mcp_server():
    """
    Reinicia o servidor MCP
    """
    print("🚀 Reiniciando servidor MCP...")
    
    try:
        # Muda para o diretório MCP
        mcp_dir = Path(__file__).parent
        os.chdir(mcp_dir)
        
        # Inicia o servidor MCP em background
        cmd = ['python', 'mcp_server_stdio.py']
        process = subprocess.Popen(cmd, 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        
        # Aguarda um pouco para verificar se iniciou
        time.sleep(2)
        
        if process.poll() is None:
            print(f"   ✅ Servidor MCP iniciado (PID: {process.pid})")
            return process
        else:
            print("   ❌ Falha ao iniciar servidor MCP")
            return None
            
    except Exception as e:
        print(f"   ❌ Erro ao reiniciar servidor: {e}")
        return None

def test_mcp_functions():
    """
    Testa as funções MCP após refresh
    """
    print("🧪 Testando funções MCP...")
    
    try:
        # Importa mcp_rules fresh
        import mcp_rules
        
        # Testa iarules com timestamp para verificar refresh real
        rules_result = mcp_rules.iarules()
        print(f"   ✅ IA Rules: {rules_result}")
        
        # Verifica se contém timestamp (indicando refresh real)
        if "REFRESH:" in rules_result:
            print("   ✅ Timestamp detectado - Refresh confirmado!")
            return True
        else:
            print("   ⚠️ Timestamp não encontrado - Possível cache ativo")
            return False
        
    except Exception as e:
        print(f"   ❌ Erro nos testes: {e}")
        return False

def simulate_trae_mcp_refresh():
    """
    Simula o processo de refresh do MCP no Trae AI
    """
    print("🔄 SIMULANDO REFRESH MCP DO TRAE AI")
    print("=" * 60)
    
    # Passo 1: Finalizar processos MCP
    kill_mcp_processes()
    time.sleep(1)
    
    # Passo 2: Limpar cache completo
    clear_all_cache()
    time.sleep(1)
    
    # Passo 3: Recarregar configuração
    config = reload_mcp_config()
    time.sleep(1)
    
    # Passo 4: Forçar reload dos módulos
    force_module_reload()
    time.sleep(1)
    
    # Passo 5: Reiniciar servidor MCP
    server_process = restart_mcp_server()
    time.sleep(2)
    
    # Passo 6: Testar funcionamento
    test_success = test_mcp_functions()
    
    print("=" * 60)
    
    if test_success:
        print("✅ REFRESH MCP CONCLUÍDO COM SUCESSO!")
        print("🎯 Sistema MCP totalmente atualizado e funcional")
    else:
        print("❌ REFRESH MCP CONCLUÍDO COM PROBLEMAS")
        print("⚠️ Verifique os logs acima para detalhes")
    
    return server_process

def auto_refresh_mcp():
    """
    Função principal de auto refresh
    """
    print("🤖 AUTO REFRESH MCP - ELIS v2")
    print("Automatizando o processo de refresh do MCP...")
    print()
    
    return simulate_trae_mcp_refresh()

if __name__ == "__main__":
    auto_refresh_mcp()