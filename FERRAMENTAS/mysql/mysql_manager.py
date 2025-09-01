#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ferramenta MySQL Manager - ELIS v2
Gerenciador simples para conexao e execucao de queries MySQL
"""

import mysql.connector
from mysql.connector import Error
import json
from typing import List, Dict, Any, Optional

class MySQLManager:
    """
    Classe para gerenciar conexoes e operacoes MySQL
    """
    
    def __init__(self):
        self.connection = None
        self.cursor = None
    
    def conectar(self, host: str, database: str, user: str, password: str, port: int = 3306) -> bool:
        """
        Conecta ao banco MySQL
        
        Args:
            host: Endereco do servidor MySQL
            database: Nome do banco de dados
            user: Usuario MySQL
            password: Senha MySQL
            port: Porta MySQL (padrao 3306)
            
        Returns:
            bool: True se conectou com sucesso, False caso contrario
        """
        try:
            self.connection = mysql.connector.connect(
                host=host,
                database=database,
                user=user,
                password=password,
                port=port
            )
            
            if self.connection.is_connected():
                self.cursor = self.connection.cursor(dictionary=True)
                print(f"Conectado ao MySQL: {database}@{host}:{port}")
                return True
                
        except Error as e:
            print(f"Erro ao conectar MySQL: {e}")
            return False
    
    def desconectar(self):
        """
        Desconecta do banco MySQL
        """
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Desconectado do MySQL")
    
    def executar_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """
        Executa uma query SELECT e retorna os resultados
        
        Args:
            query: Query SQL para executar
            params: Parametros para a query (opcional)
            
        Returns:
            List[Dict]: Lista de registros como dicionarios
        """
        if not self.connection or not self.connection.is_connected():
            print("Erro: Nao conectado ao banco")
            return []
        
        try:
            self.cursor.execute(query, params)
            resultados = self.cursor.fetchall()
            print(f"Query executada: {len(resultados)} registros retornados")
            return resultados
            
        except Error as e:
            print(f"Erro ao executar query: {e}")
            return []
    
    def executar_comando(self, comando: str, params: Optional[tuple] = None) -> bool:
        """
        Executa comandos INSERT, UPDATE, DELETE
        
        Args:
            comando: Comando SQL para executar
            params: Parametros para o comando (opcional)
            
        Returns:
            bool: True se executou com sucesso, False caso contrario
        """
        if not self.connection or not self.connection.is_connected():
            print("Erro: Nao conectado ao banco")
            return False
        
        try:
            self.cursor.execute(comando, params)
            self.connection.commit()
            print(f"Comando executado: {self.cursor.rowcount} linhas afetadas")
            return True
            
        except Error as e:
            print(f"Erro ao executar comando: {e}")
            return False
    
    def listar_tabelas(self) -> List[str]:
        """
        Lista todas as tabelas do banco atual
        
        Returns:
            List[str]: Lista com nomes das tabelas
        """
        resultados = self.executar_query("SHOW TABLES")
        tabelas = [list(row.values())[0] for row in resultados]
        return tabelas
    
    def descrever_tabela(self, nome_tabela: str) -> List[Dict[str, Any]]:
        """
        Descreve a estrutura de uma tabela
        
        Args:
            nome_tabela: Nome da tabela para descrever
            
        Returns:
            List[Dict]: Estrutura da tabela
        """
        return self.executar_query(f"DESCRIBE {nome_tabela}")

# Funcoes utilitarias
def criar_conexao_rapida(host: str, database: str, user: str, password: str) -> MySQLManager:
    """
    Cria uma conexao rapida ao MySQL
    
    Args:
        host: Endereco do servidor
        database: Nome do banco
        user: Usuario
        password: Senha
        
    Returns:
        MySQLManager: Instancia conectada ou None
    """
    manager = MySQLManager()
    if manager.conectar(host, database, user, password):
        return manager
    return None

def executar_query_simples(host: str, database: str, user: str, password: str, query: str) -> List[Dict[str, Any]]:
    """
    Executa uma query simples e retorna resultados
    
    Args:
        host: Endereco do servidor
        database: Nome do banco
        user: Usuario
        password: Senha
        query: Query para executar
        
    Returns:
        List[Dict]: Resultados da query
    """
    manager = criar_conexao_rapida(host, database, user, password)
    if manager:
        resultados = manager.executar_query(query)
        manager.desconectar()
        return resultados
    return []

if __name__ == "__main__":
    # Exemplo de uso
    print("MySQL Manager - ELIS v2")
    print("Exemplo de uso:")
    print("manager = MySQLManager()")
    print("manager.conectar('localhost', 'meudb', 'user', 'senha')")
    print("resultados = manager.executar_query('SELECT * FROM tabela')")
    print("manager.desconectar()")