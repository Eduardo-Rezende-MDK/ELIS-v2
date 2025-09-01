#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analise Tabelas Dinamicas - MySQL Manager ELIS v2
Script para analisar tabelas dinamicas que fazem parte das amarracoes
"""

import sys
import os
from pathlib import Path

# Adicionar o diretorio mysql ao path
sys.path.insert(0, str(Path(__file__).parent))

from mysql_ai import conectar_e_executar
import json

def analisar_estrutura_dinamicas():
    """
    Analisa a estrutura das tabelas dinamicas
    """
    print("=== ESTRUTURA DAS TABELAS DINAMICAS ===")
    
    tabelas_dinamicas = [
        'dinamica_ia_ajuste',
        'dinamica_fix', 
        'dinamica_menus',
        'dinamica_menus_sub'
    ]
    
    for tabela in tabelas_dinamicas:
        print(f"\n{tabela.upper()}:")
        query_estrutura = f"DESCRIBE {tabela}"
        
        resultado = conectar_e_executar('integrafoods', query_estrutura)
        
        if resultado.get('sucesso'):
            colunas = resultado.get('dados', [])
            for coluna in colunas:
                campo = coluna.get('Field', 'N/A')
                tipo = coluna.get('Type', 'N/A')
                nulo = coluna.get('Null', 'N/A')
                chave = coluna.get('Key', 'N/A')
                default = coluna.get('Default', 'N/A')
                print(f"  {campo}: {tipo} {'(PK)' if chave == 'PRI' else ''}{'(NOT NULL)' if nulo == 'NO' else ''} {'DEFAULT: ' + str(default) if default != 'N/A' and default is not None else ''}")
        else:
            print(f"  Erro ao obter estrutura: {resultado.get('erro', 'Desconhecido')}")

def analisar_conteudo_dinamicas():
    """
    Analisa o conteudo das tabelas dinamicas
    """
    print("\n=== CONTEUDO DAS TABELAS DINAMICAS ===")
    
    # 1. DINAMICA_IA_AJUSTE
    print("\n1. DINAMICA_IA_AJUSTE:")
    query_ia_ajuste = "SELECT * FROM dinamica_ia_ajuste LIMIT 10"
    
    resultado = conectar_e_executar('integrafoods', query_ia_ajuste)
    
    if resultado.get('sucesso'):
        dados = resultado.get('dados', [])
        print(f"   Total de registros (amostra): {len(dados)}")
        
        for i, registro in enumerate(dados[:5], 1):
            print(f"   {i}. Registro:")
            for campo, valor in registro.items():
                valor_str = str(valor)[:50] + "..." if len(str(valor)) > 50 else str(valor)
                print(f"      {campo}: {valor_str}")
            print()
    else:
        print(f"   Erro: {resultado.get('erro')}")
    
    # 2. DINAMICA_FIX
    print("\n2. DINAMICA_FIX:")
    query_fix = "SELECT * FROM dinamica_fix LIMIT 10"
    
    resultado = conectar_e_executar('integrafoods', query_fix)
    
    if resultado.get('sucesso'):
        dados = resultado.get('dados', [])
        print(f"   Total de registros (amostra): {len(dados)}")
        
        for i, registro in enumerate(dados[:5], 1):
            print(f"   {i}. Registro:")
            for campo, valor in registro.items():
                valor_str = str(valor)[:50] + "..." if len(str(valor)) > 50 else str(valor)
                print(f"      {campo}: {valor_str}")
            print()
    else:
        print(f"   Erro: {resultado.get('erro')}")
    
    # 3. DINAMICA_MENUS
    print("\n3. DINAMICA_MENUS:")
    query_menus = "SELECT * FROM dinamica_menus LIMIT 10"
    
    resultado = conectar_e_executar('integrafoods', query_menus)
    
    if resultado.get('sucesso'):
        dados = resultado.get('dados', [])
        print(f"   Total de registros (amostra): {len(dados)}")
        
        for i, registro in enumerate(dados[:5], 1):
            print(f"   {i}. Registro:")
            for campo, valor in registro.items():
                valor_str = str(valor)[:50] + "..." if len(str(valor)) > 50 else str(valor)
                print(f"      {campo}: {valor_str}")
            print()
    else:
        print(f"   Erro: {resultado.get('erro')}")
    
    # 4. DINAMICA_MENUS_SUB
    print("\n4. DINAMICA_MENUS_SUB:")
    query_menus_sub = "SELECT * FROM dinamica_menus_sub LIMIT 10"
    
    resultado = conectar_e_executar('integrafoods', query_menus_sub)
    
    if resultado.get('sucesso'):
        dados = resultado.get('dados', [])
        print(f"   Total de registros (amostra): {len(dados)}")
        
        for i, registro in enumerate(dados[:5], 1):
            print(f"   {i}. Registro:")
            for campo, valor in registro.items():
                valor_str = str(valor)[:50] + "..." if len(str(valor)) > 50 else str(valor)
                print(f"      {campo}: {valor_str}")
            print()
    else:
        print(f"   Erro: {resultado.get('erro')}")

def analisar_relacionamentos_dinamicas(codigo_barras='000031000'):
    """
    Analisa relacionamentos das tabelas dinamicas com produtos
    
    Args:
        codigo_barras: Codigo de barras para analisar relacionamentos
    """
    print(f"\n=== RELACIONAMENTOS DINAMICAS - CODIGO {codigo_barras} ===")
    
    # Primeiro, obter IDs dos produtos
    query_produtos = f"""
    SELECT id, nome, id_menus_sub
    FROM produtos 
    WHERE codigo_barras = '{codigo_barras}'
    ORDER BY id
    """
    
    resultado_produtos = conectar_e_executar('integrafoods', query_produtos)
    
    if not resultado_produtos.get('sucesso'):
        print(f"Erro ao obter produtos: {resultado_produtos.get('erro')}")
        return
    
    produtos = resultado_produtos.get('dados', [])
    if not produtos:
        print("Nenhum produto encontrado")
        return
    
    produto_ids = [p.get('id') for p in produtos]
    menus_sub_ids = [p.get('id_menus_sub') for p in produtos if p.get('id_menus_sub')]
    
    print(f"Produtos encontrados: {len(produtos)}")
    print(f"IDs dos produtos: {produto_ids}")
    print(f"IDs menus_sub: {menus_sub_ids}")
    
    # Verificar relacionamentos com dinamica_menus_sub
    if menus_sub_ids:
        print("\nRELACIONAMENTO COM DINAMICA_MENUS_SUB:")
        ids_str = ','.join(map(str, menus_sub_ids))
        query_rel_menus_sub = f"""
        SELECT * FROM dinamica_menus_sub 
        WHERE id IN ({ids_str})
        """
        
        resultado = conectar_e_executar('integrafoods', query_rel_menus_sub)
        
        if resultado.get('sucesso'):
            dados = resultado.get('dados', [])
            print(f"   Registros encontrados: {len(dados)}")
            
            for registro in dados:
                print(f"   ID: {registro.get('id')} - Nome: {registro.get('nome', 'N/A')}")
                for campo, valor in registro.items():
                    if campo not in ['id', 'nome']:
                        valor_str = str(valor)[:30] + "..." if len(str(valor)) > 30 else str(valor)
                        print(f"     {campo}: {valor_str}")
        else:
            print(f"   Erro: {resultado.get('erro')}")
    
    # Verificar se ha registros relacionados nas outras tabelas dinamicas
    print("\nVERIFICACAO DE RELACIONAMENTOS INDIRETOS:")
    
    # Contar registros em cada tabela dinamica
    tabelas_dinamicas = [
        'dinamica_ia_ajuste',
        'dinamica_fix', 
        'dinamica_menus',
        'dinamica_menus_sub'
    ]
    
    for tabela in tabelas_dinamicas:
        query_count = f"SELECT COUNT(*) as total FROM {tabela}"
        resultado = conectar_e_executar('integrafoods', query_count)
        
        if resultado.get('sucesso'):
            total = resultado.get('dados', [{}])[0].get('total', 0)
            print(f"   {tabela}: {total} registros")
        else:
            print(f"   {tabela}: Erro ao contar")

def analisar_impacto_duplicados_dinamicas():
    """
    Analisa o impacto dos duplicados nas tabelas dinamicas
    """
    print("\n=== IMPACTO DOS DUPLICADOS NAS TABELAS DINAMICAS ===")
    
    # Verificar se as tabelas dinamicas tem relacionamento com id_super
    tabelas_dinamicas = [
        'dinamica_ia_ajuste',
        'dinamica_fix', 
        'dinamica_menus',
        'dinamica_menus_sub'
    ]
    
    for tabela in tabelas_dinamicas:
        print(f"\n{tabela.upper()}:")
        
        # Verificar se tem campo id_super
        query_check_super = f"SHOW COLUMNS FROM {tabela} LIKE 'id_super'"
        resultado = conectar_e_executar('integrafoods', query_check_super)
        
        if resultado.get('sucesso') and resultado.get('dados'):
            print("   Possui campo id_super - analisando distribuicao:")
            
            query_super_dist = f"""
            SELECT id_super, COUNT(*) as total
            FROM {tabela}
            WHERE id_super LIKE '%131%'
            GROUP BY id_super
            ORDER BY id_super
            """
            
            resultado_dist = conectar_e_executar('integrafoods', query_super_dist)
            
            if resultado_dist.get('sucesso'):
                dados = resultado_dist.get('dados', [])
                for item in dados:
                    id_super = item.get('id_super')
                    total = item.get('total')
                    print(f"     id_super {id_super}: {total} registros")
            else:
                print(f"     Erro ao analisar distribuicao: {resultado_dist.get('erro')}")
        else:
            print("   Nao possui campo id_super")
            
            # Contar total de registros
            query_total = f"SELECT COUNT(*) as total FROM {tabela}"
            resultado_total = conectar_e_executar('integrafoods', query_total)
            
            if resultado_total.get('sucesso'):
                total = resultado_total.get('dados', [{}])[0].get('total', 0)
                print(f"   Total de registros: {total}")

def main():
    """
    Funcao principal
    """
    try:
        # Analisar estrutura das tabelas dinamicas
        analisar_estrutura_dinamicas()
        
        # Analisar conteudo
        analisar_conteudo_dinamicas()
        
        # Analisar relacionamentos
        analisar_relacionamentos_dinamicas('000031000')
        
        # Analisar impacto dos duplicados
        analisar_impacto_duplicados_dinamicas()
        
        print("\n=== ANALISE DAS TABELAS DINAMICAS CONCLUIDA ===")
        
    except Exception as e:
        print(f"Erro durante execucao: {e}")

if __name__ == "__main__":
    main()