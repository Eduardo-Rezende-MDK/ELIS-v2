#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Visualizador MCP Streamlit - ELIS v2
Interface simples para controlar o servidor MCP
"""

import streamlit as st
import subprocess
import sys
import os
import time
from pathlib import Path
import requests

def get_project_paths():
    """
    Lê os caminhos do projeto do arquivo regras.txt
    """
    try:
        regras_path = Path(__file__).parent.parent / "regras.txt"
        with open(regras_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extrai o caminho da pasta MCP
        for line in content.split('\n'):
            if 'PASTA_MCP:' in line:
                mcp_path = line.split('PASTA_MCP:')[1].strip()
                return Path(mcp_path)
        
        # Fallback para caminho relativo
        return Path(__file__).parent.parent / "MCP"
    except:
        # Fallback para caminho relativo
        return Path(__file__).parent.parent / "MCP"

# Configuração da página
st.set_page_config(
    page_title="MCP Manager - ELIS v2",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

class MCPServerManager:
    """Gerenciador do servidor MCP"""
    
    def __init__(self):
        self.server_process = None
        self.server_port = 8000
        self.server_url = f"http://localhost:{self.server_port}"
        
    def is_server_running(self) -> bool:
        """Verifica se o servidor está rodando"""
        try:
            response = requests.get(f"{self.server_url}/visualizador_mcp.html", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def start_server(self) -> bool:
        """Inicia o servidor HTML"""
        try:
            # Verifica se já está rodando
            if self.is_server_running():
                st.session_state.logs.append(f"ℹ️ {time.strftime('%H:%M:%S')} - Servidor já está rodando")
                return True
            
            st.session_state.logs.append(f"🚀 {time.strftime('%H:%M:%S')} - Iniciando servidor na porta {self.server_port}")
            
            # Verifica se a porta está livre
            if os.name == 'nt':
                try:
                    result = subprocess.run(
                        ["netstat", "-ano", "|findstr", f":{self.server_port}"],
                        capture_output=True, text=True, shell=True
                    )
                    if result.stdout and 'LISTENING' in result.stdout:
                        st.session_state.logs.append(f"⚠️ {time.strftime('%H:%M:%S')} - Porta {self.server_port} já está em uso")
                        # Tenta limpar a porta primeiro
                        lines = result.stdout.strip().split('\n')
                        for line in lines:
                            if 'LISTENING' in line:
                                parts = line.split()
                                if len(parts) > 4:
                                    pid = parts[-1]
                                    st.session_state.logs.append(f"🔄 {time.strftime('%H:%M:%S')} - Terminando processo {pid} na porta {self.server_port}")
                                    subprocess.run(["taskkill", "/F", "/PID", pid], capture_output=True)
                                    time.sleep(2)
                except Exception as e:
                    st.session_state.logs.append(f"⚠️ {time.strftime('%H:%M:%S')} - Erro ao verificar porta: {str(e)}")
            
            # Verifica se o arquivo servidor existe
            servidor_path = Path(__file__).parent / "servidor_visualizador.py"
            if not servidor_path.exists():
                error_msg = f"❌ {time.strftime('%H:%M:%S')} - Arquivo servidor_visualizador.py não encontrado em {servidor_path}"
                st.session_state.logs.append(error_msg)
                return False
            
            st.session_state.logs.append(f"✅ {time.strftime('%H:%M:%S')} - Arquivo servidor encontrado: {servidor_path}")
            
            # Comando para iniciar o servidor
            cmd = [sys.executable, "servidor_visualizador.py"]
            st.session_state.logs.append(f"🔧 {time.strftime('%H:%M:%S')} - Comando: {' '.join(cmd)}")
            st.session_state.logs.append(f"📁 {time.strftime('%H:%M:%S')} - Diretório: {Path(__file__).parent}")
            
            # Inicia o processo em background
            try:
                self.server_process = subprocess.Popen(
                    cmd,
                    cwd=Path(__file__).parent,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=False,
                    text=True
                )
                
                st.session_state.logs.append(f"✅ {time.strftime('%H:%M:%S')} - Processo iniciado com PID: {self.server_process.pid}")
                
            except Exception as e:
                error_msg = f"❌ {time.strftime('%H:%M:%S')} - Erro ao criar processo: {str(e)}"
                st.session_state.logs.append(error_msg)
                return False
            
            # Aguarda o servidor iniciar com verificações detalhadas
            st.session_state.logs.append(f"⏳ {time.strftime('%H:%M:%S')} - Aguardando servidor iniciar...")
            
            for i in range(15):  # Tenta por 15 segundos
                time.sleep(1)
                
                # Verifica se o processo ainda está rodando
                if self.server_process.poll() is not None:
                    # Processo terminou, captura output
                    stdout, stderr = self.server_process.communicate()
                    st.session_state.logs.append(f"❌ {time.strftime('%H:%M:%S')} - Processo terminou inesperadamente")
                    if stdout:
                        st.session_state.logs.append(f"📄 {time.strftime('%H:%M:%S')} - STDOUT: {stdout[:200]}")
                    if stderr:
                        st.session_state.logs.append(f"🚨 {time.strftime('%H:%M:%S')} - STDERR: {stderr[:200]}")
                    return False
                
                # Verifica se o servidor está respondendo
                if self.is_server_running():
                    st.session_state.logs.append(f"✅ {time.strftime('%H:%M:%S')} - Servidor iniciado com sucesso após {i+1} segundos")
                    return True
                
                if i % 3 == 0:  # Log a cada 3 segundos
                    st.session_state.logs.append(f"⏳ {time.strftime('%H:%M:%S')} - Tentativa {i+1}/15 - Aguardando...")
            
            # Timeout - verifica se processo ainda está rodando
            if self.server_process.poll() is None:
                st.session_state.logs.append(f"⚠️ {time.strftime('%H:%M:%S')} - Timeout: Processo rodando mas servidor não responde")
                # Tenta capturar output parcial
                try:
                    stdout, stderr = self.server_process.communicate(timeout=2)
                    if stdout:
                        st.session_state.logs.append(f"📄 {time.strftime('%H:%M:%S')} - STDOUT parcial: {stdout[:200]}")
                    if stderr:
                        st.session_state.logs.append(f"🚨 {time.strftime('%H:%M:%S')} - STDERR parcial: {stderr[:200]}")
                except:
                    pass
            else:
                st.session_state.logs.append(f"❌ {time.strftime('%H:%M:%S')} - Processo terminou durante timeout")
            
            return False
            
        except Exception as e:
            error_msg = f"❌ {time.strftime('%H:%M:%S')} - Erro crítico ao iniciar servidor: {str(e)}"
            st.session_state.logs.append(error_msg)
            st.error(f"Erro ao iniciar servidor: {e}")
            return False
    
    def stop_server(self) -> bool:
        """Para o servidor"""
        try:
            success = False
            
            # Método 1: Parar processo próprio
            if self.server_process:
                try:
                    st.session_state.logs.append(f"🔄 {time.strftime('%H:%M:%S')} - Tentando parar processo PID: {self.server_process.pid}")
                    self.server_process.terminate()
                    
                    # Aguarda o processo terminar
                    try:
                        self.server_process.wait(timeout=3)
                        st.session_state.logs.append(f"✅ {time.strftime('%H:%M:%S')} - Processo terminado graciosamente")
                    except subprocess.TimeoutExpired:
                        st.session_state.logs.append(f"⚠️ {time.strftime('%H:%M:%S')} - Timeout, forçando kill")
                        self.server_process.kill()
                        self.server_process.wait(timeout=2)
                    
                    self.server_process = None
                    success = True
                except Exception as e:
                    st.session_state.logs.append(f"❌ {time.strftime('%H:%M:%S')} - Erro ao parar processo: {str(e)}")
            
            # Método 2: Verificar se ainda está rodando e tentar kill por porta
            if not success or self.is_server_running():
                st.session_state.logs.append(f"🔄 {time.strftime('%H:%M:%S')} - Tentando parar servidor na porta {self.server_port}")
                
                # No Windows, tenta usar netstat + taskkill
                if os.name == 'nt':
                    try:
                        # Encontra processo usando a porta
                        result = subprocess.run(
                            ["netstat", "-ano", "|findstr", f":{self.server_port}"],
                            capture_output=True, text=True, shell=True
                        )
                        
                        if result.stdout:
                            lines = result.stdout.strip().split('\n')
                            for line in lines:
                                if 'LISTENING' in line:
                                    parts = line.split()
                                    if len(parts) > 4:
                                        pid = parts[-1]
                                        st.session_state.logs.append(f"🎯 {time.strftime('%H:%M:%S')} - Encontrado PID {pid} na porta {self.server_port}")
                                        
                                        # Mata o processo
                                        kill_result = subprocess.run(
                                            ["taskkill", "/F", "/PID", pid],
                                            capture_output=True, text=True
                                        )
                                        
                                        if kill_result.returncode == 0:
                                            st.session_state.logs.append(f"✅ {time.strftime('%H:%M:%S')} - Processo {pid} terminado")
                                            success = True
                                        else:
                                            st.session_state.logs.append(f"❌ {time.strftime('%H:%M:%S')} - Falha ao matar PID {pid}: {kill_result.stderr}")
                    except Exception as e:
                        st.session_state.logs.append(f"❌ {time.strftime('%H:%M:%S')} - Erro no método netstat: {str(e)}")
            
            # Verifica se realmente parou
            for i in range(3):
                time.sleep(1)
                if not self.is_server_running():
                    st.session_state.logs.append(f"✅ {time.strftime('%H:%M:%S')} - Servidor confirmado como parado")
                    return True
                st.session_state.logs.append(f"⏳ {time.strftime('%H:%M:%S')} - Aguardando parada... ({i+1}/3)")
            
            # Última verificação
            final_status = not self.is_server_running()
            if final_status:
                st.session_state.logs.append(f"✅ {time.strftime('%H:%M:%S')} - Servidor parado com sucesso")
            else:
                st.session_state.logs.append(f"❌ {time.strftime('%H:%M:%S')} - Servidor ainda está rodando após tentativas")
            
            return final_status
            
        except Exception as e:
            error_msg = f"❌ {time.strftime('%H:%M:%S')} - Erro crítico ao parar servidor: {str(e)}"
            st.session_state.logs.append(error_msg)
            st.error(f"Erro ao parar servidor: {e}")
            return False

def main():
    """Função principal da aplicação Streamlit"""
    
    # Configuração da página
    st.title("🤖 MCP Manager - ELIS v2")
    
    # Inicializar logs se não existir
    if 'logs' not in st.session_state:
        st.session_state.logs = []
    
    # Layout com sidebar esquerda e direita
    left_sidebar = st.sidebar
    
    # Sidebar esquerda
    left_sidebar.title("📋 Menu")
    page = "MCP"  # Apenas página MCP
    
    # Inicializar gerenciador de servidor
    if 'server_manager' not in st.session_state:
        st.session_state.server_manager = MCPServerManager()
    
    server_manager = st.session_state.server_manager
    
    if page == "MCP":
        
        # Layout principal com colunas
        main_col, log_col = st.columns([2, 1])
        
        with main_col:
            st.header("🔧 Controle do Servidor MCP")
            
            # Status do servidor
            server_running = server_manager.is_server_running()
            
            # Status visual
            if server_running:
                st.success("✅ Servidor Online")
                st.info(f"🌐 URL: {server_manager.server_url}/visualizador_mcp.html")
            else:
                st.error("❌ Servidor Offline")
            
            # Botões de controle
            col1, col2, col3 = st.columns([1, 2, 1])
            
            # Botão de Reset
            with col1:
                if st.button("🔄 Reset Sistema", use_container_width=True, type="secondary", help="Para tudo, limpa cache e reinicia"):
                    try:
                        st.info("🔄 Executando reset do sistema...")
                        reset_script = Path(__file__).parent / "reset_sistema.py"
                        subprocess.Popen(
                            [sys.executable, str(reset_script)],
                            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
                        )
                        st.success("✅ Reset iniciado em nova janela!")
                        st.info("💡 Aguarde alguns segundos e recarregue a página")
                    except Exception as e:
                        st.error(f"❌ Erro no reset: {e}")
            
            with col2:
                if server_running:
                    if st.button("🛑 Parar Servidor", use_container_width=True, type="secondary"):
                        with st.spinner("Parando servidor..."):
                            try:
                                if server_manager.stop_server():
                                    st.session_state.logs.append(f"✅ {time.strftime('%H:%M:%S')} - Servidor parado com sucesso")
                                    st.success("✅ Servidor parado!")
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    error_msg = f"❌ {time.strftime('%H:%M:%S')} - Falha ao parar servidor"
                                    st.session_state.logs.append(error_msg)
                                    st.error("❌ Falha ao parar servidor")
                            except Exception as e:
                                error_msg = f"❌ {time.strftime('%H:%M:%S')} - Erro ao parar: {str(e)}"
                                st.session_state.logs.append(error_msg)
                                st.error(f"❌ Erro: {e}")
                else:
                    if st.button("🚀 Iniciar Servidor", use_container_width=True, type="primary"):
                        with st.spinner("Iniciando servidor..."):
                            try:
                                if server_manager.start_server():
                                    st.session_state.logs.append(f"✅ {time.strftime('%H:%M:%S')} - Servidor iniciado com sucesso")
                                    st.success("✅ Servidor iniciado!")
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    error_msg = f"❌ {time.strftime('%H:%M:%S')} - Falha ao iniciar servidor"
                                    st.session_state.logs.append(error_msg)
                                    st.error("❌ Falha ao iniciar servidor")
                            except Exception as e:
                                error_msg = f"❌ {time.strftime('%H:%M:%S')} - Erro ao iniciar: {str(e)}"
                                st.session_state.logs.append(error_msg)
                                st.error(f"❌ Erro: {e}")
            
            # Informações básicas
            if server_running:
                st.markdown("---")
                st.subheader("ℹ️ Informações")
                st.text(f"Porta: {server_manager.server_port}")
                st.text(f"Status: Online")
                st.markdown(f"**[🔗 Abrir Interface HTML]({server_manager.server_url}/visualizador_mcp.html)**")
                
                # Lista de funções MCP
                st.markdown("---")
                st.subheader("🔧 Funções MCP")
                try:
                    # Método simples que funciona no terminal
                    sys.path.insert(0, '../MCP')
                    import mcp_rules
                    
                    # Lista funções
                    functions = [f for f in dir(mcp_rules) if not f.startswith('_') and callable(getattr(mcp_rules, f))]
                    
                    if functions:
                        for func_name in functions:
                            col_func, col_btn = st.columns([2, 1])
                            with col_func:
                                st.text(f"• {func_name}")
                            with col_btn:
                                if st.button(f"▶️", key=f"exec_{func_name}", help=f"Executar {func_name}"):
                                    try:
                                        # Executa a função
                                        func = getattr(mcp_rules, func_name)
                                        result = func()
                                        
                                        # Log do resultado
                                        log_msg = f"🎯 {time.strftime('%H:%M:%S')} - {func_name}() = {result}"
                                        st.session_state.logs.append(log_msg)
                                        
                                        st.success(f"✅ {func_name}() executado!")
                                        st.rerun()
                                        
                                    except Exception as e:
                                        error_msg = f"❌ {time.strftime('%H:%M:%S')} - Erro em {func_name}(): {e}"
                                        st.session_state.logs.append(error_msg)
                                        st.error(f"Erro: {e}")
                        
                        st.text(f"Total: {len(functions)} função(ões)")
                    else:
                        st.info("Nenhuma função implementada ainda.")
                        st.text("Total: 0 funções")
                        
                except Exception as e:
                    st.error(f"Erro: {e}")
                    st.text("Total: 0 funções")
        
        with log_col:
            st.header("📋 Logs de Debug")
            
            # Botão para limpar logs
            if st.button("🗑️ Limpar Logs", use_container_width=True):
                st.session_state.logs = []
                st.rerun()
            
            # Área de logs
            if st.session_state.logs:
                # Mostrar logs mais recentes primeiro
                logs_text = "\n".join(reversed(st.session_state.logs[-20:]))  # Últimos 20 logs
                st.text_area(
                    "Logs (últimos 20):",
                    logs_text,
                    height=400,
                    disabled=False,  # Permite seleção de texto
                    key="logs_area"
                )
            else:
                st.info("Nenhum log ainda. Os erros e sucessos aparecerão aqui.")
            
            # Informações de debug
            st.markdown("---")
            st.subheader("🔍 Debug Info")
            st.text(f"Total de logs: {len(st.session_state.logs)}")
            st.text(f"Hora atual: {time.strftime('%H:%M:%S')}")
            
            # Status do processo
            if hasattr(server_manager, 'server_process') and server_manager.server_process:
                st.text(f"PID: {server_manager.server_process.pid}")
                st.text(f"Status: Rodando")
            else:
                st.text("PID: N/A")
                st.text("Status: Parado")

if __name__ == "__main__":
    main()