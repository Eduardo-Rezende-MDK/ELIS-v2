#!/usr/bin/env python3
"""
Teste simples de busca para verificar funcionamento básico
"""

from rag_pipeline import RAGPipeline

def teste_busca_simples():
    """Testa busca sem executar pipeline"""
    print("=== TESTE SIMPLES DE BUSCA ===")
    
    # Inicializar pipeline (deve carregar dados existentes)
    pipeline = RAGPipeline()
    
    print(f"Chunks carregados: {len(pipeline.processed_chunks)}")
    
    if not pipeline.processed_chunks:
        print("Nenhum chunk carregado - sistema vazio")
        return False
    
    # Testar várias buscas
    queries = [
        "literatura brasileira",
        "Dom Quixote",
        "Miguel de Cervantes",
        "cavaleiro andante",
        "Machado de Assis"
    ]
    
    resultados_totais = 0
    
    for query in queries:
        print(f"\nBuscando: '{query}'")
        try:
            resultados = pipeline.buscar(query, top_k=3)
            if resultados:
                print(f"  Encontrados: {len(resultados)} resultados")
                print(f"  Melhor score: {resultados[0]['similaridade']:.3f}")
                print(f"  Fonte: {resultados[0]['fonte']}")
                resultados_totais += len(resultados)
            else:
                print("  Nenhum resultado encontrado")
        except Exception as e:
            print(f"  Erro na busca: {e}")
    
    pipeline.close()
    
    print(f"\nTotal de resultados encontrados: {resultados_totais}")
    return resultados_totais > 0

if __name__ == "__main__":
    print("TESTE SIMPLES DE BUSCA")
    print("=" * 30)
    
    sucesso = teste_busca_simples()
    
    print("\n" + "=" * 30)
    if sucesso:
        print("RESULTADO: BUSCA FUNCIONANDO")
    else:
        print("RESULTADO: PROBLEMA NA BUSCA")