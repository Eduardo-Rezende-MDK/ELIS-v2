#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Amostra 20 Produtos Duplicados - MySQL Manager ELIS v2
Script para pegar amostra de 20 produtos da DUAL_produtos e verificar duplicatas em produtos
"""

import sys
import os
from pathlib import Path

# Adicionar o diretorio mysql ao path
sys.path.insert(0, str(Path(__file__).parent))

from mysql_ai import conectar_e_executar
import json

def obter_amostra_dual_produtos():
    """
    Obtém uma amostra de 20 produtos únicos da DUAL_produtos
    """
    print("=== AMOSTRA DE 20 PRODUTOS DA DUAL_PRODUTOS ===")
    
    try:
        # Pegar 20 produtos únicos da DUAL (1 por id_externo)
        query_amostra = """
        SELECT 
            id_externo as codigo_barras,
            MIN(id_produto) as id_produto_dual,
            MIN(nome) as nome_produto,
            COUNT(*) as registros_dual
        FROM DUAL_produtos
        WHERE id_externo IS NOT NULL AND id_externo != ''
        GROUP BY id_externo
        ORDER BY id_externo
        LIMIT 20
        """
        
        resultado_amostra = conectar_e_executar('integrafoods', query_amostra)
        
        if resultado_amostra.get('sucesso'):
            amostra = resultado_amostra.get('dados', [])
            print(f"\n1. AMOSTRA SELECIONADA (20 produtos únicos):")
            print(f"   {'#':<3} {'Código':<12} {'ID DUAL':<10} {'Registros DUAL':<15} {'Nome':<40}")
            print(f"   {'-'*85}")
            
            codigos_amostra = []
            for i, produto in enumerate(amostra, 1):
                codigo = produto.get('codigo_barras')
                id_dual = produto.get('id_produto_dual')
                nome = produto.get('nome_produto', 'N/A')[:35]
                registros = produto.get('registros_dual')
                
                codigos_amostra.append(codigo)
                print(f"   {i:<3} {codigo:<12} {id_dual:<10} {registros:<15} {nome:<40}")
            
            print(f"\n   Total de códigos na amostra: {len(codigos_amostra)}")
            return codigos_amostra
        else:
            print(f"   Erro: {resultado_amostra.get('erro')}")
            return []
            
    except Exception as e:
        print(f"Erro ao obter amostra: {e}")
        return []

def analisar_duplicados_amostra(codigos_amostra):
    """
    Analisa duplicados na tabela produtos para os códigos da amostra
    """
    print("\n=== ANALISE DE DUPLICADOS NA TABELA PRODUTOS ===")
    
    if not codigos_amostra:
        print("   Nenhum código para analisar.")
        return
    
    try:
        # Converter lista de códigos para string SQL
        codigos_sql = "','".join(codigos_amostra)
        codigos_sql = f"'{codigos_sql}'"
        
        # Analisar duplicados para cada código da amostra
        query_duplicados = f"""
        SELECT 
            codigo_barras,
            COUNT(*) as total_copias,
            COUNT(DISTINCT id_super) as id_supers_distintos,
            GROUP_CONCAT(DISTINCT id_super ORDER BY id_super) as lista_id_supers,
            GROUP_CONCAT(DISTINCT id ORDER BY created_at) as lista_ids,
            MIN(created_at) as primeira_criacao,
            MAX(created_at) as ultima_criacao,
            SUM(CASE WHEN status = 1 THEN 1 ELSE 0 END) as copias_ativas,
            SUM(CASE WHEN status = 0 THEN 1 ELSE 0 END) as copias_inativas
        FROM produtos
        WHERE codigo_barras IN ({codigos_sql})
        GROUP BY codigo_barras
        ORDER BY total_copias DESC, codigo_barras
        """
        
        resultado_dup = conectar_e_executar('integrafoods', query_duplicados)
        
        if resultado_dup.get('sucesso'):
            duplicados = resultado_dup.get('dados', [])
            print(f"\n1. ANALISE COMPLETA DE DUPLICADOS:")
            print(f"   {'Código':<12} {'Total':<6} {'id_supers':<15} {'Ativas':<7} {'Inativas':<8} {'Período':<25}")
            print(f"   {'-'*80}")
            
            total_copias_geral = 0
            codigos_com_duplicatas = 0
            codigos_sem_duplicatas = 0
            
            for dup in duplicados:
                codigo = dup.get('codigo_barras')
                total = dup.get('total_copias')
                id_supers_distintos = dup.get('id_supers_distintos')
                lista_supers = dup.get('lista_id_supers')
                ativas = dup.get('copias_ativas')
                inativas = dup.get('copias_inativas')
                primeira = dup.get('primeira_criacao', 'N/A')
                ultima = dup.get('ultima_criacao', 'N/A')
                
                # Formatar período
                if primeira != 'N/A' and ultima != 'N/A':
                    if str(primeira)[:10] == str(ultima)[:10]:
                        periodo = str(primeira)[:10]
                    else:
                        periodo = f"{str(primeira)[:10]} a {str(ultima)[:10]}"
                else:
                    periodo = "N/A"
                
                total_copias_geral += total
                
                if total > 1:
                    codigos_com_duplicatas += 1
                    status_dup = "DUPLICADO"
                else:
                    codigos_sem_duplicatas += 1
                    status_dup = "ÚNICO"
                
                print(f"   {codigo:<12} {total:<6} {lista_supers:<15} {ativas:<7} {inativas:<8} {periodo:<25}")
            
            print(f"\n   RESUMO GERAL:")
            print(f"   - Códigos analisados: {len(duplicados)}")
            print(f"   - Códigos SEM duplicatas: {codigos_sem_duplicatas}")
            print(f"   - Códigos COM duplicatas: {codigos_com_duplicatas}")
            print(f"   - Total de cópias: {total_copias_geral}")
            print(f"   - Média de cópias por código: {total_copias_geral/len(duplicados):.1f}")
            
            if codigos_com_duplicatas > 0:
                percentual_dup = (codigos_com_duplicatas / len(duplicados)) * 100
                print(f"   - Percentual com duplicatas: {percentual_dup:.1f}%")
        else:
            print(f"   Erro: {resultado_dup.get('erro')}")
            
    except Exception as e:
        print(f"Erro durante análise de duplicados: {e}")

def analisar_por_id_super(codigos_amostra):
    """
    Analisa especificamente por id_super = 131
    """
    print("\n=== ANALISE ESPECIFICA PARA ID_SUPER = 131 ===")
    
    if not codigos_amostra:
        print("   Nenhum código para analisar.")
        return
    
    try:
        # Converter lista de códigos para string SQL
        codigos_sql = "','".join(codigos_amostra)
        codigos_sql = f"'{codigos_sql}'"
        
        # Analisar apenas id_super = 131
        query_131 = f"""
        SELECT 
            codigo_barras,
            COUNT(*) as copias_131,
            GROUP_CONCAT(DISTINCT id ORDER BY created_at) as ids_131,
            MIN(created_at) as primeira_131,
            MAX(created_at) as ultima_131,
            SUM(CASE WHEN status = 1 THEN 1 ELSE 0 END) as ativas_131,
            SUM(CASE WHEN status = 0 THEN 1 ELSE 0 END) as inativas_131
        FROM produtos
        WHERE codigo_barras IN ({codigos_sql})
        AND id_super = 131
        GROUP BY codigo_barras
        ORDER BY copias_131 DESC, codigo_barras
        """
        
        resultado_131 = conectar_e_executar('integrafoods', query_131)
        
        if resultado_131.get('sucesso'):
            dados_131 = resultado_131.get('dados', [])
            print(f"\n1. PRODUTOS COM ID_SUPER = 131:")
            print(f"   {'Código':<12} {'Cópias':<7} {'Ativas':<7} {'Inativas':<8} {'IDs':<30}")
            print(f"   {'-'*70}")
            
            total_131 = 0
            duplicados_131 = 0
            
            for item in dados_131:
                codigo = item.get('codigo_barras')
                copias = item.get('copias_131')
                ativas = item.get('ativas_131')
                inativas = item.get('inativas_131')
                ids = item.get('ids_131', 'N/A')
                
                total_131 += copias
                if copias > 1:
                    duplicados_131 += 1
                
                # Limitar IDs mostrados
                if len(str(ids)) > 25:
                    ids_mostrar = str(ids)[:22] + "..."
                else:
                    ids_mostrar = str(ids)
                
                print(f"   {codigo:<12} {copias:<7} {ativas:<7} {inativas:<8} {ids_mostrar:<30}")
            
            print(f"\n   RESUMO ID_SUPER = 131:")
            print(f"   - Códigos encontrados: {len(dados_131)}")
            print(f"   - Códigos com duplicatas: {duplicados_131}")
            print(f"   - Total de cópias: {total_131}")
            
            if len(dados_131) > 0:
                media_131 = total_131 / len(dados_131)
                percentual_dup_131 = (duplicados_131 / len(dados_131)) * 100
                print(f"   - Média de cópias por código: {media_131:.1f}")
                print(f"   - Percentual com duplicatas: {percentual_dup_131:.1f}%")
            
            # Verificar códigos não encontrados no id_super = 131
            codigos_encontrados = [item.get('codigo_barras') for item in dados_131]
            codigos_nao_encontrados = [c for c in codigos_amostra if c not in codigos_encontrados]
            
            if codigos_nao_encontrados:
                print(f"\n   CÓDIGOS NÃO ENCONTRADOS NO ID_SUPER = 131:")
                for codigo in codigos_nao_encontrados:
                    print(f"   - {codigo}")
        else:
            print(f"   Erro: {resultado_131.get('erro')}")
            
    except Exception as e:
        print(f"Erro durante análise por id_super: {e}")

def detalhes_exemplos_duplicados(codigos_amostra):
    """
    Mostra detalhes dos primeiros 5 códigos com mais duplicatas
    """
    print("\n=== DETALHES DOS EXEMPLOS COM MAIS DUPLICATAS ===")
    
    if not codigos_amostra:
        print("   Nenhum código para analisar.")
        return
    
    try:
        # Pegar os 5 códigos com mais duplicatas
        codigos_sql = "','".join(codigos_amostra[:5])  # Primeiros 5 da amostra
        codigos_sql = f"'{codigos_sql}'"
        
        query_detalhes = f"""
        SELECT 
            id,
            codigo_barras,
            nome,
            id_super,
            status,
            created_at,
            updated_at
        FROM produtos
        WHERE codigo_barras IN ({codigos_sql})
        ORDER BY codigo_barras, created_at
        """
        
        resultado_det = conectar_e_executar('integrafoods', query_detalhes)
        
        if resultado_det.get('sucesso'):
            detalhes = resultado_det.get('dados', [])
            print(f"\n1. DETALHES DOS PRIMEIROS 5 CÓDIGOS:")
            
            codigo_atual = None
            contador = 0
            
            for item in detalhes:
                codigo = item.get('codigo_barras')
                produto_id = item.get('id')
                nome = item.get('nome', 'N/A')[:40]
                id_super = item.get('id_super')
                status = 'Ativo' if item.get('status') == 1 else 'Inativo'
                created_at = item.get('created_at')
                
                if codigo != codigo_atual:
                    if codigo_atual is not None:
                        print()  # Linha em branco entre códigos
                    codigo_atual = codigo
                    contador = 1
                    print(f"   Código: {codigo}")
                else:
                    contador += 1
                
                print(f"     {contador}. ID: {produto_id} | id_super: {id_super} | {status}")
                print(f"        Nome: {nome}")
                print(f"        Criado: {created_at}")
        else:
            print(f"   Erro: {resultado_det.get('erro')}")
            
    except Exception as e:
        print(f"Erro durante detalhamento: {e}")

def main():
    """
    Função principal
    """
    try:
        print("ANALISE DE AMOSTRA: 20 PRODUTOS DA DUAL_PRODUTOS")
        print("Objetivo: Verificar duplicatas na tabela produtos")
        print("="*60)
        
        # 1. Obter amostra da DUAL_produtos
        codigos_amostra = obter_amostra_dual_produtos()
        
        if not codigos_amostra:
            print("\nErro: Não foi possível obter amostra da DUAL_produtos.")
            return
        
        # 2. Analisar duplicados na tabela produtos
        analisar_duplicados_amostra(codigos_amostra)
        
        # 3. Análise específica para id_super = 131
        analisar_por_id_super(codigos_amostra)
        
        # 4. Detalhes dos exemplos
        detalhes_exemplos_duplicados(codigos_amostra)
        
        print("\n" + "="*60)
        print("CONCLUSÕES:")
        print("- DUAL_produtos: Produtos em pares (2 registros por código)")
        print("- Produtos: Múltiplas cópias por código (vários id_super)")
        print("- id_super = 131: Dados atuais (conforme regra estabelecida)")
        print("- Duplicação: Causada por múltiplos id_super e integrações")
        
        print("\n=== ANALISE CONCLUIDA ===")
        
    except Exception as e:
        print(f"Erro durante execução: {e}")

if __name__ == "__main__":
    main()