#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuracoes MySQL - ELIS v2
Arquivo de configuracao para conexoes MySQL
"""

import json
import os
from typing import Dict, Any

class MySQLConfig:
    """
    Classe para gerenciar configuracoes de conexao MySQL
    """
    
    def __init__(self, arquivo_config: str = "mysql_config.json"):
        self.arquivo_config = arquivo_config
        self.configuracoes = {}
        self.carregar_configuracoes()
    
    def carregar_configuracoes(self):
        """
        Carrega configuracoes do arquivo JSON
        """
        if os.path.exists(self.arquivo_config):
            try:
                with open(self.arquivo_config, 'r', encoding='utf-8') as f:
                    self.configuracoes = json.load(f)
                print(f"Configuracoes carregadas de {self.arquivo_config}")
            except Exception as e:
                print(f"Erro ao carregar configuracoes: {e}")
                self.criar_configuracao_padrao()
        else:
            self.criar_configuracao_padrao()
    
    def criar_configuracao_padrao(self):
        """
        Cria arquivo de configuracao padrao
        """
        self.configuracoes = {
            "conexoes": {
                "local": {
                    "host": "localhost",
                    "port": 3306,
                    "database": "test",
                    "user": "root",
                    "password": ""
                },
                "integrafoods": {
                    "host": "mysql.integrafoods.ind.br",
                    "port": 3306,
                    "database": "integrafoodser01",
                    "user": "integrafoodser01",
                    "password": "H9i1p8X247L3e6s4S5"
                },
                "desenvolvimento": {
                    "host": "dev-server",
                    "port": 3306,
                    "database": "dev_db",
                    "user": "dev_user",
                    "password": "dev_pass"
                }
            }
        }
        self.salvar_configuracoes()
    
    def salvar_configuracoes(self):
        """
        Salva configuracoes no arquivo JSON
        """
        try:
            with open(self.arquivo_config, 'w', encoding='utf-8') as f:
                json.dump(self.configuracoes, f, indent=2, ensure_ascii=False)
            print(f"Configuracoes salvas em {self.arquivo_config}")
        except Exception as e:
            print(f"Erro ao salvar configuracoes: {e}")
    
    def obter_conexao(self, nome: str) -> Dict[str, Any]:
        """
        Obtem configuracao de uma conexao especifica
        
        Args:
            nome: Nome da conexao
            
        Returns:
            Dict: Configuracoes da conexao
        """
        return self.configuracoes.get("conexoes", {}).get(nome, {})
    
    def adicionar_conexao(self, nome: str, host: str, database: str, user: str, password: str, port: int = 3306):
        """
        Adiciona nova configuracao de conexao
        
        Args:
            nome: Nome da conexao
            host: Endereco do servidor
            database: Nome do banco
            user: Usuario
            password: Senha
            port: Porta (padrao 3306)
        """
        if "conexoes" not in self.configuracoes:
            self.configuracoes["conexoes"] = {}
        
        self.configuracoes["conexoes"][nome] = {
            "host": host,
            "port": port,
            "database": database,
            "user": user,
            "password": password
        }
        
        self.salvar_configuracoes()
        print(f"Conexao '{nome}' adicionada")
    
    def listar_conexoes(self) -> list:
        """
        Lista todas as conexoes configuradas
        
        Returns:
            list: Lista com nomes das conexoes
        """
        return list(self.configuracoes.get("conexoes", {}).keys())
    
    def remover_conexao(self, nome: str):
        """
        Remove uma conexao configurada
        
        Args:
            nome: Nome da conexao para remover
        """
        if "conexoes" in self.configuracoes and nome in self.configuracoes["conexoes"]:
            del self.configuracoes["conexoes"][nome]
            self.salvar_configuracoes()
            print(f"Conexao '{nome}' removida")
        else:
            print(f"Conexao '{nome}' nao encontrada")

# Funcoes utilitarias
def obter_config_conexao(nome_conexao: str = "local") -> Dict[str, Any]:
    """
    Obtem configuracao de conexao rapidamente
    
    Args:
        nome_conexao: Nome da conexao (padrao 'local')
        
    Returns:
        Dict: Configuracoes da conexao
    """
    config = MySQLConfig()
    return config.obter_conexao(nome_conexao)

if __name__ == "__main__":
    # Exemplo de uso
    print("MySQL Config - ELIS v2")
    config = MySQLConfig()
    print("Conexoes disponiveis:", config.listar_conexoes())
    print("Configuracao local:", config.obter_conexao("local"))