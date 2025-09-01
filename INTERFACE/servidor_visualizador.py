#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servidor Web Simples para Visualizador MCP - ELIS v2
Versão simplificada para funcionar com subprocess
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

def main():
    """Função principal simplificada"""
    try:
        porta = 8000
        
        # Verifica se o HTML existe
        if not os.path.exists("visualizador_mcp.html"):
            print("ERRO: Arquivo visualizador_mcp.html nao encontrado")
            sys.exit(1)
        
        # Configura o servidor
        handler = http.server.SimpleHTTPRequestHandler
        
        with socketserver.TCPServer(("", porta), handler) as httpd:
            print(f"Servidor iniciado na porta {porta}")
            print(f"URL: http://localhost:{porta}/visualizador_mcp.html")
            
            # Inicia o servidor
            httpd.serve_forever()
            
    except Exception as e:
        print(f"ERRO: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()