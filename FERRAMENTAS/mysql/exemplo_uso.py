#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exemplo de Uso - MySQL Manager ELIS v2
Demonstra como usar a ferramenta MySQL com IA
"""

from mysql_ai import MySQLAI
from config import MySQLConfig
from mysql_manager import MySQLManager
import json

def exemplo_configuracao():
    """
    Exemplo de como configurar conexoes
    """
    print("=== Configurando Conexoes ===")
    
    config = MySQLConfig()
    
    # Adicionar conexao de exemplo
    config.adicionar_conexao(
        nome="exemplo",
        host="localhost",
        database="test",
        user="root",
        password=""
    )
    
    # Listar conexoes
    conexoes = config.listar_conexoes()
    print(f"Conexoes disponiveis: {conexoes}")
    
    # Mostrar configuracao
    config_exemplo = config.obter_conexao("exemplo")
    print(f"Configuracao 'exemplo': {config_exemplo}")

def exemplo_conexao_basica():
    """
    Exemplo de conexao e query basica
    """
    print("\n=== Conexao Basica ===")
    
    # Criar manager
    manager = MySQLManager()
    
    # Tentar conectar (ajuste as credenciais conforme necessario)
    if manager.conectar("localhost", "test", "root", ""):
        print("Conectado com sucesso!")
        
        # Listar tabelas
        tabelas = manager.listar_tabelas()
        print(f"Tabelas encontradas: {tabelas}")
        
        # Se houver tabelas, analisar a primeira
        if tabelas:
            primeira_tabela = tabelas[0]
            print(f"\nAnalisando tabela: {primeira_tabela}")
            
            # Descrever estrutura
            estrutura = manager.descrever_tabela(primeira_tabela)
            print(f"Colunas: {[col['Field'] for col in estrutura]}")
            
            # Executar query simples
            resultados = manager.executar_query(f"SELECT * FROM {primeira_tabela} LIMIT 3")
            print(f"Primeiros 3 registros: {len(resultados)} encontrados")
            
            if resultados:
                print("Exemplo de registro:")
                print(json.dumps(resultados[0], indent=2, default=str))
        
        manager.desconectar()
    else:
        print("Falha na conexao - verifique as credenciais")

def exemplo_mysql_ai():
    """
    Exemplo usando MySQL AI Assistant
    """
    print("\n=== MySQL AI Assistant ===")
    
    # Criar assistente IA
    mysql_ai = MySQLAI("local")  # Usa configuracao 'local'
    
    if mysql_ai.conectar():
        print("Conectado via MySQL AI!")
        
        # Analisar estrutura do banco
        estrutura = mysql_ai.analisar_estrutura_banco()
        print(f"\nEstrutura do banco:")
        print(f"- Total de tabelas: {estrutura.get('total_tabelas', 0)}")
        
        if "tabelas" in estrutura:
            for nome_tabela, info in estrutura["tabelas"].items():
                print(f"- {nome_tabela}: {info['total_colunas']} colunas")
        
        # Se houver tabelas, fazer analise detalhada da primeira
        tabelas = list(estrutura.get("tabelas", {}).keys())
        if tabelas:
            primeira_tabela = tabelas[0]
            print(f"\n=== Analise Detalhada: {primeira_tabela} ===")
            
            analise = mysql_ai.executar_analise_rapida(primeira_tabela)
            
            if "erro" not in analise:
                print(f"Total de registros: {analise['total_registros']}")
                print(f"Colunas: {len(analise['estrutura'])}")
                
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
                        
                        # Mostrar primeiro registro se houver
                        if resultado["dados"]:
                            print("Primeiro registro:")
                            print(json.dumps(resultado["dados"][0], indent=2, default=str))
        
        # Gerar relatorio geral
        print("\n=== Relatorio Geral ===")
        relatorio = mysql_ai.gerar_relatorio_banco()
        
        if "erro" not in relatorio:
            print(f"Conexao: {relatorio['conexao']}")
            print(f"Total de tabelas: {relatorio['total_tabelas']}")
            
            print("\nResumo das tabelas:")
            for tabela, detalhes in relatorio["tabelas_detalhes"].items():
                if "erro" not in detalhes:
                    print(f"- {tabela}: {detalhes['total_registros']} registros, {detalhes['total_colunas']} colunas")
                else:
                    print(f"- {tabela}: erro ao analisar")
        
        mysql_ai.desconectar()
    else:
        print("Falha na conexao - verifique configuracao 'local'")

def exemplo_funcoes_utilitarias():
    """
    Exemplo das funcoes utilitarias
    """
    print("\n=== Funcoes Utilitarias ===")
    
    from mysql_ai import conectar_e_executar, analisar_tabela_rapido
    
    # Execucao rapida de query
    print("Executando query rapida...")
    resultado = conectar_e_executar("local", "SELECT DATABASE() as banco_atual")
    
    if resultado.get("sucesso"):
        print(f"Banco atual: {resultado['dados'][0]['banco_atual']}")
    else:
        print(f"Erro: {resultado.get('erro', 'Desconhecido')}")
    
    # Analise rapida de tabela (se existir)
    print("\nTentando analisar tabela 'users' (se existir)...")
    analise = analisar_tabela_rapido("local", "users")
    
    if "erro" not in analise:
        print(f"Tabela 'users' tem {analise['total_registros']} registros")
    else:
        print("Tabela 'users' nao encontrada ou erro na conexao")

def main():
    """
    Funcao principal que executa todos os exemplos
    """
    print("MySQL Manager - ELIS v2")
    print("Exemplos de Uso")
    print("=" * 50)
    
    try:
        # 1. Configuracao
        exemplo_configuracao()
        
        # 2. Conexao basica
        exemplo_conexao_basica()
        
        # 3. MySQL AI
        exemplo_mysql_ai()
        
        # 4. Funcoes utilitarias
        exemplo_funcoes_utilitarias()
        
        print("\n=== Exemplos Concluidos ===")
        print("Para usar em seus projetos:")
        print("1. Configure suas conexoes com MySQLConfig")
        print("2. Use MySQLManager para operacoes basicas")
        print("3. Use MySQLAI para funcionalidades avancadas")
        
    except ImportError as e:
        print(f"Erro de importacao: {e}")
        print("Certifique-se de instalar: pip install mysql-connector-python")
    except Exception as e:
        print(f"Erro durante execucao: {e}")
        print("Verifique suas configuracoes de MySQL")

if __name__ == "__main__":
    main()