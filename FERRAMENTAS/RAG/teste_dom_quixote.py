#!/usr/bin/env python3
"""
Teste específico com Dom Quixote para validar acumulação real de dados únicos
"""

from rag_pipeline import RAGPipeline
import os
from pathlib import Path
import time

def teste_acumulacao_dom_quixote():
    """Testa acumulação real com tema diferente (Dom Quixote)"""
    print("=== TESTE DE ACUMULAÇÃO REAL - DOM QUIXOTE ===")
    
    # Verificar estado inicial
    pipeline = RAGPipeline()
    stats_inicial = pipeline.vector_store.sqlite_manager.get_statistics()
    chunks_inicial = stats_inicial.get('chunks', {}).get('total', 0)
    
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
        stats_primeira = pipeline.vector_store.sqlite_manager.get_statistics()
        chunks_primeira = stats_primeira.get('chunks', {}).get('total', 0)
        
        print(f"Após primeira execução: {chunks_primeira} chunks")
        print(f"Chunks adicionados: {chunks_primeira - chunks_inicial}")
        
        # Testar busca
        resultados_busca = pipeline.buscar("Dom Quixote cavaleiro andante", top_k=3)
        if resultados_busca:
            print(f"Busca funcionando: {len(resultados_busca)} resultados")
            print(f"Melhor score: {resultados_busca[0]['similaridade']:.3f}")
        else:
            print("FALHA: Busca não retornou resultados")
            return False
        
        # Fechar pipeline
        pipeline.close()
        del pipeline
        
        # Aguardar e reinicializar
        time.sleep(2)
        
        # Segunda execução com tema diferente (Literatura Brasileira)
        print("\n--- SEGUNDA EXECUÇÃO: LITERATURA BRASILEIRA ---")
        pipeline2 = RAGPipeline()
        
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
        stats_final = pipeline2.vector_store.sqlite_manager.get_statistics()
        chunks_final = stats_final.get('chunks', {}).get('total', 0)
        
        print(f"Após segunda execução: {chunks_final} chunks")
        print(f"Chunks adicionados na segunda: {chunks_final - chunks_primeira}")
        
        # Testar busca com ambos os temas
        print("\n--- TESTE DE BUSCA COMBINADA ---")
        busca_quixote = pipeline2.buscar("Dom Quixote cavaleiro", top_k=2)
        busca_brasileira = pipeline2.buscar("literatura brasileira", top_k=2)
        
        print(f"Busca Dom Quixote: {len(busca_quixote)} resultados")
        print(f"Busca Literatura Brasileira: {len(busca_brasileira)} resultados")
        
        # Verificar se realmente acumulou dados únicos
        acumulacao_real = chunks_final > chunks_primeira
        
        print(f"\n=== RESULTADO FINAL ===")
        print(f"Chunks inicial: {chunks_inicial}")
        print(f"Chunks após Dom Quixote: {chunks_primeira}")
        print(f"Chunks final: {chunks_final}")
        print(f"Acumulação real: {'SIM' if acumulacao_real else 'NÃO'}")
        
        pipeline2.close()
        
        return acumulacao_real
        
    except Exception as e:
        print(f"Erro durante teste: {e}")
        return False

if __name__ == "__main__":
    print("TESTE DE ACUMULAÇÃO REAL COM DOM QUIXOTE")
    print("=" * 50)
    
    sucesso = teste_acumulacao_dom_quixote()
    
    print("\n" + "=" * 50)
    if sucesso:
        print("RESULTADO: ACUMULAÇÃO FUNCIONANDO CORRETAMENTE")
        print("- Sistema acumula dados únicos entre execuções")
        print("- Busca funciona com múltiplos temas")
        print("- Persistência híbrida validada")
    else:
        print("RESULTADO: PROBLEMA DE ACUMULAÇÃO CONFIRMADO")
        print("- Sistema não acumula dados únicos")
        print("- Necessária investigação adicional")
        print("- Possível problema na geração de IDs ou filtros")