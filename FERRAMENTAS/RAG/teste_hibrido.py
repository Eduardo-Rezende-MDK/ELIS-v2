#!/usr/bin/env python3
"""
Teste da persistência híbrida SQLite + FAISS
"""

from rag_pipeline import RAGPipeline
import os
from pathlib import Path

def teste_persistencia_hibrida():
    """Testa o sistema RAG com persistência híbrida SQLite + FAISS"""
    print("=== TESTE PERSISTÊNCIA HÍBRIDA SQLite + FAISS ===")
    
    # Limpar dados anteriores para teste limpo
    storage_path = Path("rag_storage")
    if storage_path.exists():
        for file in storage_path.glob("*"):
            if file.is_file():
                file.unlink()
        print("Dados anteriores limpos")
    
    # Criar pipeline
    pipeline = RAGPipeline()
    
    # Tema para teste
    tema = "Inteligencia Artificial"
    print(f"Tema: {tema}")
    
    # TESTE 1: Primeira execução (criação inicial)
    print("\n=== TESTE 1: CRIAÇÃO INICIAL ===")
    relatorio1 = pipeline.executar_pipeline_completo(tema, max_docs_por_fonte=2)
    
    if 'erro' in relatorio1:
        print(f"Erro no teste 1: {relatorio1['erro']}")
        return False
    
    print(f"Primeira execução:")
    print(f"- Documentos: {relatorio1['documentos']['total_coletados']}")
    print(f"- Chunks: {relatorio1['chunks']['total_processados']}")
    print(f"- Tempo: {relatorio1['tempo_execucao_segundos']:.2f}s")
    
    # Verificar arquivos criados
    db_file = storage_path / "rag_database.db"
    faiss_file = storage_path / "faiss_index.bin"
    
    if not db_file.exists():
        print("ERRO: rag_database.db não foi criado!")
        return False
    
    if not faiss_file.exists():
        print("ERRO: faiss_index.bin não foi criado!")
        return False
    
    print(f"\nArquivos criados:")
    print(f"- rag_database.db: {db_file.stat().st_size} bytes")
    print(f"- faiss_index.bin: {faiss_file.stat().st_size} bytes")
    
    # Obter estatísticas iniciais
    stats1 = pipeline.get_statistics()
    print(f"\nEstatísticas iniciais:")
    print(f"- Total chunks: {stats1['basic_stats']['total_chunks']}")
    print(f"- Total documentos: {stats1['basic_stats']['total_documents']}")
    print(f"- Cache size: {stats1['basic_stats']['cache_size']}")
    
    # TESTE 2: Segunda execução (persistência)
    print("\n=== TESTE 2: TESTE DE PERSISTÊNCIA ===")
    
    # Criar novo pipeline (simula reinicialização)
    pipeline2 = RAGPipeline()
    
    # Verificar se dados foram carregados
    stats2_inicial = pipeline2.get_statistics()
    print(f"Dados carregados na reinicialização:")
    print(f"- Total chunks: {stats2_inicial['basic_stats']['total_chunks']}")
    print(f"- Total documentos: {stats2_inicial['basic_stats']['total_documents']}")
    
    # Executar novamente (deve acumular dados)
    relatorio2 = pipeline2.executar_pipeline_completo(tema, max_docs_por_fonte=2)
    
    if 'erro' in relatorio2:
        print(f"Erro no teste 2: {relatorio2['erro']}")
        return False
    
    print(f"\nSegunda execução:")
    print(f"- Documentos: {relatorio2['documentos']['total_coletados']}")
    print(f"- Chunks: {relatorio2['chunks']['total_processados']}")
    print(f"- Tempo: {relatorio2['tempo_execucao_segundos']:.2f}s")
    
    # Obter estatísticas finais
    stats2 = pipeline2.get_statistics()
    print(f"\nEstatísticas finais:")
    print(f"- Total chunks: {stats2['basic_stats']['total_chunks']}")
    print(f"- Total documentos: {stats2['basic_stats']['total_documents']}")
    print(f"- Cache size: {stats2['basic_stats']['cache_size']}")
    
    # Verificar acumulação de dados
    chunks_iniciais = stats1['basic_stats']['total_chunks']
    chunks_finais = stats2['basic_stats']['total_chunks']
    
    if chunks_finais <= chunks_iniciais:
        print("ERRO: Dados não foram acumulados corretamente!")
        return False
    
    print(f"\nAcumulação confirmada: {chunks_iniciais} -> {chunks_finais} chunks")
    
    # TESTE 3: Busca semântica
    print("\n=== TESTE 3: BUSCA SEMÂNTICA HÍBRIDA ===")
    
    perguntas = [
        "O que é inteligência artificial?",
        "Como funciona machine learning?",
        "Quais são as aplicações da IA?"
    ]
    
    for pergunta in perguntas:
        print(f"\nPergunta: {pergunta}")
        
        # Buscar resposta
        resultados = pipeline2.buscar(pergunta, top_k=3)
        
        if resultados:
            melhor = resultados[0]
            print(f"Melhor resposta (similaridade: {melhor['similaridade']:.3f}):")
            print(f"- Fonte: {melhor['fonte']}")
            print(f"- Qualidade: {melhor['quality_score']:.3f}")
            print(f"- Chunk ID: {melhor['chunk_id']}")
            print(f"- Texto: {melhor['texto'][:100]}...")
        else:
            print("Nenhuma resposta encontrada")
    
    # TESTE 4: Verificar integridade SQLite
    print("\n=== TESTE 4: INTEGRIDADE SQLite ===")
    
    sqlite_stats = stats2['sqlite_stats']
    print(f"Estatísticas SQLite:")
    print(f"- Documentos únicos: {sqlite_stats['documents']['unique_sources']}")
    print(f"- Chunks processados: {sqlite_stats['chunks']['documents_processed']}")
    print(f"- Distribuição por fonte: {sqlite_stats['source_distribution']}")
    print(f"- Performance de busca: {sqlite_stats['search_performance']}")
    
    # Verificar tamanhos dos arquivos
    print(f"\nTamanhos finais dos arquivos:")
    print(f"- rag_database.db: {db_file.stat().st_size} bytes")
    print(f"- faiss_index.bin: {faiss_file.stat().st_size} bytes")
    
    print(f"\n=== TESTE HÍBRIDO CONCLUÍDO COM SUCESSO ===")
    return True

def verificar_consistencia():
    """Verifica consistência entre SQLite e FAISS"""
    print("\n=== VERIFICAÇÃO DE CONSISTÊNCIA ===")
    
    from storage.sqlite_manager import SQLiteManager
    from storage.vector_store import RAGVectorStore
    
    # Inicializar componentes
    sqlite_manager = SQLiteManager()
    vector_store = RAGVectorStore()
    
    # Obter estatísticas
    sqlite_stats = sqlite_manager.get_statistics()
    vector_stats = vector_store.get_statistics()
    
    chunks_sqlite = sqlite_stats['chunks']['total']
    chunks_faiss = vector_stats['basic_stats']['total_chunks']
    
    print(f"Chunks no SQLite: {chunks_sqlite}")
    print(f"Vetores no FAISS: {chunks_faiss}")
    
    if chunks_sqlite == chunks_faiss:
        print("✓ Consistência confirmada entre SQLite e FAISS")
        return True
    else:
        print("✗ Inconsistência detectada entre SQLite e FAISS")
        return False

if __name__ == "__main__":
    sucesso = teste_persistencia_hibrida()
    
    if sucesso:
        consistencia = verificar_consistencia()
        if consistencia:
            print("\n🎉 PERSISTÊNCIA HÍBRIDA SQLite + FAISS FUNCIONANDO PERFEITAMENTE!")
        else:
            print("\n⚠️ PERSISTÊNCIA FUNCIONANDO MAS COM INCONSISTÊNCIAS")
    else:
        print("\n❌ FALHA NA PERSISTÊNCIA HÍBRIDA")