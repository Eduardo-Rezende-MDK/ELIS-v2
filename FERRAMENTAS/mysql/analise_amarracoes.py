#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analise de Amarracoes - MySQL Manager ELIS v2
Script para analisar amarracoes entre tabelas usando codigo_barras 000031000
"""

import sys
import os
from pathlib import Path

# Adicionar o diretorio mysql ao path
sys.path.insert(0, str(Path(__file__).parent))

from mysql_ai import conectar_e_executar
import json

def analisar_amarracoes_produto(codigo_barras='000031000'):
    """
    Analisa as amarracoes entre as tabelas para um codigo de barras especifico
    
    Args:
        codigo_barras: Codigo de barras para analisar (padrao: 000031000)
    """
    print(f"=== ANALISE DE AMARRACOES PARA CODIGO {codigo_barras} ===")
    
    try:
        # 1. Analisar tabela produtos
        print("\n1. TABELA PRODUTOS:")
        query_produtos = f"""
        SELECT id, nome, codigo_barras, status, venda, id_marca, id_menus_sub, 
               qtd_embalagem, created_at, updated_at
        FROM produtos 
        WHERE codigo_barras = '{codigo_barras}'
        ORDER BY id
        """
        
        resultado_produtos = conectar_e_executar('integrafoods', query_produtos)
        
        if resultado_produtos.get('sucesso'):
            produtos = resultado_produtos.get('dados', [])
            print(f"   Produtos encontrados: {len(produtos)}")
            
            produto_ids = []
            for i, produto in enumerate(produtos, 1):
                produto_id = produto.get('id')
                produto_ids.append(produto_id)
                print(f"   {i}. ID: {produto_id} - {produto.get('nome', 'N/A')[:50]}")
                print(f"      Status: {'Ativo' if produto.get('status') == 1 else 'Inativo'}")
                print(f"      Venda: {'Sim' if produto.get('venda') == 1 else 'Nao'}")
                print(f"      Marca: {produto.get('id_marca')}")
                print(f"      Criado: {produto.get('created_at')}")
                print()
        else:
            print(f"   Erro: {resultado_produtos.get('erro', 'Desconhecido')}")
            return
        
        # 2. Analisar tabela precos
        print("\n2. TABELA PRECOS:")
        if produto_ids:
            ids_str = ','.join(map(str, produto_ids))
            query_precos = f"""
            SELECT id_produto, id_super, preco, estoque, estoque_real, 
                   data_validade, created_at, updated_at
            FROM precos 
            WHERE id_produto IN ({ids_str})
            ORDER BY id_produto, updated_at DESC
            """
            
            resultado_precos = conectar_e_executar('integrafoods', query_precos)
            
            if resultado_precos.get('sucesso'):
                precos = resultado_precos.get('dados', [])
                print(f"   Registros de precos encontrados: {len(precos)}")
                
                for preco in precos:
                    print(f"   ID Produto: {preco.get('id_produto')}")
                    print(f"   ID Super: {preco.get('id_super')}")
                    print(f"   Preco: R$ {preco.get('preco', 0):.2f}")
                    print(f"   Estoque: {preco.get('estoque', 0):.3f}")
                    print(f"   Estoque Real: {preco.get('estoque_real', 0):.3f}")
                    print(f"   Validade: {preco.get('data_validade')}")
                    print(f"   Atualizado: {preco.get('updated_at')}")
                    print()
            else:
                print(f"   Erro: {resultado_precos.get('erro', 'Desconhecido')}")
        
        # 3. Analisar tabela img_produto
        print("\n3. TABELA IMG_PRODUTO:")
        if produto_ids:
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
                    print(f"   ID Produto: {img.get('id_produto')}")
                    print(f"   Imagem: {img.get('img', 'N/A')[:60]}...")
                    print(f"   Imagem Old: {img.get('img_old', 'N/A')[:60]}...")
                    print(f"   Principal: {'Sim' if img.get('principal') == 1 else 'Nao'}")
                    print(f"   ID Super: {img.get('id_super')}")
                    print(f"   ID User: {img.get('id_user')}")
                    print()
            else:
                print(f"   Erro: {resultado_imagens.get('erro', 'Desconhecido')}")
        
        # 4. Analisar tabela DUAL_produtos
        print("\n4. TABELA DUAL_PRODUTOS:")
        if produto_ids:
            query_dual = f"""
            SELECT id_produto, id_externo, nome, descricao, preco, 
                   estoque, ativo, data_atualizacao, categoria, marca
            FROM DUAL_produtos 
            WHERE id_produto IN ({ids_str})
            ORDER BY data_atualizacao
            """
            
            resultado_dual = conectar_e_executar('integrafoods', query_dual)
            
            if resultado_dual.get('sucesso'):
                duplicacoes = resultado_dual.get('dados', [])
                print(f"   Registros de duplicacao encontrados: {len(duplicacoes)}")
                
                for dup in duplicacoes:
                    print(f"   ID Produto: {dup.get('id_produto')}")
                    print(f"   ID Externo: {dup.get('id_externo')}")
                    print(f"   Nome: {dup.get('nome', 'N/A')[:50]}")
                    print(f"   Preco: R$ {dup.get('preco', 'N/A')}")
                    print(f"   Estoque: {dup.get('estoque', 'N/A')}")
                    print(f"   Ativo: {dup.get('ativo', 'N/A')}")
                    print(f"   Categoria: {dup.get('categoria', 'N/A')}")
                    print(f"   Marca: {dup.get('marca', 'N/A')}")
                    print(f"   Atualizado: {dup.get('data_atualizacao')}")
                    print()
            else:
                print(f"   Erro: {resultado_dual.get('erro', 'Desconhecido')}")
        
        # 5. Resumo da analise
        print("\n=== RESUMO DA ANALISE ===")
        print(f"Codigo de barras analisado: {codigo_barras}")
        print(f"Total de produtos: {len(produtos) if 'produtos' in locals() else 0}")
        print(f"Total de precos: {len(precos) if 'precos' in locals() else 0}")
        print(f"Total de imagens: {len(imagens) if 'imagens' in locals() else 0}")
        print(f"Total de duplicacoes: {len(duplicacoes) if 'duplicacoes' in locals() else 0}")
        
        # Verificar se ha inconsistencias
        if 'produtos' in locals() and len(produtos) > 1:
            print(f"\nALERTA: {len(produtos)} produtos com mesmo codigo de barras!")
            print("Possivel problema de integridade de dados.")
        
    except Exception as e:
        print(f"Erro durante analise: {e}")

def analisar_estrutura_tabelas():
    """
    Analisa a estrutura das tabelas para entender os relacionamentos
    """
    print("\n=== ESTRUTURA DAS TABELAS ===")
    
    tabelas = ['produtos', 'precos', 'img_produto', 'DUAL_produtos']
    
    for tabela in tabelas:
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
                print(f"  {campo}: {tipo} {'(PK)' if chave == 'PRI' else ''}{'(NOT NULL)' if nulo == 'NO' else ''}")
        else:
            print(f"  Erro ao obter estrutura: {resultado.get('erro', 'Desconhecido')}")

def main():
    """
    Funcao principal
    """
    try:
        # Analisar estrutura das tabelas
        analisar_estrutura_tabelas()
        
        # Analisar amarracoes para o codigo especifico
        analisar_amarracoes_produto('000031000')
        
        print("\n=== ANALISE CONCLUIDA ===")
        
    except Exception as e:
        print(f"Erro durante execucao: {e}")

if __name__ == "__main__":
    main()