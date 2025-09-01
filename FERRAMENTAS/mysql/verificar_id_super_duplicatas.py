#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificar ID Super Duplicatas - MySQL Manager ELIS v2
Script para verificar se as duplicatas têm o mesmo id_super
"""

import sys
import os
from pathlib import Path

# Adicionar o diretorio mysql ao path
sys.path.insert(0, str(Path(__file__).parent))

from mysql_ai import conectar_e_executar
import json

def verificar_id_super_duplicatas():
    """
    Verifica se as duplicatas têm o mesmo id_super
    """
    print("=== VERIFICACAO DE ID_SUPER NAS DUPLICATAS ===")
    
    try:
        # 1. Analisar duplicatas por código de barras e seus id_super
        print("\n1. ANALISE DE ID_SUPER POR CODIGO DUPLICADO:")
        query_duplicatas = """
        SELECT 
            codigo_barras,
            COUNT(*) as total_produtos,
            COUNT(DISTINCT id_super) as id_supers_distintos,
            GROUP_CONCAT(DISTINCT id_super ORDER BY id_super) as lista_id_supers,
            GROUP_CONCAT(DISTINCT id ORDER BY id) as lista_ids_produtos
        FROM produtos
        WHERE codigo_barras IS NOT NULL 
        AND codigo_barras != ''
        GROUP BY codigo_barras
        HAVING COUNT(*) > 1
        ORDER BY total_produtos DESC, codigo_barras
        LIMIT 20
        """
        
        resultado_dup = conectar_e_executar('integrafoods', query_duplicatas)
        
        if resultado_dup.get('sucesso'):
            duplicatas = resultado_dup.get('dados', [])
            print(f"   Primeiras 20 duplicatas analisadas:")
            
            mesmo_id_super = 0
            id_supers_diferentes = 0
            
            for i, dup in enumerate(duplicatas, 1):
                codigo = dup.get('codigo_barras')
                total = dup.get('total_produtos')
                id_supers_distintos = dup.get('id_supers_distintos')
                lista_supers = dup.get('lista_id_supers')
                lista_ids = dup.get('lista_ids_produtos')
                
                status = "MESMO id_super" if id_supers_distintos == 1 else "id_supers DIFERENTES"
                
                print(f"   {i:2d}. Código: {codigo} | {total} produtos | {status}")
                print(f"       id_supers: {lista_supers}")
                print(f"       IDs produtos: {lista_ids}")
                
                if id_supers_distintos == 1:
                    mesmo_id_super += 1
                else:
                    id_supers_diferentes += 1
            
            print(f"\n   RESUMO:")
            print(f"   - Duplicatas com MESMO id_super: {mesmo_id_super}")
            print(f"   - Duplicatas com id_supers DIFERENTES: {id_supers_diferentes}")
            
            if len(duplicatas) > 0:
                percentual_mesmo = (mesmo_id_super / len(duplicatas)) * 100
                print(f"   - Percentual com mesmo id_super: {percentual_mesmo:.1f}%")
        else:
            print(f"   Erro: {resultado_dup.get('erro')}")
        
        # 2. Focar nos exemplos específicos mencionados
        print("\n2. ANALISE DOS EXEMPLOS ESPECIFICOS:")
        codigos_exemplo = ['000031000', '000069000', '000074000', '000075000', '000076000']
        
        for codigo in codigos_exemplo:
            query_exemplo = f"""
            SELECT 
                id,
                nome,
                codigo_barras,
                id_super,
                status,
                created_at,
                updated_at
            FROM produtos
            WHERE codigo_barras = '{codigo}'
            ORDER BY created_at
            """
            
            resultado_ex = conectar_e_executar('integrafoods', query_exemplo)
            
            if resultado_ex.get('sucesso'):
                produtos = resultado_ex.get('dados', [])
                print(f"\n   Código {codigo}:")
                
                id_supers = set()
                for j, produto in enumerate(produtos, 1):
                    produto_id = produto.get('id')
                    nome = produto.get('nome', 'N/A')[:40]
                    id_super = produto.get('id_super')
                    status = 'Ativo' if produto.get('status') == 1 else 'Inativo'
                    created_at = produto.get('created_at')
                    
                    id_supers.add(id_super)
                    
                    print(f"     {j}. ID: {produto_id} | id_super: {id_super} | {status}")
                    print(f"        Nome: {nome}")
                    print(f"        Criado: {created_at}")
                
                print(f"     id_supers únicos: {sorted(list(id_supers))}")
                print(f"     Mesmo id_super: {'SIM' if len(id_supers) == 1 else 'NAO'}")
            else:
                print(f"   Erro para código {codigo}: {resultado_ex.get('erro')}")
        
        # 3. Estatísticas gerais por id_super
        print("\n3. DISTRIBUICAO GERAL POR ID_SUPER:")
        query_distribuicao = """
        SELECT 
            id_super,
            COUNT(*) as total_produtos,
            COUNT(DISTINCT codigo_barras) as codigos_unicos,
            (COUNT(*) - COUNT(DISTINCT codigo_barras)) as produtos_duplicados
        FROM produtos
        WHERE codigo_barras IS NOT NULL AND codigo_barras != ''
        GROUP BY id_super
        ORDER BY total_produtos DESC
        """
        
        resultado_dist = conectar_e_executar('integrafoods', query_distribuicao)
        
        if resultado_dist.get('sucesso'):
            distribuicao = resultado_dist.get('dados', [])
            print(f"   Distribuição por id_super:")
            
            for item in distribuicao:
                id_super = item.get('id_super')
                total = item.get('total_produtos')
                unicos = item.get('codigos_unicos')
                duplicados = item.get('produtos_duplicados')
                
                if duplicados > 0:
                    taxa_dup = (duplicados / total) * 100
                    print(f"     id_super {id_super}: {total} produtos | {unicos} únicos | {duplicados} duplicados ({taxa_dup:.1f}%)")
                else:
                    print(f"     id_super {id_super}: {total} produtos | {unicos} únicos | SEM duplicatas")
        else:
            print(f"   Erro: {resultado_dist.get('erro')}")
            
    except Exception as e:
        print(f"Erro durante verificacao: {e}")

def analisar_novos_produtos():
    """
    Analisa os produtos mais recentes para identificar padrões
    """
    print("\n=== ANALISE DOS PRODUTOS MAIS RECENTES ===")
    
    try:
        # Verificar produtos criados recentemente
        query_recentes = """
        SELECT 
            id,
            nome,
            codigo_barras,
            id_super,
            status,
            created_at
        FROM produtos
        WHERE created_at >= '2025-09-01'
        ORDER BY created_at DESC
        LIMIT 20
        """
        
        resultado_rec = conectar_e_executar('integrafoods', query_recentes)
        
        if resultado_rec.get('sucesso'):
            recentes = resultado_rec.get('dados', [])
            print(f"\n1. PRODUTOS CRIADOS A PARTIR DE 01/09/2025:")
            print(f"   Total encontrados: {len(recentes)}")
            
            if recentes:
                print(f"   Primeiros produtos:")
                
                id_supers_recentes = {}
                codigos_recentes = {}
                
                for i, produto in enumerate(recentes, 1):
                    produto_id = produto.get('id')
                    nome = produto.get('nome', 'N/A')[:40]
                    codigo = produto.get('codigo_barras')
                    id_super = produto.get('id_super')
                    status = 'Ativo' if produto.get('status') == 1 else 'Inativo'
                    created_at = produto.get('created_at')
                    
                    # Contar id_supers
                    id_supers_recentes[id_super] = id_supers_recentes.get(id_super, 0) + 1
                    
                    # Contar códigos
                    if codigo:
                        codigos_recentes[codigo] = codigos_recentes.get(codigo, 0) + 1
                    
                    print(f"     {i:2d}. ID: {produto_id} | id_super: {id_super} | {status}")
                    print(f"         Código: {codigo}")
                    print(f"         Nome: {nome}")
                    print(f"         Criado: {created_at}")
                
                print(f"\n   DISTRIBUICAO DOS PRODUTOS RECENTES:")
                print(f"   Por id_super:")
                for id_super, count in sorted(id_supers_recentes.items()):
                    print(f"     id_super {id_super}: {count} produtos")
                
                print(f"\n   Códigos de barras duplicados nos recentes:")
                duplicados_recentes = {k: v for k, v in codigos_recentes.items() if v > 1}
                if duplicados_recentes:
                    for codigo, count in sorted(duplicados_recentes.items()):
                        print(f"     {codigo}: {count} produtos")
                else:
                    print(f"     Nenhum código duplicado encontrado nos produtos recentes")
        else:
            print(f"   Erro: {resultado_rec.get('erro')}")
            
    except Exception as e:
        print(f"Erro durante analise de produtos recentes: {e}")

def main():
    """
    Função principal
    """
    try:
        # Verificar id_super nas duplicatas
        verificar_id_super_duplicatas()
        
        # Analisar produtos recentes
        analisar_novos_produtos()
        
        print("\n=== CONCLUSOES ===")
        print("\n1. PADRAO DE ID_SUPER:")
        print("   - Verificar se duplicatas mantêm o mesmo id_super")
        print("   - Identificar se novos produtos seguem padrão existente")
        
        print("\n2. IMPACTO DA INTEGRACAO:")
        print("   - Analisar se novos produtos são criados com id_super correto")
        print("   - Verificar se processo respeita produtos existentes")
        
        print("\n3. RECOMENDACOES:")
        print("   - Produtos duplicados devem manter mesmo id_super")
        print("   - Processo de integração deve verificar existência antes de criar")
        print("   - Considerar UPDATE ao invés de INSERT para produtos existentes")
        
        print("\n=== ANALISE CONCLUIDA ===")
        
    except Exception as e:
        print(f"Erro durante execução: {e}")

if __name__ == "__main__":
    main()