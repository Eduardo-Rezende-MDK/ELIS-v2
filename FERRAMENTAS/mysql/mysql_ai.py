#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MySQL AI Assistant - ELIS v2
Ferramenta que combina MySQL com assistencia de IA para queries
"""

from mysql_manager import MySQLManager, criar_conexao_rapida
from config import MySQLConfig, obter_config_conexao
from typing import List, Dict, Any, Optional
import json

class MySQLAI:
    """
    Classe que combina MySQL com funcionalidades de IA
    """
    
    def __init__(self, nome_conexao: str = "local"):
        self.mysql = MySQLManager()
        self.config = MySQLConfig()
        self.nome_conexao = nome_conexao
        self.conectado = False
    
    def conectar(self, nome_conexao: Optional[str] = None) -> bool:
        """
        Conecta usando configuracao salva
        
        Args:
            nome_conexao: Nome da conexao (opcional)
            
        Returns:
            bool: True se conectou com sucesso
        """
        if nome_conexao:
            self.nome_conexao = nome_conexao
        
        config_conexao = self.config.obter_conexao(self.nome_conexao)
        if not config_conexao:
            print(f"Configuracao '{self.nome_conexao}' nao encontrada")
            return False
        
        self.conectado = self.mysql.conectar(
            host=config_conexao["host"],
            database=config_conexao["database"],
            user=config_conexao["user"],
            password=config_conexao["password"],
            port=config_conexao.get("port", 3306)
        )
        
        return self.conectado
    
    def desconectar(self):
        """
        Desconecta do banco
        """
        self.mysql.desconectar()
        self.conectado = False
    
    def executar_query_com_contexto(self, query: str) -> Dict[str, Any]:
        """
        Executa query e retorna resultado com contexto adicional
        
        Args:
            query: Query SQL para executar
            
        Returns:
            Dict: Resultado com metadados
        """
        if not self.conectado:
            return {"erro": "Nao conectado ao banco", "dados": []}
        
        resultados = self.mysql.executar_query(query)
        
        return {
            "query": query,
            "total_registros": len(resultados),
            "dados": resultados,
            "conexao": self.nome_conexao,
            "sucesso": True
        }
    
    def analisar_estrutura_banco(self) -> Dict[str, Any]:
        """
        Analisa estrutura completa do banco para contexto de IA
        
        Returns:
            Dict: Estrutura do banco
        """
        if not self.conectado:
            return {"erro": "Nao conectado ao banco"}
        
        tabelas = self.mysql.listar_tabelas()
        estrutura = {
            "banco": self.nome_conexao,
            "total_tabelas": len(tabelas),
            "tabelas": {}
        }
        
        for tabela in tabelas:
            colunas = self.mysql.descrever_tabela(tabela)
            estrutura["tabelas"][tabela] = {
                "colunas": colunas,
                "total_colunas": len(colunas)
            }
        
        return estrutura
    
    def sugerir_queries_basicas(self, nome_tabela: str) -> List[str]:
        """
        Sugere queries basicas para uma tabela
        
        Args:
            nome_tabela: Nome da tabela
            
        Returns:
            List[str]: Lista de queries sugeridas
        """
        if not self.conectado:
            return []
        
        colunas = self.mysql.descrever_tabela(nome_tabela)
        if not colunas:
            return []
        
        nomes_colunas = [col["Field"] for col in colunas]
        primeira_coluna = nomes_colunas[0] if nomes_colunas else "id"
        
        queries = [
            f"SELECT * FROM {nome_tabela} LIMIT 10",
            f"SELECT COUNT(*) as total FROM {nome_tabela}",
            f"SELECT {primeira_coluna} FROM {nome_tabela} ORDER BY {primeira_coluna} DESC LIMIT 5",
            f"DESCRIBE {nome_tabela}"
        ]
        
        # Adiciona queries especificas baseadas nos tipos de colunas
        for coluna in colunas:
            if "date" in coluna["Type"].lower() or "time" in coluna["Type"].lower():
                queries.append(f"SELECT * FROM {nome_tabela} ORDER BY {coluna['Field']} DESC LIMIT 5")
                break
        
        return queries
    
    def executar_analise_rapida(self, nome_tabela: str) -> Dict[str, Any]:
        """
        Executa analise rapida de uma tabela
        
        Args:
            nome_tabela: Nome da tabela para analisar
            
        Returns:
            Dict: Resultado da analise
        """
        if not self.conectado:
            return {"erro": "Nao conectado ao banco"}
        
        # Estrutura da tabela
        estrutura = self.mysql.descrever_tabela(nome_tabela)
        
        # Total de registros
        total_result = self.mysql.executar_query(f"SELECT COUNT(*) as total FROM {nome_tabela}")
        total_registros = total_result[0]["total"] if total_result else 0
        
        # Primeiros registros
        amostra = self.mysql.executar_query(f"SELECT * FROM {nome_tabela} LIMIT 5")
        
        return {
            "tabela": nome_tabela,
            "estrutura": estrutura,
            "total_registros": total_registros,
            "amostra_dados": amostra,
            "queries_sugeridas": self.sugerir_queries_basicas(nome_tabela)
        }
    
    def gerar_relatorio_banco(self) -> Dict[str, Any]:
        """
        Gera relatorio completo do banco
        
        Returns:
            Dict: Relatorio do banco
        """
        if not self.conectado:
            return {"erro": "Nao conectado ao banco"}
        
        tabelas = self.mysql.listar_tabelas()
        relatorio = {
            "conexao": self.nome_conexao,
            "total_tabelas": len(tabelas),
            "tabelas_detalhes": {}
        }
        
        for tabela in tabelas:
            try:
                total_result = self.mysql.executar_query(f"SELECT COUNT(*) as total FROM {tabela}")
                total_registros = total_result[0]["total"] if total_result else 0
                
                colunas = self.mysql.descrever_tabela(tabela)
                
                relatorio["tabelas_detalhes"][tabela] = {
                    "total_registros": total_registros,
                    "total_colunas": len(colunas),
                    "colunas": [col["Field"] for col in colunas]
                }
            except Exception as e:
                relatorio["tabelas_detalhes"][tabela] = {"erro": str(e)}
        
        return relatorio

# Funcoes utilitarias
def conectar_e_executar(nome_conexao: str, query: str) -> Dict[str, Any]:
    """
    Conecta e executa query rapidamente
    
    Args:
        nome_conexao: Nome da conexao
        query: Query para executar
        
    Returns:
        Dict: Resultado da query
    """
    mysql_ai = MySQLAI(nome_conexao)
    if mysql_ai.conectar():
        resultado = mysql_ai.executar_query_com_contexto(query)
        mysql_ai.desconectar()
        return resultado
    return {"erro": "Falha na conexao", "dados": []}

def analisar_tabela_rapido(nome_conexao: str, nome_tabela: str) -> Dict[str, Any]:
    """
    Analisa uma tabela rapidamente
    
    Args:
        nome_conexao: Nome da conexao
        nome_tabela: Nome da tabela
        
    Returns:
        Dict: Analise da tabela
    """
    mysql_ai = MySQLAI(nome_conexao)
    if mysql_ai.conectar():
        resultado = mysql_ai.executar_analise_rapida(nome_tabela)
        mysql_ai.desconectar()
        return resultado
    return {"erro": "Falha na conexao"}

if __name__ == "__main__":
    # Exemplo de uso
    print("MySQL AI Assistant - ELIS v2")
    print("Exemplo de uso:")
    print("mysql_ai = MySQLAI('local')")
    print("mysql_ai.conectar()")
    print("resultado = mysql_ai.executar_query_com_contexto('SELECT * FROM usuarios LIMIT 5')")
    print("analise = mysql_ai.executar_analise_rapida('usuarios')")
    print("mysql_ai.desconectar()")