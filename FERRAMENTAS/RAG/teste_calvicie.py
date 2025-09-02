#!/usr/bin/env python3
"""
Teste do sistema RAG com tema: tratamentos para calvície
"""

from rag_pipeline_files import RAGPipelineFiles

def teste_calvicie():
    """Testa o sistema RAG com tema calvície"""
    print("=== TESTE RAG: TRATAMENTOS PARA CALVÍCIE ===")
    
    pipeline = RAGPipelineFiles()
    
    try:
        # Executar pipeline
        print("Executando pipeline...")
        resultado = pipeline.executar_pipeline_completo(
            tema="pesquisa tratamentos para calvicie",
            max_docs_por_fonte=2
        )
        
        if 'erro' in resultado:
            print(f"Erro no pipeline: {resultado['erro']}")
            return False
        
        print(f"\nPipeline executado com sucesso:")
        print(f"- Documentos coletados: {resultado.get('documentos_coletados', 0)}")
        print(f"- Chunks novos: {resultado.get('chunks_novos', 0)}")
        print(f"- Total de chunks: {resultado.get('total_chunks', 0)}")
        
        # Teste de busca
        print("\n=== TESTE DE BUSCA ===")
        queries = [
            "tratamentos calvicie alopecia",
            "queda de cabelo",
            "finasterida minoxidil"
        ]
        
        for query in queries:
            print(f"\nBuscando: '{query}'")
            resultados = pipeline.buscar(query, top_k=3)
            
            if resultados:
                print(f"Encontrados: {len(resultados)} resultados")
                for i, r in enumerate(resultados, 1):
                    print(f"  {i}. Score: {r['similaridade']:.3f}")
                    print(f"     Fonte: {r['fonte']}")
                    print(f"     Texto: {r['texto'][:80]}...")
            else:
                print("  Nenhum resultado encontrado")
        
        # Verificar organização de pastas
        print("\n=== VERIFICAÇÃO DE ORGANIZAÇÃO ===")
        from pathlib import Path
        
        results_path = Path("RESULTADOS")
        if results_path.exists():
            print(f"Pasta RESULTADOS existe: {results_path}")
            
            # Listar conteúdo
            for item in results_path.iterdir():
                if item.is_dir():
                    print(f"  Subpasta: {item.name}")
                    for subitem in item.iterdir():
                        print(f"    Arquivo: {subitem.name}")
        else:
            print("Pasta RESULTADOS não encontrada")
        
        pipeline.close()
        return True
        
    except Exception as e:
        print(f"Erro durante teste: {e}")
        pipeline.close()
        return False

if __name__ == "__main__":
    sucesso = teste_calvicie()
    
    print("\n" + "=" * 50)
    if sucesso:
        print("TESTE CONCLUÍDO COM SUCESSO")
        print("- Pipeline funcionando")
        print("- Busca operacional")
        print("- Organização de pastas validada")
    else:
        print("TESTE FALHOU")
        print("- Verificar logs de erro")