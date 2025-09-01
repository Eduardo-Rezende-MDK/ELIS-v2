#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Produtos Recentes Duplicados - MySQL Manager ELIS v2
Script para analisar os 10 produtos mais recentes e suas duplicatas
"""

import sys
import os
from pathlib import Path

# Adicionar o diretorio mysql ao path
sys.path.insert(0, str(Path(__file__).parent))

from mysql_ai import conectar_e_executar
import json

def analisar_produtos_recentes():
    """
    Analisa os 10 produtos mais recentes e suas duplicatas
    """
    print("=== ANALISE DOS 10 PRODUTOS MAIS RECENTES ===")
    
    try:
        # Query para obter os 10 produtos mais recentes
        query_recentes = """
        SELECT id, nome, codigo_barras, status, venda, id_super, created_at, updated_at
        FROM produtos 
        ORDER BY created_at DESC
        LIMIT 10
        """
        
        resultado = conectar_e_executar('integrafoods', query_recentes)
        
        if not resultado.get('sucesso'):
            print(f"Erro: {resultado.get('erro')}")
            return
        
        produtos_recentes = resultado.get('dados', [])
        print(f"Produtos mais recentes encontrados: {len(produtos_recentes)}")
        
        print("\n=== LISTA DOS 10 PRODUTOS MAIS RECENTES ===")
        for i, produto in enumerate(produtos_recentes, 1):
            print(f"\n{i}. ID: {produto.get('id')}")
            print(f"   Nome: {produto.get('nome', 'N/A')[:60]}")
            print(f"   Codigo: {produto.get('codigo_barras', 'N/A')}")
            print(f"   Status: {'Ativo' if produto.get('status') == 1 else 'Inativo'}")
            print(f"   Venda: {'Sim' if produto.get('venda') == 1 else 'Nao'}")
            print(f"   Super: {produto.get('id_super')}")
            print(f"   Criado: {produto.get('created_at')}")
        
        # Analisar duplicatas para cada produto
        print("\n=== ANALISE DE DUPLICATAS POR PRODUTO ===")
        
        total_duplicatas = 0
        produtos_com_duplicatas = 0
        
        for i, produto in enumerate(produtos_recentes, 1):
            codigo_barras = produto.get('codigo_barras')
            produto_id = produto.get('id')
            
            if not codigo_barras or codigo_barras == '':
                print(f"\n{i}. Produto ID {produto_id}: SEM CODIGO DE BARRAS")
                continue
            
            # Query para contar duplicatas do codigo de barras
            query_duplicatas = f"""
            SELECT 
                COUNT(*) as total_duplicatas,
                GROUP_CONCAT(id ORDER BY created_at) as ids_produtos
            FROM produtos 
            WHERE codigo_barras = '{codigo_barras}'
            """
            
            resultado_dup = conectar_e_executar('integrafoods', query_duplicatas)
            
            if resultado_dup.get('sucesso'):
                dados_dup = resultado_dup.get('dados', [])
                if dados_dup:
                    total_dup = dados_dup[0].get('total_duplicatas', 0)
                    ids_produtos = dados_dup[0].get('ids_produtos', '')
                    
                    print(f"\n{i}. Produto ID {produto_id}:")
                    print(f"   Codigo: {codigo_barras}")
                    print(f"   Total de duplicatas: {total_dup}")
                    
                    if total_dup > 1:
                        produtos_com_duplicatas += 1
                        total_duplicatas += total_dup
                        print(f"   IDs duplicados: {ids_produtos}")
                        
                        # Mostrar detalhes das duplicatas
                        if total_dup <= 5:  # Mostrar detalhes se nao for muitas
                            query_detalhes = f"""
                            SELECT id, nome, status, id_super, created_at
                            FROM produtos 
                            WHERE codigo_barras = '{codigo_barras}'
                            ORDER BY created_at
                            """
                            
                            resultado_det = conectar_e_executar('integrafoods', query_detalhes)
                            
                            if resultado_det.get('sucesso'):
                                detalhes = resultado_det.get('dados', [])
                                print(f"   Detalhes das duplicatas:")
                                for j, detalhe in enumerate(detalhes, 1):
                                    status_txt = 'Ativo' if detalhe.get('status') == 1 else 'Inativo'
                                    print(f"     {j}. ID {detalhe.get('id')} | {status_txt} | Super: {detalhe.get('id_super')} | {detalhe.get('created_at')}")
                    else:
                        print(f"   SEM DUPLICATAS (produto unico)")
            else:
                print(f"\n{i}. Produto ID {produto_id}: ERRO ao verificar duplicatas")
        
        # Resumo final
        print(f"\n=== RESUMO DA ANALISE ===")
        print(f"Total de produtos analisados: {len(produtos_recentes)}")
        print(f"Produtos com duplicatas: {produtos_com_duplicatas}")
        print(f"Produtos sem duplicatas: {len(produtos_recentes) - produtos_com_duplicatas}")
        print(f"Total de registros duplicados: {total_duplicatas}")
        
        if produtos_com_duplicatas > 0:
            media_duplicatas = total_duplicatas / produtos_com_duplicatas
            print(f"Media de duplicatas por produto: {media_duplicatas:.1f}")
        
        # Verificar padroes temporais
        print(f"\n=== PADROES TEMPORAIS ===")
        
        if produtos_recentes:
            primeiro = produtos_recentes[-1].get('created_at')
            ultimo = produtos_recentes[0].get('created_at')
            print(f"Periodo analisado: {primeiro} ate {ultimo}")
            
            # Verificar id_super dos produtos recentes
            supers = {}
            for produto in produtos_recentes:
                id_super = produto.get('id_super')
                if id_super:
                    supers[id_super] = supers.get(id_super, 0) + 1
            
            print(f"\nDistribuicao por id_super:")
            for super_id, count in sorted(supers.items()):
                print(f"  id_super {super_id}: {count} produtos")
        
    except Exception as e:
        print(f"Erro durante analise: {e}")

def verificar_tendencia_duplicacao():
    """
    Verifica a tendencia de duplicacao nos produtos mais recentes
    """
    print(f"\n=== TENDENCIA DE DUPLICACAO ===")
    
    try:
        # Query para verificar duplicacao por periodo
        query_tendencia = """
        SELECT 
            DATE(created_at) as data_criacao,
            COUNT(*) as total_produtos,
            COUNT(DISTINCT codigo_barras) as codigos_unicos,
            (COUNT(*) - COUNT(DISTINCT codigo_barras)) as duplicatas_criadas
        FROM produtos 
        WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
        AND codigo_barras IS NOT NULL 
        AND codigo_barras != ''
        GROUP BY DATE(created_at)
        ORDER BY data_criacao DESC
        LIMIT 7
        """
        
        resultado = conectar_e_executar('integrafoods', query_tendencia)
        
        if resultado.get('sucesso'):
            dados = resultado.get('dados', [])
            
            if dados:
                print("Duplicacao por dia (ultimos 7 dias):")
                print("-" * 70)
                print(f"{'Data':<12} {'Total':<8} {'Unicos':<8} {'Duplicatas':<10} {'Taxa %':<8}")
                print("-" * 70)
                
                total_geral = 0
                duplicatas_geral = 0
                
                for item in dados:
                    data = item.get('data_criacao', 'N/A')
                    total = item.get('total_produtos', 0)
                    unicos = item.get('codigos_unicos', 0)
                    duplicatas = item.get('duplicatas_criadas', 0)
                    
                    taxa = (duplicatas / total * 100) if total > 0 else 0
                    
                    print(f"{data:<12} {total:<8} {unicos:<8} {duplicatas:<10} {taxa:<7.1f}%")
                    
                    total_geral += total
                    duplicatas_geral += duplicatas
                
                print("-" * 70)
                taxa_geral = (duplicatas_geral / total_geral * 100) if total_geral > 0 else 0
                print(f"{'TOTAL':<12} {total_geral:<8} {total_geral-duplicatas_geral:<8} {duplicatas_geral:<10} {taxa_geral:<7.1f}%")
                
                print(f"\nCONCLUSAO:")
                if taxa_geral > 50:
                    print(f"  CRITICO: {taxa_geral:.1f}% dos produtos criados sao duplicatas!")
                elif taxa_geral > 25:
                    print(f"  ALTO: {taxa_geral:.1f}% dos produtos criados sao duplicatas")
                elif taxa_geral > 10:
                    print(f"  MODERADO: {taxa_geral:.1f}% dos produtos criados sao duplicatas")
                else:
                    print(f"  BAIXO: {taxa_geral:.1f}% dos produtos criados sao duplicatas")
            else:
                print("Nenhum dado encontrado para os ultimos 7 dias")
        else:
            print(f"Erro: {resultado.get('erro')}")
            
    except Exception as e:
        print(f"Erro durante verificacao de tendencia: {e}")

def main():
    """
    Funcao principal
    """
    try:
        # Analisar produtos recentes
        analisar_produtos_recentes()
        
        # Verificar tendencia
        verificar_tendencia_duplicacao()
        
        print("\n=== ANALISE CONCLUIDA ===")
        
    except Exception as e:
        print(f"Erro durante execucao: {e}")

if __name__ == "__main__":
    main()