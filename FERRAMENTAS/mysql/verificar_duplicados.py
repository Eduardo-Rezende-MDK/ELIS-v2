#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificar Duplicados - MySQL Manager ELIS v2
Script para verificar códigos de barras duplicados na tabela produtos
"""

import sys
import os
from pathlib import Path

# Adicionar o diretorio mysql ao path
sys.path.insert(0, str(Path(__file__).parent))

from mysql_ai import conectar_e_executar
import json

def verificar_codigos_duplicados():
    """
    Verifica se existem códigos de barras duplicados
    """
    print("=== VERIFICACAO DE CODIGOS DE BARRAS DUPLICADOS ===")
    
    try:
        # Query para encontrar códigos duplicados
        query = """
        SELECT codigo_barras, COUNT(*) as quantidade
        FROM produtos 
        WHERE codigo_barras IS NOT NULL AND codigo_barras != ''
        GROUP BY codigo_barras 
        HAVING COUNT(*) > 1
        ORDER BY quantidade DESC, codigo_barras
        """
        
        resultado = conectar_e_executar('integrafoods', query)
        
        if resultado.get('sucesso'):
            total_duplicados = resultado.get('total_registros', 0)
            print(f"Total de códigos de barras duplicados: {total_duplicados}")
            
            dados = resultado.get('dados', [])
            if dados:
                print(f"\nCódigos de barras com duplicatas:")
                print("-" * 60)
                
                total_produtos_afetados = 0
                for i, registro in enumerate(dados, 1):
                    codigo = registro.get('codigo_barras', 'N/A')
                    quantidade = registro.get('quantidade', 0)
                    total_produtos_afetados += quantidade
                    
                    print(f"{i}. Código: {codigo} - {quantidade} produtos")
                
                print(f"\nTotal de produtos com códigos duplicados: {total_produtos_afetados}")
                
                # Mostrar detalhes dos primeiros 5 códigos duplicados
                print(f"\n=== DETALHES DOS PRIMEIROS 5 CÓDIGOS DUPLICADOS ===")
                for i, registro in enumerate(dados[:5], 1):
                    codigo = registro.get('codigo_barras', 'N/A')
                    print(f"\n{i}. Código de barras: {codigo}")
                    
                    # Buscar produtos com este código
                    query_detalhes = f"""
                    SELECT id, nome, status, venda, id_marca, created_at, updated_at
                    FROM produtos 
                    WHERE codigo_barras = '{codigo}'
                    ORDER BY id
                    """
                    
                    detalhes = conectar_e_executar('integrafoods', query_detalhes)
                    if detalhes.get('sucesso') and detalhes.get('dados'):
                        produtos = detalhes.get('dados')
                        print(f"   Produtos encontrados:")
                        for j, produto in enumerate(produtos, 1):
                            nome = produto.get('nome', 'Nome não informado')[:50]
                            if len(produto.get('nome', '')) > 50:
                                nome += "..."
                            status = 'Ativo' if produto.get('status') == 1 else 'Inativo'
                            venda = 'Sim' if produto.get('venda') == 1 else 'Não'
                            
                            print(f"   {j}. ID: {produto.get('id')} - {nome}")
                            print(f"      Status: {status} | Venda: {venda} | Marca: {produto.get('id_marca')}")
                            print(f"      Criado: {produto.get('created_at')} | Atualizado: {produto.get('updated_at')}")
                
            else:
                print("\nNenhum código de barras duplicado encontrado!")
                print("Todos os códigos de barras são únicos na tabela produtos.")
                
        else:
            print(f"Erro na consulta: {resultado.get('erro', 'Erro desconhecido')}")
            
    except ImportError as e:
        print(f"Erro de importacao: {e}")
        print("Certifique-se de instalar: pip install mysql-connector-python")
    except Exception as e:
        print(f"Erro durante execucao: {e}")

def verificar_estatisticas_codigos():
    """
    Verifica estatísticas gerais dos códigos de barras
    """
    print(f"\n=== ESTATISTICAS GERAIS DOS CODIGOS DE BARRAS ===")
    
    try:
        # Total de produtos
        query_total = "SELECT COUNT(*) as total FROM produtos"
        resultado_total = conectar_e_executar('integrafoods', query_total)
        
        # Produtos com código de barras
        query_com_codigo = """
        SELECT COUNT(*) as com_codigo 
        FROM produtos 
        WHERE codigo_barras IS NOT NULL AND codigo_barras != ''
        """
        resultado_com_codigo = conectar_e_executar('integrafoods', query_com_codigo)
        
        # Produtos sem código de barras
        query_sem_codigo = """
        SELECT COUNT(*) as sem_codigo 
        FROM produtos 
        WHERE codigo_barras IS NULL OR codigo_barras = ''
        """
        resultado_sem_codigo = conectar_e_executar('integrafoods', query_sem_codigo)
        
        # Códigos únicos
        query_unicos = """
        SELECT COUNT(DISTINCT codigo_barras) as codigos_unicos 
        FROM produtos 
        WHERE codigo_barras IS NOT NULL AND codigo_barras != ''
        """
        resultado_unicos = conectar_e_executar('integrafoods', query_unicos)
        
        if all(r.get('sucesso') for r in [resultado_total, resultado_com_codigo, resultado_sem_codigo, resultado_unicos]):
            total = resultado_total['dados'][0]['total']
            com_codigo = resultado_com_codigo['dados'][0]['com_codigo']
            sem_codigo = resultado_sem_codigo['dados'][0]['sem_codigo']
            unicos = resultado_unicos['dados'][0]['codigos_unicos']
            
            print(f"Total de produtos: {total}")
            print(f"Produtos com código de barras: {com_codigo} ({com_codigo/total*100:.1f}%)")
            print(f"Produtos sem código de barras: {sem_codigo} ({sem_codigo/total*100:.1f}%)")
            print(f"Códigos de barras únicos: {unicos}")
            
            if com_codigo > unicos:
                duplicatas = com_codigo - unicos
                print(f"Produtos com códigos duplicados: {duplicatas} ({duplicatas/total*100:.1f}%)")
            else:
                print("Todos os códigos de barras são únicos!")
                
    except Exception as e:
        print(f"Erro ao obter estatísticas: {e}")

def main():
    """
    Funcao principal
    """
    try:
        verificar_codigos_duplicados()
        verificar_estatisticas_codigos()
        
        print("\n=== VERIFICACAO CONCLUIDA ===")
        
    except Exception as e:
        print(f"Erro durante execucao: {e}")

if __name__ == "__main__":
    main()