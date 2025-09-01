#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Consulta Super 131 - MySQL Manager ELIS v2
Script para consultar produtos com id_super = 131
"""

import sys
import os
from pathlib import Path

# Adicionar o diretorio mysql ao path
sys.path.insert(0, str(Path(__file__).parent))

from mysql_ai import conectar_e_executar
import json

def consultar_produtos_super_131():
    """
    Consulta produtos com id_super = 131 e verifica duplicatas de codigo_barras
    """
    print("=== PRODUTOS COM ID_SUPER = 131 ===")
    
    try:
        # Executar query
        query = "SELECT * FROM produtos WHERE id_super = 131"
        resultado = conectar_e_executar('integrafoods', query)
        
        # Query para verificar duplicatas de codigo_barras no id_super = 131
        query_duplicados = """
        SELECT codigo_barras, COUNT(*) as quantidade
        FROM produtos 
        WHERE id_super = 131 AND codigo_barras IS NOT NULL AND codigo_barras != ''
        GROUP BY codigo_barras 
        HAVING COUNT(*) > 1
        ORDER BY quantidade DESC, codigo_barras
        """
        resultado_duplicados = conectar_e_executar('integrafoods', query_duplicados)
        
        if resultado.get('sucesso'):
            total = resultado.get('total_registros', 0)
            print(f"Total de produtos encontrados: {total}")
            
            dados = resultado.get('dados', [])
            if dados:
                print(f"\nListagem dos {total} produtos:")
                print("-" * 80)
                
                for i, registro in enumerate(dados, 1):
                    print(f"\n{i}. {registro.get('nome', 'Nome nao informado')} (ID: {registro.get('id', 'N/A')})")
                    print(f"   Codigo de barras: {registro.get('codigo_barras', 'N/A')}")
                    print(f"   Status: {registro.get('status', 'N/A')} ({'Ativo' if registro.get('status') == 1 else 'Inativo'})")
                    print(f"   Venda: {registro.get('venda', 'N/A')} ({'Sim' if registro.get('venda') == 1 else 'Nao'})")
                    print(f"   Quantidade embalagem: {registro.get('qtd_embalagem', 'N/A')}")
                    print(f"   Marca ID: {registro.get('id_marca', 'N/A')}")
                    print(f"   Menu sub ID: {registro.get('id_menus_sub', 'N/A')}")
                    
                    # Mostrar segmentos se existir
                    segmentos = registro.get('segmentos', '')
                    if segmentos:
                        print(f"   Segmentos: {segmentos}")
                    
                    # Mostrar NCM se existir
                    ncm = registro.get('ncm', '')
                    if ncm:
                        print(f"   NCM: {ncm}")
                    
                    # Mostrar datas
                    created = registro.get('created_at', 'N/A')
                    updated = registro.get('updated_at', 'N/A')
                    print(f"   Criado em: {created}")
                    print(f"   Atualizado em: {updated}")
                    
                    if i < total:
                        print("-" * 40)
                        
            else:
                print("Nenhum produto encontrado com id_super = 131")
                
            # Estatisticas adicionais
            if dados:
                print(f"\n=== ESTATISTICAS ===")
                ativos = sum(1 for p in dados if p.get('status') == 1)
                inativos = sum(1 for p in dados if p.get('status') == 0)
                para_venda = sum(1 for p in dados if p.get('venda') == 1)
                
                print(f"Produtos ativos: {ativos}")
                print(f"Produtos inativos: {inativos}")
                print(f"Produtos para venda: {para_venda}")
                
                # Marcas mais comuns
                marcas = {}
                for produto in dados:
                    marca_id = produto.get('id_marca')
                    if marca_id:
                        marcas[marca_id] = marcas.get(marca_id, 0) + 1
                
                if marcas:
                    print(f"\nMarcas mais comuns:")
                    for marca_id, count in sorted(marcas.items(), key=lambda x: x[1], reverse=True)[:5]:
                        print(f"  Marca ID {marca_id}: {count} produtos")
            
            # Verificar duplicatas de codigo_barras
            print(f"\n=== VERIFICACAO DE CODIGOS DE BARRAS DUPLICADOS ===")
            if resultado_duplicados.get('sucesso'):
                duplicados = resultado_duplicados.get('dados', [])
                total_duplicados = resultado_duplicados.get('total_registros', 0)
                
                if duplicados:
                    print(f"Total de códigos de barras duplicados: {total_duplicados}")
                    
                    total_produtos_duplicados = 0
                    for dup in duplicados:
                        total_produtos_duplicados += dup.get('quantidade', 0)
                    
                    print(f"Total de produtos com códigos duplicados: {total_produtos_duplicados}")
                    print(f"Percentual de produtos com códigos duplicados: {total_produtos_duplicados/total*100:.1f}%")
                    
                    print(f"\nPrimeiros 10 códigos duplicados:")
                    for i, dup in enumerate(duplicados[:10], 1):
                        codigo = dup.get('codigo_barras', 'N/A')
                        quantidade = dup.get('quantidade', 0)
                        print(f"  {i}. Código: {codigo} - {quantidade} produtos")
                        
                else:
                    print("Nenhum código de barras duplicado encontrado no id_super = 131!")
                    print("Todos os códigos são únicos neste conjunto.")
            else:
                print(f"Erro ao verificar duplicatas: {resultado_duplicados.get('erro', 'Erro desconhecido')}")
                        
        else:
            print(f"Erro na consulta: {resultado.get('erro', 'Erro desconhecido')}")
            print(f"Erro ao verificar duplicatas: não foi possível executar a verificação")
            
    except ImportError as e:
        print(f"Erro de importacao: {e}")
        print("Certifique-se de instalar: pip install mysql-connector-python")
    except Exception as e:
        print(f"Erro durante execucao: {e}")

if __name__ == "__main__":
    consultar_produtos_super_131()