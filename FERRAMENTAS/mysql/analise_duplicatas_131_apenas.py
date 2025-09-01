#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analise Duplicatas ID_SUPER 131 Apenas - MySQL Manager ELIS v2
Script focado APENAS no id_super = 131 para verificar se duplicatas são idênticas
"""

import sys
import os
from pathlib import Path

# Adicionar o diretorio mysql ao path
sys.path.insert(0, str(Path(__file__).parent))

from mysql_ai import conectar_e_executar
import json

def obter_amostra_dual_131():
    """
    Obtém amostra de 20 produtos da DUAL_produtos que existem no id_super = 131
    """
    print("=== AMOSTRA DUAL_PRODUTOS (APENAS ID_SUPER = 131) ===")
    
    try:
        # Pegar 20 produtos da DUAL que existem no id_super = 131
        query_amostra = """
        SELECT DISTINCT 
            d.id_externo as codigo_barras,
            MIN(d.nome) as nome_dual
        FROM DUAL_produtos d
        INNER JOIN produtos p ON d.id_externo = p.codigo_barras
        WHERE d.id_externo IS NOT NULL 
        AND d.id_externo != ''
        AND p.id_super = 131
        GROUP BY d.id_externo
        ORDER BY d.id_externo
        LIMIT 20
        """
        
        resultado_amostra = conectar_e_executar('integrafoods', query_amostra)
        
        if resultado_amostra.get('sucesso'):
            amostra = resultado_amostra.get('dados', [])
            print(f"\n1. AMOSTRA SELECIONADA (20 códigos com id_super = 131):")
            print(f"   {'#':<3} {'Código':<12} {'Nome':<50}")
            print(f"   {'-'*70}")
            
            codigos_amostra = []
            for i, produto in enumerate(amostra, 1):
                codigo = produto.get('codigo_barras')
                nome = produto.get('nome_dual', 'N/A')[:45]
                
                codigos_amostra.append(codigo)
                print(f"   {i:<3} {codigo:<12} {nome:<50}")
            
            print(f"\n   Total de códigos: {len(codigos_amostra)}")
            return codigos_amostra
        else:
            print(f"   Erro: {resultado_amostra.get('erro')}")
            return []
            
    except Exception as e:
        print(f"Erro ao obter amostra: {e}")
        return []

def analisar_duplicatas_131_apenas(codigos_amostra):
    """
    Analisa APENAS duplicatas no id_super = 131
    """
    print("\n=== DUPLICATAS APENAS NO ID_SUPER = 131 ===")
    
    if not codigos_amostra:
        print("   Nenhum código para analisar.")
        return
    
    try:
        # Converter lista de códigos para string SQL
        codigos_sql = "','".join(codigos_amostra)
        codigos_sql = f"'{codigos_sql}'"
        
        # Analisar APENAS id_super = 131
        query_131 = f"""
        SELECT 
            codigo_barras,
            COUNT(*) as total_duplicatas,
            GROUP_CONCAT(DISTINCT id ORDER BY created_at) as lista_ids,
            MIN(created_at) as primeira_criacao,
            MAX(created_at) as ultima_criacao,
            SUM(CASE WHEN status = 1 THEN 1 ELSE 0 END) as ativas,
            SUM(CASE WHEN status = 0 THEN 1 ELSE 0 END) as inativas
        FROM produtos
        WHERE codigo_barras IN ({codigos_sql})
        AND id_super = 131
        GROUP BY codigo_barras
        ORDER BY total_duplicatas DESC, codigo_barras
        """
        
        resultado_131 = conectar_e_executar('integrafoods', query_131)
        
        if resultado_131.get('sucesso'):
            dados_131 = resultado_131.get('dados', [])
            print(f"\n1. CONTAGEM DE DUPLICATAS (ID_SUPER = 131):")
            print(f"   {'Código':<12} {'Duplicatas':<10} {'Ativas':<7} {'Inativas':<8} {'IDs':<25}")
            print(f"   {'-'*70}")
            
            total_duplicatas = 0
            codigos_com_dup = 0
            codigos_sem_dup = 0
            
            for item in dados_131:
                codigo = item.get('codigo_barras')
                duplicatas = item.get('total_duplicatas')
                ativas = item.get('ativas')
                inativas = item.get('inativas')
                ids = item.get('lista_ids', 'N/A')
                
                total_duplicatas += duplicatas
                
                if duplicatas > 1:
                    codigos_com_dup += 1
                else:
                    codigos_sem_dup += 1
                
                # Limitar IDs mostrados
                if len(str(ids)) > 20:
                    ids_mostrar = str(ids)[:17] + "..."
                else:
                    ids_mostrar = str(ids)
                
                print(f"   {codigo:<12} {duplicatas:<10} {ativas:<7} {inativas:<8} {ids_mostrar:<25}")
            
            print(f"\n   RESUMO:")
            print(f"   - Códigos analisados: {len(dados_131)}")
            print(f"   - Códigos SEM duplicatas: {codigos_sem_dup}")
            print(f"   - Códigos COM duplicatas: {codigos_com_dup}")
            print(f"   - Total de produtos: {total_duplicatas}")
            
            if len(dados_131) > 0:
                media = total_duplicatas / len(dados_131)
                print(f"   - Média de produtos por código: {media:.1f}")
                
                if codigos_com_dup > 0:
                    percentual = (codigos_com_dup / len(dados_131)) * 100
                    print(f"   - Percentual com duplicatas: {percentual:.1f}%")
            
            return dados_131
        else:
            print(f"   Erro: {resultado_131.get('erro')}")
            return []
            
    except Exception as e:
        print(f"Erro durante análise: {e}")
        return []

def comparar_duplicatas_detalhadamente(codigos_amostra):
    """
    Compara detalhadamente as duplicatas para verificar se são idênticas
    """
    print("\n=== COMPARACAO DETALHADA DAS DUPLICATAS ===")
    
    if not codigos_amostra:
        print("   Nenhum código para analisar.")
        return
    
    try:
        # Pegar os primeiros 5 códigos para análise detalhada
        codigos_analise = codigos_amostra[:5]
        
        for i, codigo in enumerate(codigos_analise, 1):
            print(f"\n{i}. CÓDIGO: {codigo}")
            print(f"   {'-'*50}")
            
            # Query detalhada para um código específico
            query_detalhes = f"""
            SELECT 
                id,
                nome,
                codigo_barras,
                status,
                created_at,
                updated_at
            FROM produtos
            WHERE codigo_barras = '{codigo}'
            AND id_super = 131
            ORDER BY created_at
            """
            
            resultado_det = conectar_e_executar('integrafoods', query_detalhes)
            
            if resultado_det.get('sucesso'):
                detalhes = resultado_det.get('dados', [])
                
                if len(detalhes) <= 1:
                    print(f"   Produto ÚNICO (sem duplicatas)")
                    if detalhes:
                        produto = detalhes[0]
                        print(f"   ID: {produto.get('id')} | Status: {'Ativo' if produto.get('status') == 1 else 'Inativo'}")
                        print(f"   Nome: {produto.get('nome', 'N/A')[:40]}")
                else:
                    print(f"   {len(detalhes)} DUPLICATAS encontradas:")
                    
                    # Comparar campos importantes
                    nomes = set()
                    status_list = set()
                    
                    for j, produto in enumerate(detalhes, 1):
                        produto_id = produto.get('id')
                        nome = produto.get('nome', 'N/A')
                        status = produto.get('status')
                        created_at = produto.get('created_at')
                        updated_at = produto.get('updated_at')
                        
                        # Coletar valores únicos
                        nomes.add(nome)
                        status_list.add(status)
                        
                        status_texto = 'Ativo' if status == 1 else 'Inativo'
                        print(f"     {j}. ID: {produto_id} | {status_texto}")
                        print(f"        Nome: {nome[:50]}")
                        print(f"        Criado: {created_at} | Atualizado: {updated_at}")
                    
                    # Análise de diferenças
                    print(f"\n   ANÁLISE DE DIFERENÇAS:")
                    print(f"   - Nomes únicos: {len(nomes)} {'(IDÊNTICOS)' if len(nomes) == 1 else '(DIFERENTES)'}")
                    print(f"   - Status únicos: {len(status_list)} {'(IDÊNTICOS)' if len(status_list) == 1 else '(DIFERENTES)'}")
                    
                    # Conclusão para este código
                    diferencas = []
                    if len(nomes) > 1: diferencas.append('nomes')
                    if len(status_list) > 1: diferencas.append('status')
                    
                    if diferencas:
                        print(f"   CONCLUSÃO: DUPLICATAS COM DIFERENÇAS em {', '.join(diferencas)}")
                    else:
                        print(f"   CONCLUSÃO: DUPLICATAS IDÊNTICAS (apenas IDs e datas diferentes)")
            else:
                print(f"   Erro: {resultado_det.get('erro')}")
                
    except Exception as e:
        print(f"Erro durante comparação detalhada: {e}")

def resumo_final_131(dados_131):
    """
    Gera resumo final focado apenas no id_super = 131
    """
    print("\n=== RESUMO FINAL (APENAS ID_SUPER = 131) ===")
    
    if not dados_131:
        print("   Nenhum dado para resumir.")
        return
    
    try:
        # Estatísticas gerais
        total_codigos = len(dados_131)
        total_produtos = sum(item.get('total_duplicatas', 0) for item in dados_131)
        codigos_com_duplicatas = sum(1 for item in dados_131 if item.get('total_duplicatas', 0) > 1)
        codigos_sem_duplicatas = total_codigos - codigos_com_duplicatas
        
        print(f"\n1. ESTATÍSTICAS GERAIS:")
        print(f"   - Códigos analisados: {total_codigos}")
        print(f"   - Total de produtos: {total_produtos}")
        print(f"   - Códigos SEM duplicatas: {codigos_sem_duplicatas}")
        print(f"   - Códigos COM duplicatas: {codigos_com_duplicatas}")
        
        if total_codigos > 0:
            media_produtos = total_produtos / total_codigos
            percentual_duplicatas = (codigos_com_duplicatas / total_codigos) * 100
            print(f"   - Média de produtos por código: {media_produtos:.1f}")
            print(f"   - Percentual com duplicatas: {percentual_duplicatas:.1f}%")
        
        # Distribuição de duplicatas
        if codigos_com_duplicatas > 0:
            distribuicao = {}
            for item in dados_131:
                duplicatas = item.get('total_duplicatas', 0)
                if duplicatas > 1:
                    distribuicao[duplicatas] = distribuicao.get(duplicatas, 0) + 1
            
            print(f"\n2. DISTRIBUIÇÃO DE DUPLICATAS:")
            for num_dup, count in sorted(distribuicao.items()):
                print(f"   - {num_dup} produtos: {count} códigos")
        
        print(f"\n3. CONCLUSÕES:")
        print(f"   - Foco APENAS no id_super = 131 (dados atuais)")
        print(f"   - Eliminado ruído de outros id_super")
        print(f"   - Duplicatas identificadas são do mesmo id_super")
        print(f"   - Necessário verificar se são idênticas ou diferentes")
        
    except Exception as e:
        print(f"Erro durante resumo: {e}")

def main():
    """
    Função principal - FOCO APENAS NO ID_SUPER = 131
    """
    try:
        print("ANÁLISE FOCADA: APENAS ID_SUPER = 131")
        print("Objetivo: Verificar duplicatas SEM ruído de outros id_super")
        print("="*60)
        
        # 1. Obter amostra focada no id_super = 131
        codigos_amostra = obter_amostra_dual_131()
        
        if not codigos_amostra:
            print("\nErro: Não foi possível obter amostra.")
            return
        
        # 2. Analisar duplicatas APENAS no id_super = 131
        dados_131 = analisar_duplicatas_131_apenas(codigos_amostra)
        
        # 3. Comparação detalhada das duplicatas
        comparar_duplicatas_detalhadamente(codigos_amostra)
        
        # 4. Resumo final
        resumo_final_131(dados_131)
        
        print("\n" + "="*60)
        print("FOCO: APENAS ID_SUPER = 131 - SEM RUÍDO")
        print("=== ANÁLISE CONCLUÍDA ===")
        
    except Exception as e:
        print(f"Erro durante execução: {e}")

if __name__ == "__main__":
    main()