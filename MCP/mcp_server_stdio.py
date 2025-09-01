#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Server STDIO - ELIS v2
Servidor MCP compatível com Trae IDE usando protocolo stdio
"""

import json
import sys
import asyncio
from typing import Any, Dict, List
from mcp_rules import live, iarules

class MCPServer:
    """Servidor MCP usando protocolo stdio"""
    
    def __init__(self):
        self.tools = {
            "live": {
                "name": "live",
                "description": "Retorna número aleatório de 3 dígitos para validação do MCP",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            "iarules": {
                "name": "iarules",
                "description": "Retorna as regras da IA do projeto ELIS v2",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
    
    def send_response(self, response: Dict[str, Any]):
        """Envia resposta via stdout"""
        print(json.dumps(response), flush=True)
    
    def handle_initialize(self, request: Dict[str, Any]):
        """Responde à inicialização do MCP"""
        response = {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {
                        "listChanged": True
                    }
                },
                "serverInfo": {
                    "name": "elis-mcp-server",
                    "version": "1.0.0"
                }
            }
        }
        self.send_response(response)
    
    def handle_tools_list(self, request: Dict[str, Any]):
        """Lista as ferramentas disponíveis"""
        response = {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {
                "tools": list(self.tools.values())
            }
        }
        self.send_response(response)
    
    def handle_tools_call(self, request: Dict[str, Any]):
        """Executa uma ferramenta"""
        params = request.get("params", {})
        tool_name = params.get("name")
        
        if tool_name == "live":
            try:
                result = live()
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": f"MCP Live: {result}"
                            }
                        ]
                    }
                }
            except Exception as e:
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {
                        "code": -32603,
                        "message": f"Erro ao executar live: {str(e)}"
                    }
                }
        elif tool_name == "iarules":
            try:
                result = iarules()
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": result
                            }
                        ]
                    }
                }
            except Exception as e:
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {
                        "code": -32603,
                        "message": f"Erro ao executar iarules: {str(e)}"
                    }
                }
        else:
            response = {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32601,
                    "message": f"Ferramenta não encontrada: {tool_name}"
                }
            }
        
        self.send_response(response)
    
    def handle_request(self, request: Dict[str, Any]):
        """Processa requisições MCP"""
        method = request.get("method")
        
        if method == "initialize":
            self.handle_initialize(request)
        elif method == "tools/list":
            self.handle_tools_list(request)
        elif method == "tools/call":
            self.handle_tools_call(request)
        else:
            # Método não suportado
            response = {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32601,
                    "message": f"Método não suportado: {method}"
                }
            }
            self.send_response(response)
    
    def run(self):
        """Executa o servidor MCP"""
        try:
            for line in sys.stdin:
                line = line.strip()
                if not line:
                    continue
                
                try:
                    request = json.loads(line)
                    self.handle_request(request)
                except json.JSONDecodeError as e:
                    # Erro de parsing JSON
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {
                            "code": -32700,
                            "message": f"Erro de parsing JSON: {str(e)}"
                        }
                    }
                    self.send_response(error_response)
                except Exception as e:
                    # Erro interno
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {
                            "code": -32603,
                            "message": f"Erro interno: {str(e)}"
                        }
                    }
                    self.send_response(error_response)
        
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f"Erro fatal no servidor MCP: {e}", file=sys.stderr)

def main():
    """Função principal"""
    server = MCPServer()
    server.run()

if __name__ == "__main__":
    main()