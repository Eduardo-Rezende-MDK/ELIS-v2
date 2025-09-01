#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analise Duplicados Melhorada - MySQL Manager ELIS v2
Analise focada no problema de duplicados com amarracoes corretas
"""

import sys
import os
from pathlib import Path

# Adicionar o diretorio mysql ao path
sys.path.insert(0, str(Path(__file__).parent))

from mysql_ai import conectar_e_executar
import json

def analisar_duplicados_completo(codigo_barras='000031000'):
    """
    Analise completa do problema de duplicados
    
    Estrutura correta:
    - produtos: dados base
    - precos: informacao de estoque
    - DUAL_produtos: precos
    - img_produto: imagens
    
    Args:
        codigo_barras: Codigo de barras para analisar
    """
    print(f"=== ANALISE COMPLETA DE DUPLICADOS - CODIGO {codigo_barras} ===")
    
    try:
        # 1. PRODUTOS - Dados base
        print("\n1. PRODUTOS (Dados Base):")
        query_produtos = f"""
        SELECT id, nome, codigo_barras, status, venda, id_marca, id_menus_sub, 
               qtd_embalagem, id_super, created_at, updated_at
        FROM produtos 
        WHERE codigo_barras = '{codigo_barras}'
        ORDER BY created_at
        """
        
        resultado_produtos = conectar_e_executar('integrafoods', query_produtos)
        
        if not resultado_produtos.get('sucesso'):
            print(f"   Erro: {resultado_produtos.get('erro')}")
            return
        
        produtos = resultado_produtos.get('dados', [])
        print(f"   Total de produtos duplicados: {len(produtos)}")
        
        produto_ids = []
        for i, produto in enumerate(produtos, 1):
            produto_id = produto.get('id')
            produto_ids.append(produto_id)
            print(f"\n   {i}. ID: {produto_id}")
            print(f"      Nome: {produto.get('nome', 'N/A')[:60]}")
            print(f"      Status: {'Ativo' if produto.get('status') == 1 else 'Inativo'}")
            print(f"      Venda: {'Sim' if produto.get('venda') == 1 else 'Nao'}")
            print(f"      Marca: {produto.get('id_marca')}")
            print(f"      Super: {produto.get('id_super')}")
            print(f"      Criado: {produto.get('created_at')}")
            print(f"      Atualizado: {produto.get('updated_at')}")
        
        if not produto_ids:
            print("   Nenhum produto encontrado")
            return
        
        # 2. PRECOS - Informacao de estoque
        print("\n2. PRECOS (Informacao de Estoque):")
        ids_str = ','.join(map(str, produto_ids))
        query_precos = f"""
        SELECT id_produto, id_super, preco, estoque, estoque_real, 
               data_validade, updated_at
        FROM precos 
        WHERE id_produto IN ({ids_str})
        ORDER BY id_produto, updated_at DESC
        """
        
        resultado_precos = conectar_e_executar('integrafoods', query_precos)
        
        if resultado_precos.get('sucesso'):
            precos = resultado_precos.get('dados', [])
            print(f"   Registros de estoque encontrados: {len(precos)}")
            
            for preco in precos:
                print(f"\n   ID Produto: {preco.get('id_produto')}")
                print(f"   ID Super: {preco.get('id_super')}")
                print(f"   Preco Tabela: R$ {float(preco.get('preco', 0)):.2f}")
                print(f"   Estoque: {float(preco.get('estoque', 0)):.3f}")
                print(f"   Estoque Real: {float(preco.get('estoque_real', 0)):.3f}")
                print(f"   Validade: {preco.get('data_validade')}")
                print(f"   Atualizado: {preco.get('updated_at')}")
        else:
            print(f"   Erro: {resultado_precos.get('erro')}")
        
        # 3. DUAL_PRODUTOS - Precos
        print("\n3. DUAL_PRODUTOS (Precos):")
        query_dual = f"""
        SELECT id_produto, id_externo, nome, preco, preco_promocional,
               estoque, ativo, data_atualizacao, categoria, marca
        FROM DUAL_produtos 
        WHERE id_produto IN ({ids_str})
        ORDER BY id_produto
        """
        
        resultado_dual = conectar_e_executar('integrafoods', query_dual)
        
        if resultado_dual.get('sucesso'):
            dual_produtos = resultado_dual.get('dados', [])
            print(f"   Registros de precos encontrados: {len(dual_produtos)}")
            
            for dual in dual_produtos:
                print(f"\n   ID Produto: {dual.get('id_produto')}")
                print(f"   ID Externo: {dual.get('id_externo')}")
                print(f"   Nome: {dual.get('nome', 'N/A')[:50]}")
                print(f"   Preco: R$ {dual.get('preco', 'N/A')}")
                print(f"   Preco Promocional: R$ {dual.get('preco_promocional', 'N/A')}")
                print(f"   Estoque: {dual.get('estoque', 'N/A')}")
                print(f"   Ativo: {dual.get('ativo', 'N/A')}")
                print(f"   Categoria: {dual.get('categoria', 'N/A')}")
                print(f"   Marca: {dual.get('marca', 'N/A')}")
                print(f"   Atualizado: {dual.get('data_atualizacao')}")
        else:
            print(f"   Erro: {resultado_dual.get('erro')}")
        
        # 4. IMG_PRODUTO - Imagens
        print("\n4. IMG_PRODUTO (Imagens):")
        query_imagens = f"""
        SELECT id_produto, img, img_old, principal, id_super, id_user
        FROM img_produto 
        WHERE id_produto IN ({ids_str})
        ORDER BY id_produto, principal DESC
        """
        
        resultado_imagens = conectar_e_executar('integrafoods', query_imagens)
        
        if resultado_imagens.get('sucesso'):
            imagens = resultado_imagens.get('dados', [])
            print(f"   Imagens encontradas: {len(imagens)}")
            
            for img in imagens:
                print(f"\n   ID Produto: {img.get('id_produto')}")
                img_path = img.get('img', 'N/A')
                img_old_path = img.get('img_old', 'N/A')
                print(f"   Imagem: {img_path[:50]}{'...' if len(str(img_path)) > 50 else ''}")
                print(f"   Imagem Old: {img_old_path[:50]}{'...' if len(str(img_old_path)) > 50 else ''}")
                print(f"   Principal: {'Sim' if img.get('principal') == 1 else 'Nao'}")
                print(f"   ID Super: {img.get('id_super')}")
                print(f"   ID User: {img.get('id_user')}")
        else:
            print(f"   Erro: {resultado_imagens.get('erro')}")
        
        # 5. ANALISE DO PROBLEMA DE DUPLICACAO
        print("\n=== ANALISE DO PROBLEMA DE DUPLICACAO ===")
        
        if len(produtos) > 1:
            print(f"PROBLEMA IDENTIFICADO: {len(produtos)} produtos com mesmo codigo de barras!")
            
            # Analisar padroes temporais
            datas_criacao = [p.get('created_at') for p in produtos if p.get('created_at')]
            if datas_criacao:
                print(f"\nPadrao temporal:")
                print(f"  Primeiro produto: {min(datas_criacao)}")
                print(f"  Ultimo produto: {max(datas_criacao)}")
            
            # Analisar status
            ativos = sum(1 for p in produtos if p.get('status') == 1)
            inativos = len(produtos) - ativos
            print(f"\nStatus dos produtos:")
            print(f"  Ativos: {ativos}")
            print(f"  Inativos: {inativos}")
            
            # Analisar id_super
            supers = set(p.get('id_super') for p in produtos if p.get('id_super'))
            print(f"\nID_Super diferentes: {len(supers)} ({list(supers)})")
            
            # Verificar se ha precos/estoques para todos
            produtos_com_preco = len(precos) if 'precos' in locals() else 0
            produtos_com_dual = len(dual_produtos) if 'dual_produtos' in locals() else 0
            produtos_com_img = len(imagens) if 'imagens' in locals() else 0
            
            print(f"\nCobertura de dados:")
            print(f"  Produtos com estoque (precos): {produtos_com_preco}/{len(produtos)}")
            print(f"  Produtos com precos (dual): {produtos_com_dual}/{len(produtos)}")
            print(f"  Produtos com imagens: {produtos_com_img}/{len(produtos)}")
            
            # Sugestoes
            print(f"\nSUGESTOES PARA CORRECAO:")
            if inativos > 0:
                print(f"  1. Considerar remover {inativos} produto(s) inativo(s)")
            if len(supers) > 1:
                print(f"  2. Unificar id_super (atualmente: {list(supers)})")
            if produtos_com_preco < len(produtos):
                print(f"  3. Verificar produtos sem estoque na tabela precos")
            if produtos_com_dual < len(produtos):
                print(f"  4. Verificar produtos sem precos na tabela DUAL_produtos")
        else:
            print("Nenhum problema de duplicacao encontrado.")
        
    except Exception as e:
        print(f"Erro durante analise: {e}")

def gerar_query_correcao(codigo_barras='000031000'):
    """
    Gera queries SQL para corrigir o problema de duplicacao
    """
    print(f"\n=== QUERIES PARA CORRECAO - CODIGO {codigo_barras} ===")
    
    print("\n1. Query para identificar produtos duplicados:")
    print(f"""
    SELECT id, nome, status, venda, created_at, updated_at
    FROM produtos 
    WHERE codigo_barras = '{codigo_barras}'
    ORDER BY created_at;
    """)
    
    print("\n2. Query para verificar relacionamentos:")
    print(f"""
    SELECT 
        p.id as produto_id,
        p.nome,
        p.status,
        pr.estoque,
        d.preco as preco_dual,
        i.img as tem_imagem
    FROM produtos p
    LEFT JOIN precos pr ON p.id = pr.id_produto
    LEFT JOIN DUAL_produtos d ON p.id = d.id_produto
    LEFT JOIN img_produto i ON p.id = i.id_produto AND i.principal = 1
    WHERE p.codigo_barras = '{codigo_barras}'
    ORDER BY p.created_at;
    """)
    
    print("\n3. Query para remover produtos inativos (CUIDADO - BACKUP ANTES):")
    print(f"""
    -- FAZER BACKUP ANTES DE EXECUTAR!
    DELETE FROM produtos 
    WHERE codigo_barras = '{codigo_barras}' 
    AND status = 0 
    AND venda = 0;
    """)

def main():
    """
    Funcao principal
    """
    try:
        # Analisar duplicados
        analisar_duplicados_completo('000031000')
        
        # Gerar queries de correcao
        gerar_query_correcao('000031000')
        
        print("\n=== ANALISE COMPLETA CONCLUIDA ===")
        
    except Exception as e:
        print(f"Erro durante execucao: {e}")

if __name__ == "__main__":
    main()