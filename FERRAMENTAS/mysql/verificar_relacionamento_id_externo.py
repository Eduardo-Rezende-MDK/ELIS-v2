#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificar Relacionamento ID Externo - MySQL Manager ELIS v2
Script para verificar relacionamento produtos.codigo_barras = DUAL_produtos.id_externo
"""

import sys
import os
from pathlib import Path

# Adicionar o diretorio mysql ao path
sys.path.insert(0, str(Path(__file__).parent))

from mysql_ai import conectar_e_executar
import json

def verificar_estrutura_dual_produtos():
    """
    Verifica a estrutura da tabela DUAL_produtos para identificar o campo id_externo
    """
    print("=== ESTRUTURA DA TABELA DUAL_PRODUTOS ===")
    
    try:
        query_estrutura = "DESCRIBE DUAL_produtos"
        
        resultado = conectar_e_executar('integrafoods', query_estrutura)
        
        if resultado.get('sucesso'):
            campos = resultado.get('dados', [])
            print(f"Campos encontrados na DUAL_produtos:")
            
            tem_id_externo = False
            for campo in campos:
                field_name = campo.get('Field')
                field_type = campo.get('Type')
                field_null = campo.get('Null')
                field_key = campo.get('Key')
                field_default = campo.get('Default')
                
                print(f"  {field_name}: {field_type} {'(PK)' if field_key == 'PRI' else ''} {'(NOT NULL)' if field_null == 'NO' else ''} {f'DEFAULT: {field_default}' if field_default else ''}")
                
                if field_name == 'id_externo':
                    tem_id_externo = True
            
            print(f"\nCampo 'id_externo' encontrado: {'SIM' if tem_id_externo else 'NAO'}")
            return tem_id_externo
        else:
            print(f"Erro: {resultado.get('erro')}")
            return False
            
    except Exception as e:
        print(f"Erro durante verificacao de estrutura: {e}")
        return False

def verificar_relacionamento_codigo_barras():
    """
    Verifica o relacionamento produtos.codigo_barras = DUAL_produtos.id_externo
    """
    print("\n=== VERIFICACAO DO RELACIONAMENTO ===")
    
    try:
        # 1. Verificar se existe o campo id_externo
        query_campo = """
        SELECT COUNT(*) as total_registros,
               COUNT(DISTINCT id_externo) as id_externos_unicos,
               COUNT(CASE WHEN id_externo IS NOT NULL THEN 1 END) as id_externos_nao_nulos
        FROM DUAL_produtos
        """
        
        resultado_campo = conectar_e_executar('integrafoods', query_campo)
        
        if resultado_campo.get('sucesso'):
            stats = resultado_campo.get('dados', [])[0]
            total = stats.get('total_registros', 0)
            unicos = stats.get('id_externos_unicos', 0)
            nao_nulos = stats.get('id_externos_nao_nulos', 0)
            
            print(f"1. ESTATISTICAS DO CAMPO id_externo:")
            print(f"   Total de registros na DUAL_produtos: {total}")
            print(f"   id_externo únicos: {unicos}")
            print(f"   id_externo não nulos: {nao_nulos}")
            print(f"   id_externo nulos: {total - nao_nulos}")
            
            if nao_nulos == 0:
                print(f"   PROBLEMA: Todos os id_externo são NULL!")
                return
        else:
            print(f"Erro: {resultado_campo.get('erro')}")
            return
        
        # 2. Verificar relacionamento com produtos
        print(f"\n2. RELACIONAMENTO COM PRODUTOS:")
        query_relacionamento = """
        SELECT 
            COUNT(DISTINCT p.codigo_barras) as codigos_produtos,
            COUNT(DISTINCT d.id_externo) as id_externos_dual,
            COUNT(DISTINCT CASE WHEN p.codigo_barras = d.id_externo THEN p.codigo_barras END) as relacionamentos_encontrados
        FROM produtos p
        CROSS JOIN DUAL_produtos d
        WHERE p.codigo_barras IS NOT NULL 
        AND p.codigo_barras != ''
        AND d.id_externo IS NOT NULL
        AND d.id_externo != ''
        """
        
        resultado_rel = conectar_e_executar('integrafoods', query_relacionamento)
        
        if resultado_rel.get('sucesso'):
            rel_stats = resultado_rel.get('dados', [])[0]
            codigos_produtos = rel_stats.get('codigos_produtos', 0)
            id_externos = rel_stats.get('id_externos_dual', 0)
            relacionamentos = rel_stats.get('relacionamentos_encontrados', 0)
            
            print(f"   Códigos de barras únicos em produtos: {codigos_produtos}")
            print(f"   id_externo únicos em DUAL_produtos: {id_externos}")
            print(f"   Relacionamentos encontrados: {relacionamentos}")
            
            if relacionamentos > 0:
                percentual = (relacionamentos / min(codigos_produtos, id_externos)) * 100
                print(f"   Taxa de relacionamento: {percentual:.1f}%")
            else:
                print(f"   PROBLEMA: Nenhum relacionamento encontrado!")
        else:
            print(f"Erro: {resultado_rel.get('erro')}")
        
        # 3. Exemplos de relacionamentos
        print(f"\n3. EXEMPLOS DE RELACIONAMENTOS:")
        query_exemplos = """
        SELECT 
            p.id as produto_id,
            p.nome as produto_nome,
            p.codigo_barras,
            d.id_externo,
            d.nome as dual_nome,
            d.preco,
            d.estoque
        FROM produtos p
        INNER JOIN DUAL_produtos d ON p.codigo_barras = d.id_externo
        WHERE p.id_super = 131
        ORDER BY p.id
        LIMIT 10
        """
        
        resultado_ex = conectar_e_executar('integrafoods', query_exemplos)
        
        if resultado_ex.get('sucesso'):
            exemplos = resultado_ex.get('dados', [])
            print(f"   Primeiros 10 relacionamentos encontrados:")
            
            for i, ex in enumerate(exemplos, 1):
                produto_id = ex.get('produto_id')
                produto_nome = ex.get('produto_nome', 'N/A')[:40]
                codigo_barras = ex.get('codigo_barras')
                id_externo = ex.get('id_externo')
                dual_nome = ex.get('dual_nome', 'N/A')[:40]
                preco = ex.get('preco')
                estoque = ex.get('estoque')
                
                print(f"   {i:2d}. Produto ID: {produto_id} | Código: {codigo_barras}")
                print(f"       Produto: {produto_nome}")
                print(f"       DUAL: {dual_nome} | Preço: {preco} | Estoque: {estoque}")
                print()
        else:
            print(f"   Nenhum relacionamento direto encontrado")
            print(f"   Erro: {resultado_ex.get('erro')}")
            
    except Exception as e:
        print(f"Erro durante verificacao de relacionamento: {e}")

def verificar_cobertura_relacionamento():
    """
    Verifica a cobertura do relacionamento entre as tabelas
    """
    print("\n=== COBERTURA DO RELACIONAMENTO ===")
    
    try:
        # 1. Produtos que têm correspondência na DUAL_produtos
        query_cobertura_produtos = """
        SELECT 
            COUNT(DISTINCT p.id) as produtos_total,
            COUNT(DISTINCT CASE WHEN d.id_externo IS NOT NULL THEN p.id END) as produtos_com_dual,
            COUNT(DISTINCT CASE WHEN d.id_externo IS NULL THEN p.id END) as produtos_sem_dual
        FROM produtos p
        LEFT JOIN DUAL_produtos d ON p.codigo_barras = d.id_externo
        WHERE p.id_super = 131
        """
        
        resultado_cob_prod = conectar_e_executar('integrafoods', query_cobertura_produtos)
        
        if resultado_cob_prod.get('sucesso'):
            cob_prod = resultado_cob_prod.get('dados', [])[0]
            total_produtos = cob_prod.get('produtos_total', 0)
            com_dual = cob_prod.get('produtos_com_dual', 0)
            sem_dual = cob_prod.get('produtos_sem_dual', 0)
            
            print(f"1. COBERTURA DOS PRODUTOS (id_super = 131):")
            print(f"   Total de produtos: {total_produtos}")
            print(f"   Produtos com dados na DUAL: {com_dual}")
            print(f"   Produtos sem dados na DUAL: {sem_dual}")
            
            if total_produtos > 0:
                percentual_cobertura = (com_dual / total_produtos) * 100
                print(f"   Cobertura: {percentual_cobertura:.1f}%")
        else:
            print(f"Erro: {resultado_cob_prod.get('erro')}")
        
        # 2. DUAL_produtos que têm correspondência em produtos
        query_cobertura_dual = """
        SELECT 
            COUNT(*) as dual_total,
            COUNT(DISTINCT CASE WHEN p.id IS NOT NULL THEN d.id_externo END) as dual_com_produto,
            COUNT(DISTINCT CASE WHEN p.id IS NULL THEN d.id_externo END) as dual_sem_produto
        FROM DUAL_produtos d
        LEFT JOIN produtos p ON d.id_externo = p.codigo_barras AND p.id_super = 131
        WHERE d.id_externo IS NOT NULL AND d.id_externo != ''
        """
        
        resultado_cob_dual = conectar_e_executar('integrafoods', query_cobertura_dual)
        
        if resultado_cob_dual.get('sucesso'):
            cob_dual = resultado_cob_dual.get('dados', [])[0]
            total_dual = cob_dual.get('dual_total', 0)
            com_produto = cob_dual.get('dual_com_produto', 0)
            sem_produto = cob_dual.get('dual_sem_produto', 0)
            
            print(f"\n2. COBERTURA DA DUAL_PRODUTOS:")
            print(f"   Total de registros DUAL (com id_externo): {total_dual}")
            print(f"   DUAL com produto correspondente: {com_produto}")
            print(f"   DUAL sem produto correspondente: {sem_produto}")
            
            if total_dual > 0:
                percentual_cobertura_dual = (com_produto / total_dual) * 100
                print(f"   Cobertura: {percentual_cobertura_dual:.1f}%")
        else:
            print(f"Erro: {resultado_cob_dual.get('erro')}")
            
    except Exception as e:
        print(f"Erro durante verificacao de cobertura: {e}")

def analisar_duplicatas_relacionamento():
    """
    Analisa duplicatas considerando o relacionamento id_externo
    """
    print("\n=== ANALISE DE DUPLICATAS NO RELACIONAMENTO ===")
    
    try:
        # Verificar se há duplicatas de id_externo na DUAL_produtos
        query_dup_dual = """
        SELECT 
            id_externo,
            COUNT(*) as total_registros,
            GROUP_CONCAT(DISTINCT codTabPreco ORDER BY codTabPreco) as codigos_tabela
        FROM DUAL_produtos
        WHERE id_externo IS NOT NULL AND id_externo != ''
        GROUP BY id_externo
        HAVING COUNT(*) > 1
        ORDER BY total_registros DESC
        LIMIT 10
        """
        
        resultado_dup_dual = conectar_e_executar('integrafoods', query_dup_dual)
        
        if resultado_dup_dual.get('sucesso'):
            dup_dual = resultado_dup_dual.get('dados', [])
            print(f"1. DUPLICATAS DE id_externo NA DUAL_PRODUTOS:")
            print(f"   Primeiras 10 duplicatas:")
            
            for i, dup in enumerate(dup_dual, 1):
                id_externo = dup.get('id_externo')
                total = dup.get('total_registros')
                codigos = dup.get('codigos_tabela')
                
                print(f"   {i:2d}. id_externo: {id_externo} | {total} registros")
                print(f"       Códigos tabela: {codigos}")
        else:
            print(f"Erro: {resultado_dup_dual.get('erro')}")
        
        # Verificar produtos duplicados que se relacionam com DUAL
        query_dup_produtos = """
        SELECT 
            p.codigo_barras,
            COUNT(DISTINCT p.id) as produtos_duplicados,
            COUNT(DISTINCT d.id_externo) as registros_dual,
            GROUP_CONCAT(DISTINCT p.id ORDER BY p.id) as produto_ids
        FROM produtos p
        LEFT JOIN DUAL_produtos d ON p.codigo_barras = d.id_externo
        WHERE p.id_super = 131
        AND p.codigo_barras IS NOT NULL AND p.codigo_barras != ''
        GROUP BY p.codigo_barras
        HAVING COUNT(DISTINCT p.id) > 1
        ORDER BY produtos_duplicados DESC
        LIMIT 10
        """
        
        resultado_dup_prod = conectar_e_executar('integrafoods', query_dup_produtos)
        
        if resultado_dup_prod.get('sucesso'):
            dup_prod = resultado_dup_prod.get('dados', [])
            print(f"\n2. PRODUTOS DUPLICADOS COM RELACIONAMENTO DUAL:")
            print(f"   Primeiras 10 duplicatas:")
            
            for i, dup in enumerate(dup_prod, 1):
                codigo_barras = dup.get('codigo_barras')
                produtos_dup = dup.get('produtos_duplicados')
                registros_dual = dup.get('registros_dual')
                produto_ids = dup.get('produto_ids')
                
                print(f"   {i:2d}. Código: {codigo_barras} | {produtos_dup} produtos | {registros_dual} registros DUAL")
                print(f"       IDs produtos: {produto_ids}")
        else:
            print(f"Erro: {resultado_dup_prod.get('erro')}")
            
    except Exception as e:
        print(f"Erro durante analise de duplicatas: {e}")

def main():
    """
    Função principal
    """
    try:
        # Verificar estrutura
        tem_id_externo = verificar_estrutura_dual_produtos()
        
        if not tem_id_externo:
            print("\nERRO: Campo 'id_externo' não encontrado na tabela DUAL_produtos!")
            print("Verifique se o nome do campo está correto.")
            return
        
        # Verificar relacionamento
        verificar_relacionamento_codigo_barras()
        
        # Verificar cobertura
        verificar_cobertura_relacionamento()
        
        # Analisar duplicatas
        analisar_duplicatas_relacionamento()
        
        print("\n=== RESUMO FINAL ===")
        print("\n1. RELACIONAMENTO IDENTIFICADO:")
        print("   produtos.codigo_barras = DUAL_produtos.id_externo")
        
        print("\n2. PONTOS DE ATENÇÃO:")
        print("   - Verificar se todos os id_externo estão preenchidos")
        print("   - Analisar cobertura do relacionamento")
        print("   - Considerar duplicatas em ambas as tabelas")
        
        print("\n3. RECOMENDAÇÕES:")
        print("   - Use LEFT JOIN para preservar dados de produtos sem DUAL")
        print("   - Considere GROUP BY para lidar com duplicatas")
        print("   - Monitore a integridade referencial")
        
        print("\n=== ANALISE CONCLUIDA ===")
        
    except Exception as e:
        print(f"Erro durante execução: {e}")

if __name__ == "__main__":
    main()