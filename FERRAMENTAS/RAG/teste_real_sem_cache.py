#!/usr/bin/env python3
"""
Teste real da persistência híbrida sem cache ou atalhos
"""

from rag_pipeline import RAGPipeline
import os
from pathlib import Path
import time

def limpar_dados_completamente():
    """Limpa todos os dados para teste limpo"""
    print("=== LIMPEZA COMPLETA DE DADOS ===")
    
    storage_path = Path("rag_storage")
    
    # Fechar todas as conexões SQLite possíveis
    try:
        from storage.sqlite_manager import SQLiteManager
        from storage.vector_store import RAGVectorStore
        from rag_pipeline import RAGPipeline
        
        # Tentar fechar instâncias existentes
        temp_manager = SQLiteManager()
        temp_manager.close()
        del temp_manager
        
        temp_vector = RAGVectorStore()
        temp_vector.close()
        del temp_vector
        
        # Forçar garbage collection múltiplas vezes
        import gc
        for _ in range(3):
            gc.collect()
            time.sleep(0.5)
        
        print("Conexões fechadas")
    except Exception as e:
        print(f"Erro ao fechar conexões: {e}")
    
    # Aguardar mais tempo para liberar arquivos
    time.sleep(3)
    
    # Remover arquivos
    if storage_path.exists():
        for file in storage_path.glob("*"):
            if file.is_file():
                try:
                    file.unlink()
                    print(f"Removido: {file.name}")
                except Exception as e:
                    print(f"Erro ao remover {file.name}: {e}")
    
    # Remover pastas de resultados
    for pasta in Path(".").glob("resultados_*"):
        if pasta.is_dir():
            try:
                import shutil
                shutil.rmtree(pasta)
                print(f"Pasta removida: {pasta.name}")
            except Exception as e:
                print(f"Erro ao remover pasta {pasta.name}: {e}")

def teste_persistencia_real():
    """Teste real da persistência sem cache"""
    print("\n=== TESTE REAL DE PERSISTÊNCIA SEM CACHE ===")
    
    # Limpar dados
    limpar_dados_completamente()
    
    # ETAPA 1: Primeira execução
    print("\n--- ETAPA 1: PRIMEIRA EXECUÇÃO ---")
    pipeline1 = RAGPipeline()
    
    tema = "Literatura Brasileira"
    print(f"Tema: {tema}")
    
    relatorio1 = pipeline1.executar_pipeline_completo(tema, max_docs_por_fonte=2)
    
    if 'erro' in relatorio1:
        print(f"Erro na primeira execução: {relatorio1['erro']}")
        return False
    
    print(f"Primeira execução:")
    print(f"- Documentos: {relatorio1['documentos']['total_coletados']}")
    print(f"- Chunks: {relatorio1['chunks']['total_processados']}")
    
    # Verificar arquivos criados
    storage_path = Path("rag_storage")
    db_file = storage_path / "rag_database.db"
    faiss_file = storage_path / "faiss_index.bin"
    
    if not db_file.exists() or not faiss_file.exists():
        print("Arquivos não foram criados corretamente")
        return False
    
    print(f"Arquivos criados:")
    print(f"- rag_database.db: {db_file.stat().st_size} bytes")
    print(f"- faiss_index.bin: {faiss_file.stat().st_size} bytes")
    
    # Obter estatísticas da primeira execução
    stats1 = pipeline1.get_statistics()
    chunks_primeira = stats1['basic_stats']['total_chunks']
    docs_primeira = stats1['basic_stats']['total_documents']
    
    print(f"Estatísticas primeira execução:")
    print(f"- Chunks: {chunks_primeira}")
    print(f"- Documentos: {docs_primeira}")
    
    # Testar busca na primeira execução
    resultado1 = pipeline1.buscar("literatura", top_k=1)
    if resultado1:
        print(f"Busca primeira execução: {resultado1[0]['similaridade']:.3f}")
    else:
        print("Busca primeira execução: sem resultados")
    
    # Fechar e destruir pipeline1 completamente
    pipeline1.close()
    del pipeline1
    
    # Forçar limpeza de memória
    import gc
    gc.collect()
    
    # ETAPA 2: Reinicialização (teste de persistência)
    print("\n--- ETAPA 2: REINICIALIZAÇÃO ---")
    
    # Aguardar para garantir que conexões foram fechadas
    time.sleep(2)
    
    # Criar novo pipeline (simula reinicialização do sistema)
    pipeline2 = RAGPipeline()
    
    # Verificar se dados foram carregados
    stats2_inicial = pipeline2.get_statistics()
    chunks_carregados = stats2_inicial['basic_stats']['total_chunks']
    docs_carregados = stats2_inicial['basic_stats']['total_documents']
    
    print(f"Dados carregados na reinicialização:")
    print(f"- Chunks: {chunks_carregados}")
    print(f"- Documentos: {docs_carregados}")
    
    # Verificar se persistência funcionou
    if chunks_carregados == 0:
        print("FALHA: Nenhum dado foi carregado na reinicialização")
        return False
    
    if chunks_carregados != chunks_primeira:
        print(f"FALHA: Chunks carregados ({chunks_carregados}) != chunks originais ({chunks_primeira})")
        return False
    
    # Testar busca após reinicialização
    resultado2 = pipeline2.buscar("literatura", top_k=1)
    if not resultado2:
        print("FALHA: Busca não funcionou após reinicialização")
        return False
    
    print(f"Busca após reinicialização: {resultado2[0]['similaridade']:.3f}")
    
    # ETAPA 3: Segunda execução (acumulação)
    print("\n--- ETAPA 3: SEGUNDA EXECUÇÃO (ACUMULAÇÃO) ---")
    
    relatorio2 = pipeline2.executar_pipeline_completo(tema, max_docs_por_fonte=2)
    
    if 'erro' in relatorio2:
        print(f"Erro na segunda execução: {relatorio2['erro']}")
        return False
    
    print(f"Segunda execução:")
    print(f"- Documentos: {relatorio2['documentos']['total_coletados']}")
    print(f"- Chunks: {relatorio2['chunks']['total_processados']}")
    
    # Verificar acumulação
    stats2_final = pipeline2.get_statistics()
    chunks_final = stats2_final['basic_stats']['total_chunks']
    
    print(f"Estatísticas finais:")
    print(f"- Chunks inicial: {chunks_primeira}")
    print(f"- Chunks final: {chunks_final}")
    
    if chunks_final <= chunks_primeira:
        print("FALHA: Dados não foram acumulados")
        return False
    
    print(f"SUCESSO: Acumulação confirmada ({chunks_primeira} -> {chunks_final})")
    
    # ETAPA 4: Verificação de consistência
    print("\n--- ETAPA 4: VERIFICAÇÃO DE CONSISTÊNCIA ---")
    
    # Verificar SQLite diretamente
    from storage.sqlite_manager import SQLiteManager
    sqlite_manager = SQLiteManager()
    sqlite_stats = sqlite_manager.get_statistics()
    
    chunks_sqlite = sqlite_stats.get('chunks', {}).get('total', 0)
    docs_sqlite = sqlite_stats.get('documents', {}).get('total', 0)
    
    print(f"Dados no SQLite:")
    print(f"- Chunks: {chunks_sqlite}")
    print(f"- Documentos: {docs_sqlite}")
    
    # Verificar FAISS
    faiss_chunks = pipeline2.vector_store.index.ntotal if pipeline2.vector_store.index else 0
    print(f"Vetores no FAISS: {faiss_chunks}")
    
    # Verificar consistência
    if chunks_sqlite != faiss_chunks:
        print(f"FALHA: Inconsistência SQLite({chunks_sqlite}) != FAISS({faiss_chunks})")
        return False
    
    if chunks_sqlite != chunks_final:
        print(f"FALHA: Inconsistência SQLite({chunks_sqlite}) != Pipeline({chunks_final})")
        return False
    
    print("SUCESSO: Consistência total confirmada")
    
    # ETAPA 5: Teste de busca final
    print("\n--- ETAPA 5: TESTE DE BUSCA FINAL ---")
    
    perguntas = [
        "O que é literatura brasileira?",
        "Quais são os principais autores?",
        "Como surgiu a literatura no Brasil?"
    ]
    
    for pergunta in perguntas:
        resultados = pipeline2.buscar(pergunta, top_k=1)
        if resultados:
            print(f"'{pergunta}' -> Similaridade: {resultados[0]['similaridade']:.3f}")
        else:
            print(f"'{pergunta}' -> Sem resultados")
    
    return True

def verificar_arquivos_finais():
    """Verifica estado final dos arquivos"""
    print("\n=== VERIFICAÇÃO FINAL DOS ARQUIVOS ===")
    
    storage_path = Path("rag_storage")
    
    if not storage_path.exists():
        print("Pasta rag_storage não existe")
        return
    
    files = list(storage_path.glob("*"))
    print(f"Arquivos na pasta rag_storage:")
    
    for file in files:
        if file.is_file():
            size = file.stat().st_size
            print(f"- {file.name}: {size} bytes")
    
    # Verificar se há arquivos antigos (chunks.pkl, metadata.json)
    chunks_pkl = storage_path / "chunks.pkl"
    metadata_json = storage_path / "metadata.json"
    
    if chunks_pkl.exists():
        print(f"AVISO: chunks.pkl ainda existe ({chunks_pkl.stat().st_size} bytes)")
    
    if metadata_json.exists():
        print(f"AVISO: metadata.json ainda existe ({metadata_json.stat().st_size} bytes)")

if __name__ == "__main__":
    print("TESTE REAL DE PERSISTÊNCIA - SEM CACHE OU ATALHOS")
    print("=" * 50)
    
    sucesso = teste_persistencia_real()
    
    verificar_arquivos_finais()
    
    print("\n" + "=" * 50)
    if sucesso:
        print("RESULTADO: PERSISTÊNCIA HÍBRIDA FUNCIONANDO PERFEITAMENTE")
        print("- Dados persistem entre reinicializações")
        print("- Acumulação funciona corretamente")
        print("- Consistência SQLite + FAISS confirmada")
        print("- Busca semântica operacional")
    else:
        print("RESULTADO: FALHAS DETECTADAS NA PERSISTÊNCIA")
        print("- Sistema precisa de correções adicionais")