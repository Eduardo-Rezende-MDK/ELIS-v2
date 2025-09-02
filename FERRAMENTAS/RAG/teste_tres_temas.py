#!/usr/bin/env python3
"""
Teste abrangente com três novos temas para validar o sistema de arquivos
Temas: Caetano Veloso, A Moreninha, Engenharia de Prompt
"""

from rag_pipeline_files import RAGPipelineFiles
import time

def teste_tres_temas_sequencial():
    """Testa o sistema com três temas diferentes sequencialmente"""
    print("=== TESTE SEQUENCIAL COM TRÊS TEMAS ===")
    
    temas = [
        "Caetano Veloso cantor brasileiro",
        "A Moreninha livro Joaquim Manuel de Macedo", 
        "Engenharia de Prompt inteligência artificial"
    ]
    
    queries_teste = [
        "Caetano Veloso música brasileira",
        "A Moreninha romance brasileiro",
        "engenharia de prompt IA"
    ]
    
    pipeline = RAGPipelineFiles()
    chunks_acumulados = []
    
    try:
        for i, tema in enumerate(temas, 1):
            print(f"\n--- EXECUÇÃO {i}: {tema.upper()} ---")
            
            # Estado inicial
            stats_inicial = pipeline.file_store.get_statistics()
            chunks_inicial = stats_inicial.get('total_chunks', 0)
            print(f"Chunks antes da execução: {chunks_inicial}")
            
            # Executar pipeline
            resultado = pipeline.executar_pipeline_completo(tema, max_docs_por_fonte=2)
            
            if 'erro' in resultado:
                print(f"ERRO na execução {i}: {resultado['erro']}")
                return False
            
            # Verificar acumulação
            stats_final = pipeline.file_store.get_statistics()
            chunks_final = stats_final.get('total_chunks', 0)
            chunks_adicionados = chunks_final - chunks_inicial
            
            print(f"Chunks após execução: {chunks_final}")
            print(f"Chunks adicionados: {chunks_adicionados}")
            
            chunks_acumulados.append(chunks_final)
            
            # Testar busca específica do tema
            print(f"\n--- TESTE DE BUSCA {i}: {queries_teste[i-1]} ---")
            resultados = pipeline.buscar(queries_teste[i-1], top_k=2)
            
            if resultados:
                print(f"Busca funcionando: {len(resultados)} resultados")
                for j, res in enumerate(resultados, 1):
                    print(f"  {j}. Score: {res['similaridade']:.3f} - Fonte: {res['fonte']} - {res['texto'][:60]}...")
            else:
                print(f"FALHA: Busca para '{queries_teste[i-1]}' não retornou resultados")
                return False
            
            # Aguardar entre execuções
            if i < len(temas):
                time.sleep(1)
        
        # Teste de busca combinada final
        print("\n--- TESTE DE BUSCA COMBINADA FINAL ---")
        todas_buscas_funcionando = True
        
        for i, query in enumerate(queries_teste, 1):
            print(f"\nBuscando: '{query}'")
            resultados = pipeline.buscar(query, top_k=2)
            
            if resultados:
                print(f"  Encontrados: {len(resultados)} resultados")
                for j, res in enumerate(resultados, 1):
                    print(f"    {j}. Score: {res['similaridade']:.3f} - {res['texto'][:50]}...")
            else:
                print(f"  FALHA: Nenhum resultado para '{query}'")
                todas_buscas_funcionando = False
        
        # Estatísticas finais
        print("\n=== ESTATÍSTICAS FINAIS ===")
        stats_finais = pipeline.get_statistics()
        print(f"Total de chunks em memória: {stats_finais['chunks_em_memoria']}")
        print(f"Total de documentos em memória: {stats_finais['documentos_em_memoria']}")
        print(f"Arquivos de chunks: {stats_finais['file_storage']['chunks_files']}")
        print(f"Arquivos de documentos: {stats_finais['file_storage']['docs_files']}")
        
        # Verificar acumulação progressiva
        acumulacao_progressiva = all(
            chunks_acumulados[i] > chunks_acumulados[i-1] 
            for i in range(1, len(chunks_acumulados))
        )
        
        print(f"\n=== RESULTADO FINAL ===")
        print(f"Chunks por execução: {chunks_acumulados}")
        print(f"Acumulação progressiva: {'SIM' if acumulacao_progressiva else 'NÃO'}")
        print(f"Todas as buscas funcionando: {'SIM' if todas_buscas_funcionando else 'NÃO'}")
        
        pipeline.close()
        
        return acumulacao_progressiva and todas_buscas_funcionando
        
    except Exception as e:
        print(f"Erro durante teste: {e}")
        pipeline.close()
        return False

def teste_busca_cruzada():
    """Testa busca cruzada entre diferentes temas"""
    print("\n=== TESTE DE BUSCA CRUZADA ===")
    
    pipeline = RAGPipelineFiles()
    
    # Queries que podem ter resultados em múltiplos temas
    queries_cruzadas = [
        "música brasileira",  # Pode aparecer em Caetano Veloso
        "literatura brasileira",  # Pode aparecer em A Moreninha
        "inteligência artificial",  # Pode aparecer em Engenharia de Prompt
        "Brasil cultura",  # Pode aparecer em múltiplos temas
        "tecnologia moderna"  # Pode aparecer em Engenharia de Prompt
    ]
    
    resultados_totais = 0
    
    for query in queries_cruzadas:
        print(f"\nBuscando: '{query}'")
        resultados = pipeline.buscar(query, top_k=3)
        
        if resultados:
            print(f"  Encontrados: {len(resultados)} resultados")
            resultados_totais += len(resultados)
            
            # Mostrar diversidade de fontes
            fontes = set(res['fonte'] for res in resultados)
            documentos = set(res['documento'] for res in resultados)
            
            print(f"  Fontes: {', '.join(fontes)}")
            print(f"  Documentos únicos: {len(documentos)}")
            
            # Mostrar melhor resultado
            melhor = resultados[0]
            print(f"  Melhor: Score {melhor['similaridade']:.3f} - {melhor['texto'][:60]}...")
        else:
            print(f"  Nenhum resultado encontrado")
    
    pipeline.close()
    
    print(f"\nTotal de resultados encontrados: {resultados_totais}")
    return resultados_totais > 10  # Esperamos pelo menos 10 resultados no total

def limpar_e_testar():
    """Limpa dados e executa todos os testes"""
    print("TESTE ABRANGENTE COM TRÊS NOVOS TEMAS")
    print("=" * 60)
    
    # Limpar dados primeiro
    print("=== LIMPANDO DADOS ANTERIORES ===")
    try:
        pipeline_temp = RAGPipelineFiles()
        pipeline_temp.file_store.clear_all()
        pipeline_temp.close()
        
        # Remover diretórios de resultados
        import shutil
        from pathlib import Path
        
        # Remover pasta RESULTADOS se existir
        results_path = Path("RESULTADOS")
        if results_path.exists():
            shutil.rmtree(results_path)
            print(f"Removido: {results_path}")
        
        # Remover pastas de resultados soltas (caso existam)
        for path in Path(".").glob("resultados_*"):
            if path.is_dir():
                shutil.rmtree(path)
                print(f"Removido: {path}")
        
        print("Limpeza concluída\n")
    except Exception as e:
        print(f"Erro na limpeza: {e}\n")
    
    # Executar testes
    sucesso_sequencial = teste_tres_temas_sequencial()
    sucesso_cruzado = teste_busca_cruzada()
    
    print("\n" + "=" * 60)
    
    if sucesso_sequencial and sucesso_cruzado:
        print("RESULTADO: SISTEMA VALIDADO COM SUCESSO TOTAL")
        print("- Acumulação progressiva confirmada com 3 temas")
        print("- Busca funcional para todos os temas")
        print("- Busca cruzada funcionando")
        print("- Sistema de arquivos completamente validado")
        print("- Pronto para uso em produção")
    else:
        print("RESULTADO: PROBLEMAS DETECTADOS")
        if not sucesso_sequencial:
            print("- Falha no teste sequencial")
        if not sucesso_cruzado:
            print("- Falha no teste de busca cruzada")
        print("- Sistema precisa de ajustes adicionais")
    
    return sucesso_sequencial and sucesso_cruzado

if __name__ == "__main__":
    limpar_e_testar()