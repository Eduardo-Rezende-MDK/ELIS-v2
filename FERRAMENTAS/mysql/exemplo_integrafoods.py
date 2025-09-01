#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exemplo Integrafoods - MySQL Manager ELIS v2
Exemplo de uso com a conexao integrafoods extraida
"""

from mysql_ai import MySQLAI
from config import MySQLConfig
import json

def testar_conexao_integrafoods():
    """
    Testa a conexao com o banco integrafoods
    """
    print("=== Testando Conexao Integrafoods ===")
    
    # Verificar se a configuracao existe
    config = MySQLConfig()
    conexoes = config.listar_conexoes()
    print(f"Conexoes disponiveis: {conexoes}")
    
    if "integrafoods" not in conexoes:
        print("Configuracao 'integrafoods' nao encontrada")
        return False
    
    # Mostrar configuracao (sem senha)
    config_integra = config.obter_conexao("integrafoods")
    config_safe = config_integra.copy()
    config_safe["password"] = "***"
    print(f"Configuracao integrafoods: {config_safe}")
    
    # Tentar conectar
    mysql_ai = MySQLAI("integrafoods")
    
    if mysql_ai.conectar():
        print("Conexao estabelecida com sucesso!")
        return mysql_ai
    else:
        print("Falha na conexao - verifique credenciais e conectividade")
        return None

def explorar_banco_integrafoods(mysql_ai):
    """
    Explora a estrutura do banco integrafoods
    
    Args:
        mysql_ai: Instancia conectada do MySQLAI
    """
    print("\n=== Explorando Banco Integrafoods ===")
    
    # Analisar estrutura geral
    estrutura = mysql_ai.analisar_estrutura_banco()
    
    if "erro" in estrutura:
        print(f"Erro ao analisar estrutura: {estrutura['erro']}")
        return
    
    print(f"Total de tabelas: {estrutura['total_tabelas']}")
    
    # Listar tabelas com resumo
    print("\nTabelas encontradas:")
    for nome_tabela, info in estrutura["tabelas"].items():
        print(f"- {nome_tabela}: {info['total_colunas']} colunas")
    
    # Gerar relatorio detalhado
    print("\n=== Relatorio Detalhado ===")
    relatorio = mysql_ai.gerar_relatorio_banco()
    
    if "erro" not in relatorio:
        print(f"Banco: {relatorio['conexao']}")
        print(f"Total de tabelas: {relatorio['total_tabelas']}")
        
        print("\nResumo por tabela:")
        for tabela, detalhes in relatorio["tabelas_detalhes"].items():
            if "erro" not in detalhes:
                print(f"- {tabela}:")
                print(f"  * Registros: {detalhes['total_registros']}")
                print(f"  * Colunas: {detalhes['total_colunas']}")
                print(f"  * Campos: {', '.join(detalhes['colunas'][:5])}{'...' if len(detalhes['colunas']) > 5 else ''}")
            else:
                print(f"- {tabela}: erro ao analisar")
    
    return estrutura

def analisar_tabela_especifica(mysql_ai, nome_tabela):
    """
    Analisa uma tabela especifica em detalhes
    
    Args:
        mysql_ai: Instancia conectada do MySQLAI
        nome_tabela: Nome da tabela para analisar
    """
    print(f"\n=== Analise Detalhada: {nome_tabela} ===")
    
    analise = mysql_ai.executar_analise_rapida(nome_tabela)
    
    if "erro" in analise:
        print(f"Erro ao analisar tabela: {analise['erro']}")
        return
    
    print(f"Total de registros: {analise['total_registros']}")
    print(f"Total de colunas: {len(analise['estrutura'])}")
    
    # Mostrar estrutura das colunas
    print("\nEstrutura das colunas:")
    for coluna in analise["estrutura"]:
        print(f"- {coluna['Field']}: {coluna['Type']} {'(NOT NULL)' if coluna['Null'] == 'NO' else '(NULL)'}")
    
    # Mostrar queries sugeridas
    print("\nQueries sugeridas:")
    for i, query in enumerate(analise["queries_sugeridas"], 1):
        print(f"{i}. {query}")
    
    # Executar primeira query sugerida
    if analise["queries_sugeridas"]:
        primeira_query = analise["queries_sugeridas"][0]
        print(f"\nExecutando: {primeira_query}")
        
        resultado = mysql_ai.executar_query_com_contexto(primeira_query)
        
        if resultado["sucesso"]:
            print(f"Resultado: {resultado['total_registros']} registros")
            
            # Mostrar amostra dos dados
            if resultado["dados"] and len(resultado["dados"]) > 0:
                print("\nAmostra dos dados:")
                for i, registro in enumerate(resultado["dados"][:3], 1):
                    print(f"Registro {i}:")
                    for campo, valor in registro.items():
                        # Limitar tamanho dos valores para exibicao
                        valor_str = str(valor)[:50] + "..." if len(str(valor)) > 50 else str(valor)
                        print(f"  {campo}: {valor_str}")
                    print()
        else:
            print("Erro ao executar query")

def executar_queries_personalizadas(mysql_ai):
    """
    Executa algumas queries personalizadas de exemplo
    
    Args:
        mysql_ai: Instancia conectada do MySQLAI
    """
    print("\n=== Queries Personalizadas ===")
    
    queries_exemplo = [
        "SELECT DATABASE() as banco_atual",
        "SELECT VERSION() as versao_mysql",
        "SELECT NOW() as data_hora_atual",
        "SHOW VARIABLES LIKE 'character_set%'"
    ]
    
    for query in queries_exemplo:
        print(f"\nExecutando: {query}")
        resultado = mysql_ai.executar_query_com_contexto(query)
        
        if resultado["sucesso"] and resultado["dados"]:
            if len(resultado["dados"]) == 1:
                # Resultado unico
                registro = resultado["dados"][0]
                for campo, valor in registro.items():
                    print(f"  {campo}: {valor}")
            else:
                # Multiplos resultados
                print(f"  {resultado['total_registros']} resultados:")
                for registro in resultado["dados"][:5]:  # Mostrar apenas os primeiros 5
                    print(f"    {registro}")
        else:
            print("  Erro ou sem resultados")

def main():
    """
    Funcao principal
    """
    print("MySQL Integrafoods - ELIS v2")
    print("Exemplo de uso com conexao extraida")
    print("=" * 50)
    
    try:
        # 1. Testar conexao
        mysql_ai = testar_conexao_integrafoods()
        
        if not mysql_ai:
            print("\nNao foi possivel conectar. Verifique:")
            print("1. Conectividade com mysql.integrafoods.ind.br")
            print("2. Credenciais de acesso")
            print("3. Firewall e permissoes")
            return
        
        # 2. Explorar estrutura do banco
        estrutura = explorar_banco_integrafoods(mysql_ai)
        
        if estrutura and "tabelas" in estrutura:
            # 3. Analisar primeira tabela encontrada
            tabelas = list(estrutura["tabelas"].keys())
            if tabelas:
                primeira_tabela = tabelas[0]
                analisar_tabela_especifica(mysql_ai, primeira_tabela)
        
        # 4. Executar queries personalizadas
        executar_queries_personalizadas(mysql_ai)
        
        # 5. Desconectar
        mysql_ai.desconectar()
        
        print("\n=== Exemplo Concluido ===")
        print("Conexao integrafoods configurada e testada com sucesso!")
        
    except Exception as e:
        print(f"Erro durante execucao: {e}")
        print("Verifique a instalacao do mysql-connector-python")

if __name__ == "__main__":
    main()