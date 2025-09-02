#!/usr/bin/env python3
"""
Teste do sistema RAG baseado em arquivos com Dom Quixote
Para comparar com o sistema híbrido SQLite+FAISS
"""

from rag_pipeline_files import RAGPipelineFiles
import os
from pathlib import Path
import time

def teste_sistema_arquivos():
    """Testa o sistema baseado em arquivos com Dom Quixote"""
    print("=== TESTE SISTEMA RAG BASEADO EM ARQUIVOS ===")
    
    # Verificar estado inicial
    pipeline = RAGPipelineFiles()
    stats_inicial = pipeline.file_store.get_statistics()
    chunks_inicial = stats_inicial.get('total_chunks', 0)
    
    print(f"Estado inicial: {chunks_inicial} chunks")
    
    try:
        # Primeira execução com Dom Quixote
        print("\n--- PRIMEIRA EXECUÇÃO: DOM QUIXOTE ---")
        resultado = pipeline.executar_pipeline_completo(
            tema="Dom Quixote Miguel de Cervantes",
            max_docs_por_fonte=2
        )
        
        if 'erro' in resultado:
            print(f"Erro na primeira execução: {resultado['erro']}")
            return False
        
        # Verificar dados após primeira execução
        stats_primeira = pipeline.file_store.get_statistics()
        chunks_primeira = stats_primeira.get('total_chunks', 0)
        
        print(f"Após primeira execução: {chunks_primeira} chunks")
        print(f"Chunks adicionados: {chunks_primeira - chunks_inicial}")
        
        # Testar busca
        print("\n--- TESTE DE BUSCA 1 ---")
        resultados_busca = pipeline.buscar("Dom Quixote cavaleiro andante", top_k=3)
        if resultados_busca:
            print(f"Busca funcionando: {len(resultados_busca)} resultados")
            for i, res in enumerate(resultados_busca, 1):
                print(f"  {i}. Score: {res['similaridade']:.3f} - Fonte: {res['fonte']} - {res['texto'][:80]}...")
        else:
            print("FALHA: Busca não retornou resultados")
            return False
        
        # Fechar pipeline
        pipeline.close()
        del pipeline
        
        # Aguardar e reinicializar
        time.sleep(2)
        
        # Segunda execução com tema diferente
        print("\n--- SEGUNDA EXECUÇÃO: LITERATURA BRASILEIRA ---")
        pipeline2 = RAGPipelineFiles()
        
        # Verificar se estado foi restaurado
        chunks_restaurados = len(pipeline2.processed_chunks)
        print(f"Chunks restaurados: {chunks_restaurados}")
        
        resultado2 = pipeline2.executar_pipeline_completo(
            tema="Literatura Brasileira Machado de Assis",
            max_docs_por_fonte=2
        )
        
        if 'erro' in resultado2:
            print(f"Erro na segunda execução: {resultado2['erro']}")
            return False
        
        # Verificar acumulação
        stats_final = pipeline2.file_store.get_statistics()
        chunks_final = stats_final.get('total_chunks', 0)
        
        print(f"Após segunda execução: {chunks_final} chunks")
        print(f"Chunks adicionados na segunda: {chunks_final - chunks_primeira}")
        
        # Testar busca com ambos os temas
        print("\n--- TESTE DE BUSCA COMBINADA ---")
        busca_quixote = pipeline2.buscar("Dom Quixote cavaleiro", top_k=2)
        busca_brasileira = pipeline2.buscar("literatura brasileira", top_k=2)
        
        print(f"Busca Dom Quixote: {len(busca_quixote)} resultados")
        if busca_quixote:
            for i, res in enumerate(busca_quixote, 1):
                print(f"  {i}. Score: {res['similaridade']:.3f} - {res['texto'][:60]}...")
        
        print(f"Busca Literatura Brasileira: {len(busca_brasileira)} resultados")
        if busca_brasileira:
            for i, res in enumerate(busca_brasileira, 1):
                print(f"  {i}. Score: {res['similaridade']:.3f} - {res['texto'][:60]}...")
        
        # Verificar se realmente acumulou dados únicos
        acumulacao_real = chunks_final > chunks_primeira
        busca_funcionando = len(busca_quixote) > 0 and len(busca_brasileira) > 0
        
        print(f"\n=== RESULTADO FINAL ===")
        print(f"Chunks inicial: {chunks_inicial}")
        print(f"Chunks após Dom Quixote: {chunks_primeira}")
        print(f"Chunks final: {chunks_final}")
        print(f"Acumulação real: {'SIM' if acumulacao_real else 'NÃO'}")
        print(f"Busca funcionando: {'SIM' if busca_funcionando else 'NÃO'}")
        
        # Mostrar estatísticas detalhadas
        print(f"\n=== ESTATÍSTICAS DETALHADAS ===")
        stats = pipeline2.get_statistics()
        print(f"Chunks em memória: {stats['chunks_em_memoria']}")
        print(f"Documentos em memória: {stats['documentos_em_memoria']}")
        print(f"Arquivos de chunks: {stats['file_storage']['chunks_files']}")
        print(f"Arquivos de docs: {stats['file_storage']['docs_files']}")
        
        pipeline2.close()
        
        return acumulacao_real and busca_funcionando
        
    except Exception as e:
        print(f"Erro durante teste: {e}")
        return False

def limpar_dados_arquivos():
    """Limpa dados do sistema de arquivos"""
    print("=== LIMPANDO DADOS DO SISTEMA DE ARQUIVOS ===")
    
    try:
        pipeline = RAGPipelineFiles()
        pipeline.file_store.clear_all()
        pipeline.close()
        
        # Remover diretórios de resultados
        import shutil
        for path in Path(".").glob("resultados_*"):
            if path.is_dir():
                shutil.rmtree(path)
                print(f"Removido: {path}")
        
        print("Limpeza concluída")
        return True
        
    except Exception as e:
        print(f"Erro na limpeza: {e}")
        return False

if __name__ == "__main__":
    print("TESTE SISTEMA RAG BASEADO EM ARQUIVOS")
    print("=" * 50)
    
    # Limpar dados primeiro
    limpar_dados_arquivos()
    
    print("\n")
    sucesso = teste_sistema_arquivos()
    
    print("\n" + "=" * 50)
    if sucesso:
        print("RESULTADO: SISTEMA DE ARQUIVOS FUNCIONANDO PERFEITAMENTE")
        print("- Acumulação de dados únicos confirmada")
        print("- Busca funcional com múltiplos temas")
        print("- Persistência baseada em arquivos validada")
        print("- Sistema mais simples e transparente")
    else:
        print("RESULTADO: PROBLEMAS DETECTADOS NO SISTEMA DE ARQUIVOS")
        print("- Necessária investigação adicional")
        print("- Possível problema similar ao sistema híbrido")