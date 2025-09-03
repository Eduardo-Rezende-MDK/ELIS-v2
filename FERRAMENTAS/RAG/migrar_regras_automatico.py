#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Migração Automática de Regras JSON para RAG - ELIS v2
Script para migrar regras do gerenciador JSON para o sistema RAG
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Adicionar caminhos necessários
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(str(Path(__file__).parent.parent / "GERENCIADOR_REGRAS"))

def executar_migracao_completa():
    """
    Executa migração completa de regras JSON para RAG
    
    Returns:
        Dict com resultado da migração
    """
    print("🔄 MIGRAÇÃO AUTOMÁTICA DE REGRAS JSON → RAG")
    print("=" * 60)
    
    try:
        # Importar IntegradorMCPRAG
        from integrador_mcp import IntegradorMCPRAG
        
        print("📋 Inicializando IntegradorMCPRAG...")
        integrador = IntegradorMCPRAG()
        
        # Executar migração
        print("🚀 Iniciando migração de regras...")
        resultado = integrador.migrar_regras_json_para_rag()
        
        # Exibir resultados
        print("\n📊 RESULTADO DA MIGRAÇÃO:")
        print("-" * 40)
        
        if resultado.get('status') == 'sucesso':
            print(f"✅ Status: {resultado['status'].upper()}")
            print(f"📈 Regras migradas: {resultado.get('regras_migradas', 0)}")
            
            if resultado.get('erros'):
                print(f"⚠️ Erros encontrados: {len(resultado['erros'])}")
                for i, erro in enumerate(resultado['erros'][:5], 1):
                    print(f"   {i}. {erro}")
                if len(resultado['erros']) > 5:
                    print(f"   ... e mais {len(resultado['erros']) - 5} erros")
            else:
                print("✅ Nenhum erro encontrado")
                
        else:
            print(f"❌ Status: {resultado.get('status', 'ERRO').upper()}")
            print(f"💥 Erro: {resultado.get('erro', 'Erro desconhecido')}")
        
        print(f"⏰ Timestamp: {resultado.get('timestamp', datetime.now().isoformat())}")
        
        # Testar busca após migração
        print("\n🔍 TESTANDO BUSCA APÓS MIGRAÇÃO:")
        print("-" * 40)
        
        contexto_teste = integrador.buscar_contexto_unificado(
            query="regras sistema ELIS",
            session_id="migracao_teste"
        )
        
        if contexto_teste.get('regras'):
            print(f"✅ Regras encontradas: {len(contexto_teste['regras'])}")
            
            # Mostrar primeira regra como exemplo
            primeira_regra = contexto_teste['regras'][0]
            if isinstance(primeira_regra, dict):
                print(f"📋 Exemplo - Fonte: {primeira_regra.get('fonte', 'N/A')}")
                if 'titulo' in primeira_regra:
                    print(f"   Título: {primeira_regra['titulo'][:100]}...")
                elif 'conteudo' in primeira_regra:
                    print(f"   Conteúdo: {primeira_regra['conteudo'][:100]}...")
        else:
            print("⚠️ Nenhuma regra encontrada na busca")
        
        # Verificar estatísticas do RAG
        if 'metadados' in contexto_teste and 'estatisticas' in contexto_teste['metadados']:
            stats = contexto_teste['metadados']['estatisticas']
            print(f"\n📈 ESTATÍSTICAS DO RAG:")
            print(f"   RAG Disponível: {stats.get('rag_disponivel', False)}")
            print(f"   Gerenciador Disponível: {stats.get('gerenciador_disponivel', False)}")
            
            if 'rag_stats' in stats and isinstance(stats['rag_stats'], dict):
                rag_stats = stats['rag_stats']
                print(f"   Total de Documentos: {rag_stats.get('total_documentos', 'N/A')}")
                print(f"   Total de Chunks: {rag_stats.get('total_chunks', 'N/A')}")
        
        print("\n" + "=" * 60)
        
        if resultado.get('status') == 'sucesso':
            print("✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        else:
            print("❌ MIGRAÇÃO CONCLUÍDA COM PROBLEMAS")
        
        return resultado
        
    except Exception as e:
        erro_msg = f"Erro crítico na migração: {str(e)}"
        print(f"\n💥 {erro_msg}")
        return {
            'status': 'erro_critico',
            'erro': erro_msg,
            'timestamp': datetime.now().isoformat()
        }

def verificar_pre_requisitos():
    """
    Verifica se todos os pré-requisitos estão disponíveis
    
    Returns:
        bool: True se todos os pré-requisitos estão OK
    """
    print("🔍 Verificando pré-requisitos...")
    
    requisitos = {
        'IntegradorMCPRAG': False,
        'RAGElis': False,
        'GerenciadorRegras': False
    }
    
    try:
        from integrador_mcp import IntegradorMCPRAG
        requisitos['IntegradorMCPRAG'] = True
        print("   ✅ IntegradorMCPRAG disponível")
    except Exception as e:
        print(f"   ❌ IntegradorMCPRAG: {e}")
    
    try:
        from rag_elis import RAGElis
        requisitos['RAGElis'] = True
        print("   ✅ RAGElis disponível")
    except Exception as e:
        print(f"   ❌ RAGElis: {e}")
    
    try:
        from gerenciador_simples import GerenciadorRegras
        requisitos['GerenciadorRegras'] = True
        print("   ✅ GerenciadorRegras disponível")
    except Exception as e:
        print(f"   ❌ GerenciadorRegras: {e}")
    
    todos_ok = all(requisitos.values())
    
    if todos_ok:
        print("✅ Todos os pré-requisitos estão disponíveis")
    else:
        print("❌ Alguns pré-requisitos estão faltando")
        faltando = [nome for nome, ok in requisitos.items() if not ok]
        print(f"   Faltando: {', '.join(faltando)}")
    
    return todos_ok

def executar_sincronizacao_completa():
    """
    Executa sincronização completa entre JSON e RAG
    
    Returns:
        Dict com resultado da sincronização
    """
    print("\n🔄 SINCRONIZAÇÃO COMPLETA JSON ↔ RAG")
    print("=" * 60)
    
    try:
        from integrador_mcp import IntegradorMCPRAG
        integrador = IntegradorMCPRAG()
        
        resultado = integrador.sincronizar_regras()
        
        print("📊 RESULTADO DA SINCRONIZAÇÃO:")
        print(f"   Status: {resultado.get('status', 'desconhecido').upper()}")
        
        if 'migracao_json_rag' in resultado:
            migracao = resultado['migracao_json_rag']
            print(f"   Regras migradas: {migracao.get('regras_migradas', 0)}")
            
            if migracao.get('erros'):
                print(f"   Erros: {len(migracao['erros'])}")
        
        return resultado
        
    except Exception as e:
        erro_msg = f"Erro na sincronização: {str(e)}"
        print(f"💥 {erro_msg}")
        return {
            'status': 'erro',
            'erro': erro_msg,
            'timestamp': datetime.now().isoformat()
        }

def main():
    """
    Função principal do script
    """
    print("🤖 MIGRAÇÃO AUTOMÁTICA DE REGRAS - ELIS v2")
    print("Migrando regras do JSON para o sistema RAG...")
    print()
    
    # Verificar pré-requisitos
    if not verificar_pre_requisitos():
        print("\n❌ Não é possível continuar sem os pré-requisitos")
        return False
    
    print()
    
    # Executar migração
    resultado_migracao = executar_migracao_completa()
    
    # Executar sincronização
    resultado_sincronizacao = executar_sincronizacao_completa()
    
    # Resultado final
    sucesso_migracao = resultado_migracao.get('status') == 'sucesso'
    sucesso_sincronizacao = resultado_sincronizacao.get('status') == 'sucesso'
    
    print("\n" + "=" * 60)
    print("🎯 RESUMO FINAL:")
    print(f"   Migração: {'✅ SUCESSO' if sucesso_migracao else '❌ FALHOU'}")
    print(f"   Sincronização: {'✅ SUCESSO' if sucesso_sincronizacao else '❌ FALHOU'}")
    
    if sucesso_migracao and sucesso_sincronizacao:
        print("\n🎉 MIGRAÇÃO AUTOMÁTICA CONCLUÍDA COM SUCESSO!")
        print("   As regras JSON foram migradas para o RAG")
        print("   O sistema está pronto para busca unificada")
        return True
    else:
        print("\n⚠️ MIGRAÇÃO CONCLUÍDA COM PROBLEMAS")
        print("   Verifique os logs acima para detalhes")
        return False

if __name__ == "__main__":
    sucesso = main()
    exit(0 if sucesso else 1)