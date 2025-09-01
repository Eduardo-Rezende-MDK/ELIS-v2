#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reset do Sistema MCP - ELIS v2
Script externo para resetar completamente o sistema
"""

import subprocess
import sys
import os
import time
from pathlib import Path
import shutil

def log_msg(msg):
    """Log com timestamp"""
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")

def parar_processos():
    """Para todos os processos relacionados"""
    log_msg("🛑 Parando processos...")
    
    # Para processos Python na porta 8501 (Streamlit)
    try:
        result = subprocess.run(
            ["netstat", "-ano", "|findstr", ":8501"],
            capture_output=True, text=True, shell=True
        )
        if result.stdout and 'LISTENING' in result.stdout:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) > 4:
                        pid = parts[-1]
                        log_msg(f"🎯 Matando processo Streamlit PID: {pid}")
                        subprocess.run(["taskkill", "/F", "/PID", pid], capture_output=True)
    except Exception as e:
        log_msg(f"⚠️ Erro ao parar Streamlit: {e}")
    
    # Para processos Python na porta 8000 (MCP Server)
    try:
        result = subprocess.run(
            ["netstat", "-ano", "|findstr", ":8000"],
            capture_output=True, text=True, shell=True
        )
        if result.stdout and 'LISTENING' in result.stdout:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) > 4:
                        pid = parts[-1]
                        log_msg(f"🎯 Matando processo MCP Server PID: {pid}")
                        subprocess.run(["taskkill", "/F", "/PID", pid], capture_output=True)
    except Exception as e:
        log_msg(f"⚠️ Erro ao parar MCP Server: {e}")
    
    time.sleep(2)
    log_msg("✅ Processos parados")

def limpar_cache():
    """Limpa cache Python"""
    log_msg("🧹 Limpando cache...")
    
    # Remove __pycache__ das pastas
    base_path = Path(__file__).parent.parent
    
    for pycache_dir in base_path.rglob('__pycache__'):
        try:
            shutil.rmtree(pycache_dir)
            log_msg(f"🗑️ Removido: {pycache_dir}")
        except Exception as e:
            log_msg(f"⚠️ Erro ao remover {pycache_dir}: {e}")
    
    # Remove arquivos .pyc
    for pyc_file in base_path.rglob('*.pyc'):
        try:
            pyc_file.unlink()
            log_msg(f"🗑️ Removido: {pyc_file}")
        except Exception as e:
            log_msg(f"⚠️ Erro ao remover {pyc_file}: {e}")
    
    log_msg("✅ Cache limpo")

def reiniciar_streamlit():
    """Reinicia o Streamlit"""
    log_msg("🚀 Reiniciando Streamlit...")
    
    try:
        # Inicia novo processo Streamlit
        interface_path = Path(__file__).parent
        subprocess.Popen(
            [sys.executable, "iniciar_streamlit.py"],
            cwd=interface_path,
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
        )
        log_msg("✅ Streamlit reiniciado em nova janela")
        
    except Exception as e:
        log_msg(f"❌ Erro ao reiniciar Streamlit: {e}")

def main():
    """Função principal do reset"""
    print("🔄 RESET DO SISTEMA MCP - ELIS v2")
    print("=" * 40)
    
    parar_processos()
    limpar_cache()
    reiniciar_streamlit()
    
    print("=" * 40)
    log_msg("✅ Reset completo finalizado!")
    log_msg("🌐 Acesse: http://localhost:8501")
    
    # Aguarda antes de fechar
    time.sleep(3)

if __name__ == "__main__":
    main()