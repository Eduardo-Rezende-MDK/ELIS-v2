#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analise Duplicados via DUAL - MySQL Manager ELIS v2
Script para usar DUAL_produtos como referência para analisar duplicatas em produtos
"""

import sys
import os
from pathlib import Path

# Adicionar o diretorio mysql ao path
sys.path.insert(0, str(Path(__file__).parent))

from mysql_ai import conectar_e_executar
import json

def analisar_duplicados_via_dual():
    """
    Usa DUAL_produtos como referência para analisar duplicatas na tabela produtos
    """
    print("=== ANALISE DE DUPLICADOS USANDO DUAL_PRODUTOS COMO REFERENCIA ===")
    
    try:
        # 1. Estatísticas da DUAL_produtos
        print("\n1. ESTATISTICAS DA DUAL_PRODUTOS:")
        query_dual_stats = """
        SELECT 
            COUNT(*) as total_registros_dual,
            COUNT(DISTINCT id_externo) as codigos_unicos_dual,
            COUNT(DISTINCT id_produto) as produtos_unicos_dual
        FROM DUAL_produtos
        WHERE id_externo IS NOT NULL AND id_externo != ''
        """
        
        resultado_dual = conectar_e_executar('integrafoods', query_dual_stats)
        
        if resultado_dual.get('sucesso'):
            stats_dual = resultado_dual.get('dados', [])[0]
            total_dual = stats_dual.get('total_registros_dual', 0)
            codigos_dual = stats_dual.get('codigos_unicos_dual', 0)
            produtos_dual = stats_dual.get('produtos_unicos_dual', 0)
            
            print(f"   Total de registros na DUAL_produtos: {total_dual}")
            print(f"   Códigos únicos (id_externo): {codigos_dual}")
            print(f"   Produtos únicos (id_produto): {produtos_dual}")
            
            if codigos_dual > 0:
                taxa_dual = (total_dual / codigos_dual)
                print(f"   Média de registros por código: {taxa_dual:.1f}")
        else:
            print(f"   Erro: {resultado_dual.get('erro')}")
            return
        
        # 2. Verificar duplicatas em produtos usando códigos da DUAL
        print("\n2. DUPLICATAS EM PRODUTOS (CODIGOS DA DUAL_PRODUTOS):")
        query_duplicados = """
        SELECT 
            p.codigo_barras,
            COUNT(*) as total_produtos,
            COUNT(DISTINCT p.id_super) as id_supers_distintos,
            GROUP_CONCAT(DISTINCT p.id_super ORDER BY p.id_super) as lista_id_supers,
            GROUP_CONCAT(DISTINCT p.id ORDER BY p.created_at) as lista_ids_produtos,
            MIN(p.created_at) as primeiro_criado,
            MAX(p.created_at) as ultimo_criado
        FROM DUAL_produtos d
        INNER JOIN produtos p ON d.id_externo = p.codigo_barras
        WHERE d.id_externo IS NOT NULL AND d.id_externo != ''
        GROUP BY p.codigo_barras
        ORDER BY total_produtos DESC, p.codigo_barras
        LIMIT 20
        """
        
        resultado_dup = conectar_e_executar('integrafoods', query_duplicados)
        
        if resultado_dup.get('sucesso'):
            duplicados = resultado_dup.get('dados', [])
            print(f"   Primeiros 20 códigos da DUAL analisados:")
            
            sem_duplicatas = 0
            com_duplicatas = 0
            mesmo_id_super = 0
            id_supers_diferentes = 0
            
            for i, dup in enumerate(duplicados, 1):
                codigo = dup.get('codigo_barras')
                total = dup.get('total_produtos')
                id_supers_distintos = dup.get('id_supers_distintos')
                lista_supers = dup.get('lista_id_supers')
                lista_ids = dup.get('lista_ids_produtos')
                primeiro = dup.get('primeiro_criado')
                ultimo = dup.get('ultimo_criado')
                
                if total == 1:
                    sem_duplicatas += 1
                    status = "SEM duplicatas"
                else:
                    com_duplicatas += 1
                    if id_supers_distintos == 1:
                        mesmo_id_super += 1
                        status = f"{total} produtos - MESMO id_super ({lista_supers})"
                    else:
                        id_supers_diferentes += 1
                        status = f"{total} produtos - id_supers DIFERENTES ({lista_supers})"
                
                print(f"   {i:2d}. Código: {codigo} | {status}")
                if total > 1:
                    print(f"       IDs produtos: {lista_ids}")
                    print(f"       Período: {primeiro} até {ultimo}")
            
            print(f"\n   RESUMO DOS 20 CÓDIGOS ANALISADOS:")
            print(f"   - Códigos SEM duplicatas: {sem_duplicatas}")
            print(f"   - Códigos COM duplicatas: {com_duplicatas}")
            if com_duplicatas > 0:
                print(f"     - Duplicatas com MESMO id_super: {mesmo_id_super}")
                print(f"     - Duplicatas com id_supers DIFERENTES: {id_supers_diferentes}")
        else:
            print(f"   Erro: {resultado_dup.get('erro')}")
        
        # 3. Estatísticas gerais de cobertura
        print("\n3. COBERTURA GERAL (DUAL vs PRODUTOS):")
        query_cobertura = """
        SELECT 
            COUNT(DISTINCT d.id_externo) as codigos_dual,
            COUNT(DISTINCT p.codigo_barras) as codigos_produtos_encontrados,
            COUNT(DISTINCT CASE WHEN p.id_super = 131 THEN p.codigo_barras END) as codigos_produtos_131,
            COUNT(DISTINCT CASE WHEN p.id_super != 131 THEN p.codigo_barras END) as codigos_produtos_outros
        FROM DUAL_produtos d
        LEFT JOIN produtos p ON d.id_externo = p.codigo_barras
        WHERE d.id_externo IS NOT NULL AND d.id_externo != ''
        """
        
        resultado_cob = conectar_e_executar('integrafoods', query_cobertura)
        
        if resultado_cob.get('sucesso'):
            cob = resultado_cob.get('dados', [])[0]
            codigos_dual = cob.get('codigos_dual', 0)
            encontrados = cob.get('codigos_produtos_encontrados', 0)
            produtos_131 = cob.get('codigos_produtos_131', 0)
            produtos_outros = cob.get('codigos_produtos_outros', 0)
            
            print(f"   Códigos únicos na DUAL_produtos: {codigos_dual}")
            print(f"   Códigos encontrados em produtos: {encontrados}")
            print(f"   Códigos em produtos (id_super = 131): {produtos_131}")
            print(f"   Códigos em produtos (outros id_super): {produtos_outros}")
            
            if codigos_dual > 0:
                cobertura = (encontrados / codigos_dual) * 100
                cobertura_131 = (produtos_131 / codigos_dual) * 100
                print(f"   Cobertura total: {cobertura:.1f}%")
                print(f"   Cobertura id_super = 131: {cobertura_131:.1f}%")
        else:
            print(f"   Erro: {resultado_cob.get('erro')}")
            
    except Exception as e:
        print(f"Erro durante análise: {e}")

def analisar_produtos_sem_dual():
    """
    Analisa produtos que não estão na DUAL_produtos
    """
    print("\n=== PRODUTOS NAO PRESENTES NA DUAL_PRODUTOS ===")
    
    try:
        # Produtos que não têm correspondência na DUAL
        query_sem_dual = """
        SELECT 
            p.id_super,
            COUNT(*) as total_produtos,
            COUNT(DISTINCT p.codigo_barras) as codigos_unicos,
            (COUNT(*) - COUNT(DISTINCT p.codigo_barras)) as produtos_duplicados
        FROM produtos p
        LEFT JOIN DUAL_produtos d ON p.codigo_barras = d.id_externo
        WHERE p.codigo_barras IS NOT NULL 
        AND p.codigo_barras != ''
        AND d.id_externo IS NULL
        GROUP BY p.id_super
        ORDER BY total_produtos DESC
        """
        
        resultado_sem = conectar_e_executar('integrafoods', query_sem_dual)
        
        if resultado_sem.get('sucesso'):
            sem_dual = resultado_sem.get('dados', [])
            print(f"\n1. PRODUTOS SEM CORRESPONDENCIA NA DUAL_PRODUTOS:")
            
            if sem_dual:
                total_sem_dual = 0
                for item in sem_dual:
                    id_super = item.get('id_super')
                    total = item.get('total_produtos')
                    unicos = item.get('codigos_unicos')
                    duplicados = item.get('produtos_duplicados')
                    total_sem_dual += total
                    
                    taxa_dup = (duplicados / total * 100) if total > 0 else 0
                    print(f"   id_super {id_super}: {total} produtos | {unicos} únicos | {duplicados} duplicados ({taxa_dup:.1f}%)")
                
                print(f"\n   Total de produtos SEM correspondência na DUAL: {total_sem_dual}")
            else:
                print(f"   Todos os produtos têm correspondência na DUAL_produtos")
        else:
            print(f"   Erro: {resultado_sem.get('erro')}")
        
        # Exemplos de produtos sem DUAL
        query_exemplos_sem = """
        SELECT 
            p.id,
            p.nome,
            p.codigo_barras,
            p.id_super,
            p.status,
            p.created_at
        FROM produtos p
        LEFT JOIN DUAL_produtos d ON p.codigo_barras = d.id_externo
        WHERE p.codigo_barras IS NOT NULL 
        AND p.codigo_barras != ''
        AND d.id_externo IS NULL
        ORDER BY p.created_at DESC
        LIMIT 10
        """
        
        resultado_ex_sem = conectar_e_executar('integrafoods', query_exemplos_sem)
        
        if resultado_ex_sem.get('sucesso'):
            exemplos_sem = resultado_ex_sem.get('dados', [])
            print(f"\n2. EXEMPLOS DE PRODUTOS SEM DUAL (10 mais recentes):")
            
            for i, ex in enumerate(exemplos_sem, 1):
                produto_id = ex.get('id')
                nome = ex.get('nome', 'N/A')[:50]
                codigo = ex.get('codigo_barras')
                id_super = ex.get('id_super')
                status = 'Ativo' if ex.get('status') == 1 else 'Inativo'
                created_at = ex.get('created_at')
                
                print(f"   {i:2d}. ID: {produto_id} | id_super: {id_super} | {status}")
                print(f"       Código: {codigo}")
                print(f"       Nome: {nome}")
                print(f"       Criado: {created_at}")
        else:
            print(f"   Erro: {resultado_ex_sem.get('erro')}")
            
    except Exception as e:
        print(f"Erro durante análise de produtos sem DUAL: {e}")

def resumo_final_duplicacao():
    """
    Gera resumo final sobre duplicação usando DUAL como referência
    """
    print("\n=== RESUMO FINAL DA DUPLICACAO ===")
    
    try:
        # Query consolidada para resumo
        query_resumo = """
        SELECT 
            'DUAL_produtos' as origem,
            COUNT(DISTINCT id_externo) as codigos_unicos,
            COUNT(*) as total_registros
        FROM DUAL_produtos
        WHERE id_externo IS NOT NULL AND id_externo != ''
        
        UNION ALL
        
        SELECT 
            'produtos (todos)' as origem,
            COUNT(DISTINCT codigo_barras) as codigos_unicos,
            COUNT(*) as total_registros
        FROM produtos
        WHERE codigo_barras IS NOT NULL AND codigo_barras != ''
        
        UNION ALL
        
        SELECT 
            'produtos (id_super=131)' as origem,
            COUNT(DISTINCT codigo_barras) as codigos_unicos,
            COUNT(*) as total_registros
        FROM produtos
        WHERE codigo_barras IS NOT NULL AND codigo_barras != ''
        AND id_super = 131
        
        UNION ALL
        
        SELECT 
            'produtos (outros id_super)' as origem,
            COUNT(DISTINCT codigo_barras) as codigos_unicos,
            COUNT(*) as total_registros
        FROM produtos
        WHERE codigo_barras IS NOT NULL AND codigo_barras != ''
        AND id_super != 131
        """
        
        resultado_resumo = conectar_e_executar('integrafoods', query_resumo)
        
        if resultado_resumo.get('sucesso'):
            resumo = resultado_resumo.get('dados', [])
            print(f"\n1. COMPARATIVO DE DUPLICACAO:")
            print(f"   {'Origem':<25} {'Códigos Únicos':<15} {'Total Registros':<15} {'Taxa Duplicação':<15}")
            print(f"   {'-'*70}")
            
            for item in resumo:
                origem = item.get('origem')
                unicos = item.get('codigos_unicos', 0)
                total = item.get('total_registros', 0)
                
                if unicos > 0:
                    taxa_dup = ((total - unicos) / total * 100) if total > 0 else 0
                    print(f"   {origem:<25} {unicos:<15} {total:<15} {taxa_dup:<14.1f}%")
        else:
            print(f"   Erro: {resultado_resumo.get('erro')}")
        
        print(f"\n2. CONCLUSOES:")
        print(f"   - DUAL_produtos serve como referência de produtos únicos")
        print(f"   - Duplicatas em produtos ocorrem por múltiplos id_super")
        print(f"   - Filtro 'id_super = 131' é essencial para dados atuais")
        print(f"   - Relacionamento produtos.codigo_barras = DUAL_produtos.id_externo")
        
        print(f"\n3. RECOMENDACOES:")
        print(f"   - Use DUAL_produtos para identificar produtos únicos")
        print(f"   - Sempre filtre produtos por 'id_super = 131'")
        print(f"   - Monitore produtos sem correspondência na DUAL")
        print(f"   - Considere DUAL_produtos como fonte de verdade para códigos")
            
    except Exception as e:
        print(f"Erro durante resumo final: {e}")

def main():
    """
    Função principal
    """
    try:
        # Analisar duplicados usando DUAL como referência
        analisar_duplicados_via_dual()
        
        # Analisar produtos que não estão na DUAL
        analisar_produtos_sem_dual()
        
        # Resumo final
        resumo_final_duplicacao()
        
        print("\n=== ANALISE CONCLUIDA ===")
        
    except Exception as e:
        print(f"Erro durante execução: {e}")

if __name__ == "__main__":
    main()