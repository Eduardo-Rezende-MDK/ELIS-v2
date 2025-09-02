#!/usr/bin/env python3
"""
Teste e correção da implementação com tema Machado de Assis
"""

from rag_pipeline import RAGPipeline
import os
from pathlib import Path

def teste_machado_assis():
    """Testa e corrige o sistema RAG com Machado de Assis"""
    print("=== TESTE E CORREÇÃO - MACHADO DE ASSIS ===")
    
    # Limpar dados anteriores
    storage_path = Path("rag_storage")
    if storage_path.exists():
        for file in storage_path.glob("*"):
            if file.is_file():
                try:
                    file.unlink()
                    print(f"Removido: {file.name}")
                except Exception as e:
                    print(f"Erro ao remover {file.name}: {e}")
    
    # Criar pipeline
    pipeline = RAGPipeline()
    
    # Tema para teste
    tema = "Machado de Assis"
    print(f"\nTema: {tema}")
    
    # TESTE 1: Execução inicial
    print("\n=== TESTE 1: EXECUÇÃO INICIAL ===")
    try:
        relatorio1 = pipeline.executar_pipeline_completo(tema, max_docs_por_fonte=3)
        
        if 'erro' in relatorio1:
            print(f"Erro: {relatorio1['erro']}")
            return False
        
        print(f"Primeira execução bem-sucedida:")
        print(f"- Documentos: {relatorio1['documentos']['total_coletados']}")
        print(f"- Chunks: {relatorio1['chunks']['total_processados']}")
        print(f"- Tempo: {relatorio1['tempo_execucao_segundos']:.2f}s")
        
        # Verificar arquivos criados
        db_file = storage_path / "rag_database.db"
        faiss_file = storage_path / "faiss_index.bin"
        
        print(f"\nArquivos criados:")
        if db_file.exists():
            print(f"✓ rag_database.db: {db_file.stat().st_size} bytes")
        else:
            print("✗ rag_database.db não encontrado")
            
        if faiss_file.exists():
            print(f"✓ faiss_index.bin: {faiss_file.stat().st_size} bytes")
        else:
            print("✗ faiss_index.bin não encontrado")
        
    except Exception as e:
        print(f"Erro na execução inicial: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # TESTE 2: Busca semântica
    print("\n=== TESTE 2: BUSCA SEMÂNTICA ===")
    try:
        perguntas = [
            "Quem foi Machado de Assis?",
            "Quais são as principais obras de Machado de Assis?",
            "Quando Machado de Assis nasceu?"
        ]
        
        for pergunta in perguntas:
            print(f"\nPergunta: {pergunta}")
            
            resultados = pipeline.buscar(pergunta, top_k=2)
            
            if resultados:
                melhor = resultados[0]
                print(f"Resposta encontrada (similaridade: {melhor['similaridade']:.3f}):")
                print(f"- Fonte: {melhor['fonte']}")
                print(f"- Documento: {melhor['documento']}")
                print(f"- Texto: {melhor['texto'][:150]}...")
            else:
                print("Nenhuma resposta encontrada")
                
    except Exception as e:
        print(f"Erro na busca semântica: {e}")
        import traceback
        traceback.print_exc()
    
    # TESTE 3: Verificar persistência
    print("\n=== TESTE 3: VERIFICAÇÃO DE PERSISTÊNCIA ===")
    try:
        # Obter estatísticas antes
        stats_antes = pipeline.get_statistics()
        chunks_antes = stats_antes['basic_stats']['total_chunks']
        print(f"Chunks antes da reinicialização: {chunks_antes}")
        
        # Simular reinicialização
        pipeline2 = RAGPipeline()
        
        # Verificar se dados foram carregados
        stats_depois = pipeline2.get_statistics()
        chunks_depois = stats_depois['basic_stats']['total_chunks']
        print(f"Chunks após reinicialização: {chunks_depois}")
        
        if chunks_depois > 0:
            print("✓ Persistência funcionando")
            
            # Testar busca após reinicialização
            resultado_persistencia = pipeline2.buscar("Machado de Assis", top_k=1)
            if resultado_persistencia:
                print("✓ Busca funcionando após reinicialização")
            else:
                print("✗ Busca não funcionando após reinicialização")
        else:
            print("✗ Persistência não funcionando - dados não carregados")
            
    except Exception as e:
        print(f"Erro na verificação de persistência: {e}")
        import traceback
        traceback.print_exc()
    
    # TESTE 4: Verificar integridade SQLite
    print("\n=== TESTE 4: INTEGRIDADE SQLite ===")
    try:
        from storage.sqlite_manager import SQLiteManager
        
        sqlite_manager = SQLiteManager()
        sqlite_stats = sqlite_manager.get_statistics()
        
        print(f"Estatísticas SQLite:")
        print(f"- Documentos: {sqlite_stats.get('documents', {}).get('total', 0)}")
        print(f"- Chunks: {sqlite_stats.get('chunks', {}).get('total', 0)}")
        print(f"- Distribuição: {sqlite_stats.get('source_distribution', {})}")
        
        # Verificar consistência
        vector_stats = pipeline.vector_store.get_statistics()
        chunks_sqlite = sqlite_stats.get('chunks', {}).get('total', 0)
        chunks_faiss = vector_stats['basic_stats']['total_chunks']
        
        print(f"\nConsistência:")
        print(f"- SQLite: {chunks_sqlite} chunks")
        print(f"- FAISS: {chunks_faiss} vetores")
        
        if chunks_sqlite == chunks_faiss and chunks_sqlite > 0:
            print("✓ Consistência confirmada")
        else:
            print("✗ Inconsistência detectada")
            
    except Exception as e:
        print(f"Erro na verificação SQLite: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n=== TESTE MACHADO DE ASSIS CONCLUÍDO ===")
    return True

def diagnosticar_problemas():
    """Diagnostica problemas específicos na implementação"""
    print("\n=== DIAGNÓSTICO DE PROBLEMAS ===")
    
    try:
        # Verificar se arquivos existem
        storage_path = Path("rag_storage")
        
        print(f"Pasta rag_storage existe: {storage_path.exists()}")
        
        if storage_path.exists():
            files = list(storage_path.glob("*"))
            print(f"Arquivos encontrados: {[f.name for f in files]}")
            
            # Verificar tamanhos
            for file in files:
                if file.is_file():
                    print(f"- {file.name}: {file.stat().st_size} bytes")
        
        # Testar componentes individualmente
        print("\nTestando componentes:")
        
        # SQLite Manager
        try:
            from storage.sqlite_manager import SQLiteManager
            sqlite_manager = SQLiteManager()
            print("✓ SQLiteManager inicializado")
        except Exception as e:
            print(f"✗ Erro no SQLiteManager: {e}")
        
        # Vector Store
        try:
            from storage.vector_store import RAGVectorStore
            vector_store = RAGVectorStore()
            print("✓ RAGVectorStore inicializado")
        except Exception as e:
            print(f"✗ Erro no RAGVectorStore: {e}")
        
        # Pipeline
        try:
            pipeline = RAGPipeline()
            print("✓ RAGPipeline inicializado")
        except Exception as e:
            print(f"✗ Erro no RAGPipeline: {e}")
            
    except Exception as e:
        print(f"Erro no diagnóstico: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Executar diagnóstico primeiro
    diagnosticar_problemas()
    
    # Executar teste
    sucesso = teste_machado_assis()
    
    if sucesso:
        print("\n🎉 TESTE MACHADO DE ASSIS CONCLUÍDO COM SUCESSO!")
    else:
        print("\n❌ FALHAS DETECTADAS NO TESTE MACHADO DE ASSIS")