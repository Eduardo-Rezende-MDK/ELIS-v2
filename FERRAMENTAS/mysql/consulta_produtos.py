#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Consulta Produtos - MySQL Manager ELIS v2
Script para consultar 5 registros da tabela produtos
"""

import sys
import os
from pathlib import Path

# Adicionar o diretorio mysql ao path
sys.path.insert(0, str(Path(__file__).parent))

from mysql_ai import conectar_e_executar
import json

def consultar_produtos():
    """
    Consulta 5 registros da tabela produtos
    """
    print("=== SELECT 5 REGISTROS DA TABELA PRODUTOS ===")
    
    try:
        # Executar query
        resultado = conectar_e_executar('integrafoods', 'SELECT * FROM produtos LIMIT 5')
        
        if resultado.get('sucesso'):
            print(f"Total de registros retornados: {resultado.get('total_registros', 0)}")
            print("\nDados:")
            
            dados = resultado.get('dados', [])
            if dados:
                for i, registro in enumerate(dados, 1):
                    print(f"\nRegistro {i}:")
                    for campo, valor in registro.items():
                        print(f"  {campo}: {valor}")
            else:
                print("Nenhum registro encontrado")
        else:
            print(f"Erro na consulta: {resultado.get('erro', 'Erro desconhecido')}")
            
    except ImportError as e:
        print(f"Erro de importacao: {e}")
        print("Certifique-se de instalar: pip install mysql-connector-python")
    except Exception as e:
        print(f"Erro durante execucao: {e}")

if __name__ == "__main__":
    consultar_produtos()