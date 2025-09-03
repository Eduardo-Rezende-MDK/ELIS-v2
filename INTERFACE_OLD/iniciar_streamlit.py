#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Inicialização da Interface Streamlit MCP - ELIS v2
Script para instalar dependências e iniciar a interface dinâmica
"""

import subprocess
import sys
import os
from pathlib import Path

def check_streamlit_installed():
    """Verifica se o Streamlit está instalado"""
    try:
        import streamlit
        return True
    except ImportError:
        return False

def install_requirements():
    """Instala os requisitos necessários"""
    print("🔧 Instalando dependências da Interface Streamlit MCP...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements_streamlit.txt"
        ])
        print("✅ Dependências instaladas com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro na instalação: {e}")
        return False

def start_streamlit():
    """Inicia a interface Streamlit"""
    print("🚀 Iniciando Interface Streamlit MCP...")
    print("📱 A aplicação será aberta no seu navegador.")
    print("🔗 URL: http://localhost:8501")
    print("⏹️  Para parar: Ctrl+C")
    print("-" * 50)
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "visualizador_mcp_streamlit.py",
            "--server.port=8501",
            "--server.headless=false",
            "--browser.gatherUsageStats=false",
            "--theme.base=light"
        ])
    except KeyboardInterrupt:
        print("\n⏹️  Interface Streamlit MCP encerrada pelo usuário.")
    except Exception as e:
        print(f"❌ Erro ao iniciar: {e}")

def main():
    """Função principal"""
    print("🤖 INICIALIZADOR DA INTERFACE STREAMLIT MCP - ELIS v2")
    print("=" * 60)
    
    # Verificar se está no diretório correto
    if not Path("visualizador_mcp_streamlit.py").exists():
        print("❌ Erro: Execute este script no diretório INTERFACE")
        print("💡 Navegue até: cd INTERFACE")
        return
    
    # Verificar arquivos necessários
    required_files = [
        "visualizador_mcp_streamlit.py",
        "requirements_streamlit.txt",
        "../MCP/mcp_rules.py",
        "../regras.txt"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print("❌ Arquivos necessários não encontrados:")
        for file in missing_files:
            print(f"   • {file}")
        print("\n💡 Certifique-se de que todos os arquivos estão no local correto.")
        return
    
    print("✅ Todos os arquivos necessários encontrados.")
    
    # Verificar e instalar dependências
    if not check_streamlit_installed():
        print("📦 Streamlit não encontrado. Instalando dependências...")
        if not install_requirements():
            print("❌ Falha na instalação. Verifique sua conexão e tente novamente.")
            return
    else:
        print("✅ Streamlit já está instalado.")
    
    print("\n🎯 FUNCIONALIDADES DA INTERFACE:")
    print("• 🚀 Start/Stop do servidor HTML")
    print("• 📊 Dashboard com métricas do sistema")
    print("• ⚙️ Visualização das configurações")
    print("• Teste da função iarules()")
    print("• 🌐 Acesso à interface HTML")
    print("• 📱 Interface responsiva e dinâmica")
    
    print("\n" + "=" * 60)
    
    # Iniciar Streamlit
    start_streamlit()

if __name__ == "__main__":
    main()