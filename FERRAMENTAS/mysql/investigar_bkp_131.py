#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Investigar BKP 131 - MySQL Manager ELIS v2
Script para investigar produtos com id_super LIKE 131 (backups mal feitos)
"""

import sys
import os
from pathlib import Path

# Adicionar o diretorio mysql ao path
sys.path.insert(0, str(Path(__file__).parent))

from mysql_ai import conectar_e_executar
import json

def investigar_id_super_131():
    """
    Investiga produtos com id_super que contem 131 usando LIKE
    """
    print("=== INVESTIGACAO ID_SUPER LIKE 131 ===")
    
    try:
        # Query para encontrar todos os id_super que contem 131
        query_like_131 = """
        SELECT DISTINCT id_super, COUNT(*) as total_produtos
        FROM produtos 
        WHERE id_super LIKE '%131%'
        GROUP BY id_super
        ORDER BY id_super
        """
        
        resultado = conectar_e_executar('integrafoods', query_like_131)
        
        if resultado.get('sucesso'):
            dados = resultado.get('dados', [])
            print(f"Total de id_super diferentes encontrados: {len(dados)}")
            
            print("\nID_SUPER encontrados com '131':")
            for item in dados:
                id_super = item.get('id_super')
                total = item.get('total_produtos')
                print(f"  {id_super}: {total} produtos")
            
            # Analisar cada id_super encontrado
            for item in dados:
                id_super = item.get('id_super')
                total = item.get('total_produtos')
                
                print(f"\n=== DETALHES ID_SUPER: {id_super} ({total} produtos) ===")
                
                # Query para obter detalhes dos produtos
                query_detalhes = f"""
                SELECT id, nome, codigo_barras, status, venda, created_at, updated_at
                FROM produtos 
                WHERE id_super = {id_super}
                ORDER BY created_at
                LIMIT 10
                """
                
                resultado_detalhes = conectar_e_executar('integrafoods', query_detalhes)
                
                if resultado_detalhes.get('sucesso'):
                    produtos = resultado_detalhes.get('dados', [])
                    
                    for i, produto in enumerate(produtos, 1):
                        print(f"  {i}. ID: {produto.get('id')} - {produto.get('nome', 'N/A')[:50]}")
                        print(f"     Codigo: {produto.get('codigo_barras')}")
                        print(f"     Status: {'Ativo' if produto.get('status') == 1 else 'Inativo'}")
                        print(f"     Criado: {produto.get('created_at')}")
                        
                        if i >= 5:  # Mostrar apenas os primeiros 5
                            if total > 5:
                                print(f"     ... e mais {total - 5} produtos")
                            break
                else:
                    print(f"  Erro ao obter detalhes: {resultado_detalhes.get('erro')}")
        else:
            print(f"Erro na consulta: {resultado.get('erro')}")
            
    except Exception as e:
        print(f"Erro durante investigacao: {e}")

def analisar_duplicados_por_super():
    """
    Analisa duplicados de codigo_barras agrupados por id_super
    """
    print("\n=== ANALISE DE DUPLICADOS POR ID_SUPER ===")
    
    try:
        # Query para encontrar duplicados por id_super
        query_duplicados = """
        SELECT 
            id_super,
            codigo_barras,
            COUNT(*) as total_duplicados,
            GROUP_CONCAT(id ORDER BY id) as ids_produtos
        FROM produtos 
        WHERE id_super LIKE '%131%' 
        AND codigo_barras IS NOT NULL 
        AND codigo_barras != ''
        GROUP BY id_super, codigo_barras
        HAVING COUNT(*) > 1
        ORDER BY id_super, total_duplicados DESC
        LIMIT 20
        """
        
        resultado = conectar_e_executar('integrafoods', query_duplicados)
        
        if resultado.get('sucesso'):
            duplicados = resultado.get('dados', [])
            print(f"Grupos de duplicados encontrados: {len(duplicados)}")
            
            for i, dup in enumerate(duplicados, 1):
                id_super = dup.get('id_super')
                codigo = dup.get('codigo_barras')
                total = dup.get('total_duplicados')
                ids = dup.get('ids_produtos', '')
                
                print(f"\n{i}. ID_Super: {id_super} | Codigo: {codigo}")
                print(f"   Total duplicados: {total}")
                print(f"   IDs dos produtos: {ids}")
        else:
            print(f"Erro na consulta: {resultado.get('erro')}")
            
    except Exception as e:
        print(f"Erro durante analise: {e}")

def comparar_estruturas_131():
    """
    Compara as estruturas entre diferentes id_super que contem 131
    """
    print("\n=== COMPARACAO DE ESTRUTURAS 131 ===")
    
    try:
        # Query para comparar estatisticas entre diferentes id_super
        query_comparacao = """
        SELECT 
            id_super,
            COUNT(*) as total_produtos,
            SUM(CASE WHEN status = 1 THEN 1 ELSE 0 END) as produtos_ativos,
            SUM(CASE WHEN status = 0 THEN 1 ELSE 0 END) as produtos_inativos,
            SUM(CASE WHEN venda = 1 THEN 1 ELSE 0 END) as produtos_venda,
            COUNT(DISTINCT codigo_barras) as codigos_unicos,
            MIN(created_at) as primeiro_produto,
            MAX(created_at) as ultimo_produto
        FROM produtos 
        WHERE id_super LIKE '%131%'
        GROUP BY id_super
        ORDER BY id_super
        """
        
        resultado = conectar_e_executar('integrafoods', query_comparacao)
        
        if resultado.get('sucesso'):
            dados = resultado.get('dados', [])
            
            print("Comparacao entre id_super:")
            print("-" * 100)
            print(f"{'ID_Super':<10} {'Total':<8} {'Ativos':<8} {'Inativos':<10} {'Venda':<8} {'Unicos':<8} {'Primeiro':<12} {'Ultimo':<12}")
            print("-" * 100)
            
            for item in dados:
                id_super = item.get('id_super', 'N/A')
                total = item.get('total_produtos', 0)
                ativos = item.get('produtos_ativos', 0)
                inativos = item.get('produtos_inativos', 0)
                venda = item.get('produtos_venda', 0)
                unicos = item.get('codigos_unicos', 0)
                primeiro = str(item.get('primeiro_produto', 'N/A'))[:10]
                ultimo = str(item.get('ultimo_produto', 'N/A'))[:10]
                
                print(f"{id_super:<10} {total:<8} {ativos:<8} {inativos:<10} {venda:<8} {unicos:<8} {primeiro:<12} {ultimo:<12}")
                
                # Calcular taxa de duplicacao
                if total > 0 and unicos > 0:
                    taxa_dup = ((total - unicos) / total) * 100
                    print(f"           Taxa de duplicacao: {taxa_dup:.1f}%")
        else:
            print(f"Erro na consulta: {resultado.get('erro')}")
            
    except Exception as e:
        print(f"Erro durante comparacao: {e}")

def main():
    """
    Funcao principal
    """
    try:
        # Investigar id_super com LIKE 131
        investigar_id_super_131()
        
        # Analisar duplicados por super
        analisar_duplicados_por_super()
        
        # Comparar estruturas
        comparar_estruturas_131()
        
        print("\n=== INVESTIGACAO CONCLUIDA ===")
        print("\nCONCLUSAO:")
        print("- Foram encontrados diferentes id_super contendo '131'")
        print("- Isso sugere backups ou migrações mal executadas")
        print("- Cada id_super pode representar uma versão diferente dos dados")
        print("- Recomenda-se analisar qual id_super contem os dados mais atuais")
        
    except Exception as e:
        print(f"Erro durante execucao: {e}")

if __name__ == "__main__":
    main()