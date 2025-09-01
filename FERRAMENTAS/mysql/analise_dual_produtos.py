#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analise DUAL_produtos - MySQL Manager ELIS v2
Script para analisar DUAL_produtos e seus relacionamentos com produtos
"""

import sys
import os
from pathlib import Path

# Adicionar o diretorio mysql ao path
sys.path.insert(0, str(Path(__file__).parent))

from mysql_ai import conectar_e_executar
import json

def analisar_dual_produtos():
    """
    Analisa a tabela DUAL_produtos e seus pares de codTabPreco
    """
    print("=== ANALISE DA TABELA DUAL_PRODUTOS ===")
    
    try:
        # 1. Estatisticas gerais da DUAL_produtos
        print("\n1. ESTATISTICAS GERAIS:")
        query_stats = """
        SELECT 
            COUNT(*) as total_registros,
            COUNT(DISTINCT id_produto) as produtos_unicos,
            COUNT(DISTINCT codTabPreco) as cod_tab_precos_unicos,
            COUNT(DISTINCT nome) as nomes_unicos
        FROM DUAL_produtos
        """
        
        resultado_stats = conectar_e_executar('integrafoods', query_stats)
        
        if resultado_stats.get('sucesso'):
            stats = resultado_stats.get('dados', [])[0]
            print(f"   Total de registros: {stats.get('total_registros', 0)}")
            print(f"   Produtos únicos (id_produto): {stats.get('produtos_unicos', 0)}")
            print(f"   Códigos de tabela únicos: {stats.get('cod_tab_precos_unicos', 0)}")
            print(f"   Nomes únicos: {stats.get('nomes_unicos', 0)}")
        else:
            print(f"   Erro: {resultado_stats.get('erro')}")
            return
        
        # 2. Analisar pares de codTabPreco
        print("\n2. ANALISE DE PARES DE CODTABPRECO:")
        query_pares = """
        SELECT 
            id_produto,
            nome,
            COUNT(*) as total_codtabpreco,
            GROUP_CONCAT(DISTINCT codTabPreco ORDER BY codTabPreco) as codigos_tabela
        FROM DUAL_produtos
        GROUP BY id_produto, nome
        ORDER BY total_codtabpreco DESC, id_produto
        LIMIT 20
        """
        
        resultado_pares = conectar_e_executar('integrafoods', query_pares)
        
        if resultado_pares.get('sucesso'):
            pares = resultado_pares.get('dados', [])
            print(f"   Primeiros 20 produtos (ordenados por quantidade de códigos):")
            
            pares_duplos = 0
            pares_simples = 0
            pares_multiplos = 0
            
            for i, par in enumerate(pares, 1):
                id_produto = par.get('id_produto')
                nome = par.get('nome', 'N/A')[:50]
                total_cod = par.get('total_codtabpreco', 0)
                codigos = par.get('codigos_tabela', 'N/A')
                
                print(f"   {i:2d}. ID: {id_produto} | Códigos: {total_cod} | {nome}")
                print(f"       Tabelas: {codigos}")
                
                if total_cod == 2:
                    pares_duplos += 1
                elif total_cod == 1:
                    pares_simples += 1
                else:
                    pares_multiplos += 1
            
            print(f"\n   Resumo dos primeiros 20:")
            print(f"   - Produtos com 2 códigos (pares): {pares_duplos}")
            print(f"   - Produtos com 1 código (simples): {pares_simples}")
            print(f"   - Produtos com 3+ códigos (múltiplos): {pares_multiplos}")
        else:
            print(f"   Erro: {resultado_pares.get('erro')}")
        
        # 3. Distribuição geral de códigos por produto
        print("\n3. DISTRIBUICAO GERAL DE CODIGOS POR PRODUTO:")
        query_distribuicao = """
        SELECT 
            total_codtabpreco,
            COUNT(*) as quantidade_produtos
        FROM (
            SELECT 
                id_produto,
                COUNT(*) as total_codtabpreco
            FROM DUAL_produtos
            GROUP BY id_produto
        ) as subquery
        GROUP BY total_codtabpreco
        ORDER BY total_codtabpreco
        """
        
        resultado_dist = conectar_e_executar('integrafoods', query_distribuicao)
        
        if resultado_dist.get('sucesso'):
            distribuicao = resultado_dist.get('dados', [])
            print("   Distribuição:")
            
            total_produtos_dual = 0
            produtos_com_pares = 0
            
            for item in distribuicao:
                cod_count = item.get('total_codtabpreco', 0)
                prod_count = item.get('quantidade_produtos', 0)
                total_produtos_dual += prod_count
                
                if cod_count == 2:
                    produtos_com_pares = prod_count
                
                print(f"   - {cod_count} código(s): {prod_count} produtos")
            
            print(f"\n   Total de produtos únicos na DUAL_produtos: {total_produtos_dual}")
            print(f"   Produtos com exatamente 2 códigos (pares): {produtos_com_pares}")
            
            if total_produtos_dual > 0:
                percentual_pares = (produtos_com_pares / total_produtos_dual) * 100
                print(f"   Percentual de produtos em pares: {percentual_pares:.1f}%")
        else:
            print(f"   Erro: {resultado_dist.get('erro')}")
        
        return total_produtos_dual if 'total_produtos_dual' in locals() else 0
        
    except Exception as e:
        print(f"Erro durante analise DUAL_produtos: {e}")
        return 0

def verificar_relacionamento_produtos():
    """
    Verifica quantos produtos da DUAL_produtos estão na tabela produtos
    """
    print("\n=== RELACIONAMENTO DUAL_PRODUTOS <-> PRODUTOS ===")
    
    try:
        # 1. Produtos da DUAL que existem na tabela produtos
        print("\n1. PRODUTOS DA DUAL_PRODUTOS NA TABELA PRODUTOS:")
        query_relacionamento = """
        SELECT 
            COUNT(DISTINCT d.id_produto) as produtos_dual_total,
            COUNT(DISTINCT p.id) as produtos_encontrados_produtos,
            COUNT(DISTINCT CASE WHEN p.id IS NULL THEN d.id_produto END) as produtos_nao_encontrados
        FROM DUAL_produtos d
        LEFT JOIN produtos p ON d.id_produto = p.id
        """
        
        resultado_rel = conectar_e_executar('integrafoods', query_relacionamento)
        
        if resultado_rel.get('sucesso'):
            rel = resultado_rel.get('dados', [])[0]
            dual_total = rel.get('produtos_dual_total', 0)
            encontrados = rel.get('produtos_encontrados_produtos', 0)
            nao_encontrados = rel.get('produtos_nao_encontrados', 0)
            
            print(f"   Produtos únicos na DUAL_produtos: {dual_total}")
            print(f"   Encontrados na tabela produtos: {encontrados}")
            print(f"   NÃO encontrados na tabela produtos: {nao_encontrados}")
            
            if dual_total > 0:
                percentual_encontrados = (encontrados / dual_total) * 100
                print(f"   Percentual de cobertura: {percentual_encontrados:.1f}%")
        else:
            print(f"   Erro: {resultado_rel.get('erro')}")
        
        # 2. Verificar duplicatas dos produtos encontrados
        print("\n2. DUPLICATAS DOS PRODUTOS ENCONTRADOS:")
        query_duplicatas = """
        SELECT 
            p.codigo_barras,
            COUNT(*) as total_duplicatas,
            GROUP_CONCAT(DISTINCT p.id ORDER BY p.id) as ids_produtos,
            GROUP_CONCAT(DISTINCT p.id_super ORDER BY p.id_super) as id_supers
        FROM DUAL_produtos d
        INNER JOIN produtos p ON d.id_produto = p.id
        WHERE p.codigo_barras IS NOT NULL AND p.codigo_barras != ''
        GROUP BY p.codigo_barras
        HAVING COUNT(*) > 1
        ORDER BY total_duplicatas DESC
        LIMIT 10
        """
        
        resultado_dup = conectar_e_executar('integrafoods', query_duplicatas)
        
        if resultado_dup.get('sucesso'):
            duplicatas = resultado_dup.get('dados', [])
            print(f"   Primeiras 10 duplicatas encontradas:")
            
            for i, dup in enumerate(duplicatas, 1):
                codigo = dup.get('codigo_barras')
                total = dup.get('total_duplicatas')
                ids = dup.get('ids_produtos')
                supers = dup.get('id_supers')
                
                print(f"   {i:2d}. Código: {codigo} | {total} duplicatas")
                print(f"       IDs: {ids}")
                print(f"       Supers: {supers}")
        else:
            print(f"   Erro: {resultado_dup.get('erro')}")
        
        # 3. Estatísticas de duplicação
        print("\n3. ESTATISTICAS DE DUPLICACAO:")
        query_stats_dup = """
        SELECT 
            COUNT(DISTINCT d.id_produto) as produtos_dual_na_produtos,
            COUNT(DISTINCT p.codigo_barras) as codigos_unicos,
            COUNT(*) as total_registros_produtos
        FROM DUAL_produtos d
        INNER JOIN produtos p ON d.id_produto = p.id
        WHERE p.codigo_barras IS NOT NULL AND p.codigo_barras != ''
        """
        
        resultado_stats_dup = conectar_e_executar('integrafoods', query_stats_dup)
        
        if resultado_stats_dup.get('sucesso'):
            stats_dup = resultado_stats_dup.get('dados', [])[0]
            produtos_dual_na_produtos = stats_dup.get('produtos_dual_na_produtos', 0)
            codigos_unicos = stats_dup.get('codigos_unicos', 0)
            total_registros = stats_dup.get('total_registros_produtos', 0)
            
            print(f"   Produtos da DUAL encontrados em produtos: {produtos_dual_na_produtos}")
            print(f"   Códigos de barras únicos: {codigos_unicos}")
            print(f"   Total de registros na produtos: {total_registros}")
            
            if codigos_unicos > 0:
                duplicatas_total = total_registros - codigos_unicos
                taxa_duplicacao = (duplicatas_total / total_registros) * 100
                print(f"   Registros duplicados: {duplicatas_total}")
                print(f"   Taxa de duplicação: {taxa_duplicacao:.1f}%")
        else:
            print(f"   Erro: {resultado_stats_dup.get('erro')}")
            
    except Exception as e:
        print(f"Erro durante verificacao de relacionamento: {e}")

def gerar_lista_produtos_unicos():
    """
    Gera lista de produtos únicos da DUAL_produtos contornando os pares
    """
    print("\n=== LISTA DE PRODUTOS UNICOS (CONTORNANDO PARES) ===")
    
    try:
        # Query para obter produtos únicos, priorizando um dos códigos de tabela
        query_unicos = """
        SELECT 
            id_produto,
            nome,
            MIN(codTabPreco) as codTabPreco_principal,
            COUNT(*) as total_codigos,
            GROUP_CONCAT(DISTINCT codTabPreco ORDER BY codTabPreco) as todos_codigos,
            preco,
            estoque,
            ativo
        FROM DUAL_produtos
        GROUP BY id_produto, nome
        ORDER BY id_produto
        LIMIT 20
        """
        
        resultado_unicos = conectar_e_executar('integrafoods', query_unicos)
        
        if resultado_unicos.get('sucesso'):
            unicos = resultado_unicos.get('dados', [])
            print(f"\nPrimeiros 20 produtos únicos (1 por id_produto):")
            print("-" * 100)
            
            for i, produto in enumerate(unicos, 1):
                id_produto = produto.get('id_produto')
                nome = produto.get('nome', 'N/A')[:40]
                cod_principal = produto.get('codTabPreco_principal')
                total_cod = produto.get('total_codigos')
                todos_cod = produto.get('todos_codigos')
                preco = produto.get('preco', 'N/A')
                estoque = produto.get('estoque', 'N/A')
                ativo = produto.get('ativo', 'N/A')
                
                print(f"{i:2d}. ID: {id_produto} | Cod: {cod_principal} | {nome}")
                print(f"    Total códigos: {total_cod} ({todos_cod})")
                print(f"    Preço: {preco} | Estoque: {estoque} | Ativo: {ativo}")
                print()
        else:
            print(f"Erro: {resultado_unicos.get('erro')}")
        
        # Query para contar total de produtos únicos
        query_count_unicos = """
        SELECT COUNT(DISTINCT id_produto) as total_produtos_unicos
        FROM DUAL_produtos
        """
        
        resultado_count = conectar_e_executar('integrafoods', query_count_unicos)
        
        if resultado_count.get('sucesso'):
            count = resultado_count.get('dados', [])[0]
            total_unicos = count.get('total_produtos_unicos', 0)
            print(f"\nTOTAL DE PRODUTOS ÚNICOS NA DUAL_PRODUTOS: {total_unicos}")
        else:
            print(f"Erro ao contar únicos: {resultado_count.get('erro')}")
            
    except Exception as e:
        print(f"Erro durante geração de lista única: {e}")

def main():
    """
    Função principal
    """
    try:
        # Analisar DUAL_produtos
        total_produtos_dual = analisar_dual_produtos()
        
        # Verificar relacionamento com produtos
        verificar_relacionamento_produtos()
        
        # Gerar lista de produtos únicos
        gerar_lista_produtos_unicos()
        
        print("\n=== RESUMO FINAL ===")
        print("\n1. DUAL_PRODUTOS:")
        print("   - Contém dados de produtos recebidos do cliente")
        print("   - Produtos aparecem em pares com diferentes codTabPreco")
        print("   - Necessário agrupar por id_produto para obter lista única")
        
        print("\n2. RELACIONAMENTO COM PRODUTOS:")
        print("   - Nem todos os produtos da DUAL estão na tabela produtos")
        print("   - Produtos encontrados podem ter duplicatas por código de barras")
        print("   - Taxa de duplicação varia conforme id_super")
        
        print("\n3. RECOMENDAÇÕES:")
        print("   - Use GROUP BY id_produto para contornar pares na DUAL_produtos")
        print("   - Verifique cobertura antes de integrar dados")
        print("   - Considere id_super ao analisar duplicatas")
        
        print("\n=== ANALISE CONCLUIDA ===")
        
    except Exception as e:
        print(f"Erro durante execução: {e}")

if __name__ == "__main__":
    main()