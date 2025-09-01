#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Recuperar IA Ajuste - MySQL Manager ELIS v2
Script para recuperar dados da dinamica_ia_ajuste considerando duplicacao de produtos
"""

import sys
import os
from pathlib import Path

# Adicionar o diretorio mysql ao path
sys.path.insert(0, str(Path(__file__).parent))

from mysql_ai import conectar_e_executar
import json

def analisar_problema_ia_ajuste(codigo_barras='000031000'):
    """
    Analisa o problema de recuperacao de dados da dinamica_ia_ajuste
    considerando produtos duplicados
    
    Args:
        codigo_barras: Codigo de barras para analisar
    """
    print(f"=== PROBLEMA DE RECUPERACAO IA_AJUSTE - CODIGO {codigo_barras} ===")
    
    try:
        # 1. Identificar produtos duplicados
        print("\n1. PRODUTOS DUPLICADOS:")
        query_produtos = f"""
        SELECT id, nome, codigo_barras, status, id_super, created_at, updated_at
        FROM produtos 
        WHERE codigo_barras = '{codigo_barras}'
        ORDER BY created_at
        """
        
        resultado_produtos = conectar_e_executar('integrafoods', query_produtos)
        
        if not resultado_produtos.get('sucesso'):
            print(f"Erro: {resultado_produtos.get('erro')}")
            return
        
        produtos = resultado_produtos.get('dados', [])
        print(f"Total de produtos duplicados: {len(produtos)}")
        
        produto_ids = []
        for i, produto in enumerate(produtos, 1):
            produto_id = produto.get('id')
            produto_ids.append(produto_id)
            print(f"  {i}. ID: {produto_id} | Super: {produto.get('id_super')} | Status: {'Ativo' if produto.get('status') == 1 else 'Inativo'}")
            print(f"     Nome: {produto.get('nome', 'N/A')[:60]}")
            print(f"     Criado: {produto.get('created_at')}")
        
        # 2. Verificar dados na dinamica_ia_ajuste
        print("\n2. DADOS NA DINAMICA_IA_AJUSTE:")
        if produto_ids:
            ids_str = ','.join(map(str, produto_ids))
            query_ia_ajuste = f"""
            SELECT id, id_produto, titulo, desc, curta
            FROM dinamica_ia_ajuste 
            WHERE id_produto IN ({ids_str})
            ORDER BY id_produto
            """
            
            resultado_ia = conectar_e_executar('integrafoods', query_ia_ajuste)
            
            if resultado_ia.get('sucesso'):
                dados_ia = resultado_ia.get('dados', [])
                print(f"Registros encontrados na IA_AJUSTE: {len(dados_ia)}")
                
                for i, registro in enumerate(dados_ia, 1):
                    print(f"\n  {i}. ID IA: {registro.get('id')} | ID Produto: {registro.get('id_produto')}")
                    print(f"     Titulo: {registro.get('titulo', 'N/A')[:60]}")
                    print(f"     Desc: {registro.get('desc', 'N/A')[:80]}")
                    print(f"     Curta: {registro.get('curta', 'N/A')[:60]}")
            else:
                print(f"Erro: {resultado_ia.get('erro')}")
        
        return produto_ids, dados_ia if 'dados_ia' in locals() else []
        
    except Exception as e:
        print(f"Erro durante analise: {e}")
        return [], []

def estrategias_recuperacao(codigo_barras='000031000'):
    """
    Apresenta estrategias para recuperar dados da IA_AJUSTE
    
    Args:
        codigo_barras: Codigo de barras para analisar
    """
    print(f"\n=== ESTRATEGIAS DE RECUPERACAO - CODIGO {codigo_barras} ===")
    
    try:
        # ESTRATEGIA 1: Usar codigo_barras como ponte
        print("\nESTRATEGIA 1: Usar codigo_barras como ponte")
        query_estrategia1 = f"""
        SELECT 
            p.codigo_barras,
            p.id as produto_id,
            p.nome as produto_nome,
            p.status,
            p.id_super,
            ia.id as ia_id,
            ia.titulo,
            ia.desc,
            ia.curta
        FROM produtos p
        LEFT JOIN dinamica_ia_ajuste ia ON p.id = ia.id_produto
        WHERE p.codigo_barras = '{codigo_barras}'
        ORDER BY p.created_at, ia.id
        """
        
        resultado1 = conectar_e_executar('integrafoods', query_estrategia1)
        
        if resultado1.get('sucesso'):
            dados1 = resultado1.get('dados', [])
            print(f"Registros encontrados: {len(dados1)}")
            
            com_ia = [d for d in dados1 if d.get('ia_id')]
            sem_ia = [d for d in dados1 if not d.get('ia_id')]
            
            print(f"  Produtos COM dados IA: {len(com_ia)}")
            print(f"  Produtos SEM dados IA: {len(sem_ia)}")
            
            if com_ia:
                print("\n  Produtos com dados IA:")
                for item in com_ia:
                    print(f"    ID Produto: {item.get('produto_id')} | Super: {item.get('id_super')} | Status: {'Ativo' if item.get('status') == 1 else 'Inativo'}")
                    print(f"    Titulo IA: {item.get('titulo', 'N/A')[:50]}")
        else:
            print(f"Erro: {resultado1.get('erro')}")
        
        # ESTRATEGIA 2: Buscar por similaridade de nome
        print("\nESTRATEGIA 2: Buscar por similaridade de nome")
        
        # Primeiro, pegar um nome de produto para buscar similares
        if 'dados1' in locals() and dados1:
            nome_referencia = dados1[0].get('produto_nome', '')
            if nome_referencia:
                # Extrair palavras-chave do nome
                palavras = nome_referencia.split()[:3]  # Primeiras 3 palavras
                if palavras:
                    palavra_chave = palavras[0]
                    
                    query_estrategia2 = f"""
                    SELECT 
                        p.id as produto_id,
                        p.nome,
                        p.codigo_barras,
                        p.status,
                        ia.titulo,
                        ia.desc
                    FROM produtos p
                    INNER JOIN dinamica_ia_ajuste ia ON p.id = ia.id_produto
                    WHERE p.nome LIKE '%{palavra_chave}%'
                    AND p.codigo_barras = '{codigo_barras}'
                    ORDER BY p.created_at DESC
                    LIMIT 5
                    """
                    
                    resultado2 = conectar_e_executar('integrafoods', query_estrategia2)
                    
                    if resultado2.get('sucesso'):
                        dados2 = resultado2.get('dados', [])
                        print(f"Registros similares encontrados: {len(dados2)}")
                        
                        for item in dados2:
                            print(f"    ID: {item.get('produto_id')} - {item.get('nome', 'N/A')[:40]}")
                            print(f"    Titulo IA: {item.get('titulo', 'N/A')[:50]}")
                    else:
                        print(f"Erro: {resultado2.get('erro')}")
        
        # ESTRATEGIA 3: Priorizar por status e data
        print("\nESTRATEGIA 3: Priorizar por status e data (mais recente ativo)")
        query_estrategia3 = f"""
        SELECT 
            p.id as produto_id,
            p.nome,
            p.status,
            p.id_super,
            p.created_at,
            ia.titulo,
            ia.desc,
            ia.curta
        FROM produtos p
        LEFT JOIN dinamica_ia_ajuste ia ON p.id = ia.id_produto
        WHERE p.codigo_barras = '{codigo_barras}'
        ORDER BY 
            p.status DESC,  -- Ativos primeiro
            p.created_at DESC,  -- Mais recentes primeiro
            ia.id DESC  -- IA mais recente
        LIMIT 1
        """
        
        resultado3 = conectar_e_executar('integrafoods', query_estrategia3)
        
        if resultado3.get('sucesso'):
            dados3 = resultado3.get('dados', [])
            if dados3:
                melhor = dados3[0]
                print(f"Melhor candidato:")
                print(f"  ID Produto: {melhor.get('produto_id')}")
                print(f"  Nome: {melhor.get('nome', 'N/A')[:50]}")
                print(f"  Status: {'Ativo' if melhor.get('status') == 1 else 'Inativo'}")
                print(f"  Super: {melhor.get('id_super')}")
                print(f"  Criado: {melhor.get('created_at')}")
                print(f"  Titulo IA: {melhor.get('titulo', 'SEM DADOS IA')[:50]}")
                
                if melhor.get('titulo'):
                    print(f"\n  DADOS IA ENCONTRADOS:")
                    print(f"    Titulo: {melhor.get('titulo', 'N/A')}")
                    print(f"    Desc: {melhor.get('desc', 'N/A')[:100]}")
                    print(f"    Curta: {melhor.get('curta', 'N/A')[:80]}")
                else:
                    print(f"\n  PRODUTO SEM DADOS IA - Necessario gerar")
        else:
            print(f"Erro: {resultado3.get('erro')}")
            
    except Exception as e:
        print(f"Erro durante estrategias: {e}")

def query_recuperacao_otimizada(codigo_barras='000031000'):
    """
    Gera query otimizada para recuperar dados da IA_AJUSTE
    
    Args:
        codigo_barras: Codigo de barras para gerar query
    """
    print(f"\n=== QUERY OTIMIZADA PARA RECUPERACAO ===")
    
    print("\nQuery recomendada para recuperar dados IA_AJUSTE:")
    print(f"""
    -- Query para recuperar dados IA considerando duplicacao
    SELECT 
        p.codigo_barras,
        p.id as produto_id,
        p.nome as produto_nome,
        p.status,
        p.id_super,
        p.created_at,
        ia.id as ia_id,
        ia.titulo,
        ia.desc,
        ia.curta,
        -- Ranking para priorizar
        ROW_NUMBER() OVER (
            PARTITION BY p.codigo_barras 
            ORDER BY 
                p.status DESC,  -- Ativos primeiro
                p.created_at DESC,  -- Mais recentes
                ia.id DESC  -- IA mais recente
        ) as ranking
    FROM produtos p
    LEFT JOIN dinamica_ia_ajuste ia ON p.id = ia.id_produto
    WHERE p.codigo_barras = '{codigo_barras}'
    ORDER BY ranking
    LIMIT 1;
    """)
    
    print("\nQuery para recuperar TODOS os dados IA de um codigo:")
    print(f"""
    -- Query para ver todos os dados IA de um codigo
    SELECT 
        p.codigo_barras,
        p.id as produto_id,
        p.nome,
        p.status,
        p.id_super,
        ia.titulo,
        ia.desc,
        ia.curta
    FROM produtos p
    INNER JOIN dinamica_ia_ajuste ia ON p.id = ia.id_produto
    WHERE p.codigo_barras = '{codigo_barras}'
    ORDER BY p.status DESC, p.created_at DESC;
    """)
    
    print("\nQuery para consolidar dados IA (remover duplicatas):")
    print(f"""
    -- Query para consolidar dados IA únicos por codigo_barras
    WITH dados_ia_unicos AS (
        SELECT 
            p.codigo_barras,
            ia.titulo,
            ia.desc,
            ia.curta,
            ROW_NUMBER() OVER (
                PARTITION BY p.codigo_barras, ia.titulo 
                ORDER BY p.status DESC, p.created_at DESC
            ) as rn
        FROM produtos p
        INNER JOIN dinamica_ia_ajuste ia ON p.id = ia.id_produto
        WHERE p.codigo_barras = '{codigo_barras}'
    )
    SELECT codigo_barras, titulo, desc, curta
    FROM dados_ia_unicos 
    WHERE rn = 1;
    """)

def main():
    """
    Funcao principal
    """
    try:
        # Analisar o problema
        produto_ids, dados_ia = analisar_problema_ia_ajuste('000031000')
        
        # Apresentar estrategias
        estrategias_recuperacao('000031000')
        
        # Gerar queries otimizadas
        query_recuperacao_otimizada('000031000')
        
        print("\n=== RESUMO DAS SOLUCOES ===")
        print("\n1. PROBLEMA IDENTIFICADO:")
        print("   - Produtos duplicados com mesmo codigo_barras")
        print("   - dinamica_ia_ajuste usa id_produto (afetado pela duplicacao)")
        print("   - Alguns produtos podem ter dados IA, outros nao")
        
        print("\n2. SOLUCOES RECOMENDADAS:")
        print("   A) Usar codigo_barras como ponte para encontrar dados IA")
        print("   B) Priorizar produtos ativos e mais recentes")
        print("   C) Consolidar dados IA únicos por codigo_barras")
        print("   D) Implementar ranking para escolher melhor candidato")
        
        print("\n3. IMPLEMENTACAO:")
        print("   - Use as queries otimizadas fornecidas")
        print("   - Considere criar view para facilitar acesso")
        print("   - Monitore produtos sem dados IA para geracao")
        
    except Exception as e:
        print(f"Erro durante execucao: {e}")

if __name__ == "__main__":
    main()