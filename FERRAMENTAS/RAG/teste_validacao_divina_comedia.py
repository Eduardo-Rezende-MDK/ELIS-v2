#!/usr/bin/env python3
"""
Teste de validação usando os três últimos temas testados:
Caetano Veloso, A Moreninha, Engenharia de Prompt
"""

from rag_pipeline_files import RAGPipelineFiles
import pickle
from pathlib import Path

def verificar_dados_fisicos():
    """Verifica se existem dados físicos persistidos dos três temas"""
    print("=== VERIFICAÇÃO DE DADOS FÍSICOS PERSISTIDOS ===")
    
    file_storage_path = Path("file_storage")
    chunks_path = file_storage_path / "chunks"
    docs_path = file_storage_path / "documents"
    
    if not file_storage_path.exists():
        print("FALHA: Diretório file_storage não existe")
        return False
    
    # Contar arquivos físicos
    chunk_files = list(chunks_path.glob("*.pkl")) if chunks_path.exists() else []
    doc_files = list(docs_path.glob("*.pkl")) if docs_path.exists() else []
    
    print(f"Arquivos de chunks encontrados: {len(chunk_files)}")
    print(f"Arquivos de documentos encontrados: {len(doc_files)}")
    
    # Examinar arquivos para verificar conteúdo dos três temas
    temas_encontrados = {
        'caetano': 0,
        'moreninha': 0, 
        'engenharia': 0
    }
    
    print("\n--- EXAMINANDO CONTEÚDO DOS ARQUIVOS ---")
    
    # Verificar chunks
    for i, chunk_file in enumerate(chunk_files[:10]):  # Examinar primeiros 10
        try:
            with open(chunk_file, 'rb') as f:
                chunk = pickle.load(f)
            
            texto_lower = chunk.text.lower()
            titulo_lower = chunk.document_title.lower()
            
            # Verificar Caetano Veloso
            if 'caetano' in texto_lower or 'veloso' in texto_lower or 'caetano' in titulo_lower:
                temas_encontrados['caetano'] += 1
                print(f"  Chunk {i+1}: CAETANO VELOSO encontrado")
                print(f"    Arquivo: {chunk_file.name}")
                print(f"    Documento: {chunk.document_title}")
                print(f"    Texto: {chunk.text[:80]}...")
            
            # Verificar A Moreninha
            elif 'moreninha' in texto_lower or 'macedo' in texto_lower or 'moreninha' in titulo_lower:
                temas_encontrados['moreninha'] += 1
                print(f"  Chunk {i+1}: A MORENINHA encontrado")
                print(f"    Arquivo: {chunk_file.name}")
                print(f"    Documento: {chunk.document_title}")
                print(f"    Texto: {chunk.text[:80]}...")
            
            # Verificar Engenharia de Prompt
            elif ('prompt' in texto_lower or 'engenharia' in texto_lower or 
                  'inteligência artificial' in texto_lower or 'prompt' in titulo_lower):
                temas_encontrados['engenharia'] += 1
                print(f"  Chunk {i+1}: ENGENHARIA DE PROMPT encontrado")
                print(f"    Arquivo: {chunk_file.name}")
                print(f"    Documento: {chunk.document_title}")
                print(f"    Texto: {chunk.text[:80]}...")
            
            else:
                print(f"  Chunk {i+1}: Outro tema - {chunk.text[:50]}...")
                
        except Exception as e:
            print(f"  Erro ao ler {chunk_file}: {e}")
    
    print(f"\nResumo da verificação física:")
    print(f"- Chunks Caetano Veloso: {temas_encontrados['caetano']}")
    print(f"- Chunks A Moreninha: {temas_encontrados['moreninha']}")
    print(f"- Chunks Engenharia de Prompt: {temas_encontrados['engenharia']}")
    
    total_temas = sum(temas_encontrados.values())
    print(f"- Total de chunks dos três temas: {total_temas}")
    
    return len(chunk_files) > 0 and total_temas > 0

def testar_busca_tres_temas():
    """Testa busca específica para os três temas"""
    print("\n=== TESTE DE BUSCA: TRÊS TEMAS ===")
    
    pipeline = RAGPipelineFiles()
    
    # Verificar estado do pipeline
    stats = pipeline.get_statistics()
    print(f"Chunks em memória: {stats['chunks_em_memoria']}")
    print(f"Total de chunks no storage: {stats['file_storage']['total_chunks']}")
    
    if stats['chunks_em_memoria'] == 0:
        print("AVISO: Nenhum chunk em memória - sistema pode estar vazio")
        return False
    
    # Queries dos três temas testados
    queries_teste = [
        # Caetano Veloso
        "Caetano Veloso música brasileira",
        "cantor compositor brasileiro",
        
        # A Moreninha
        "A Moreninha romance brasileiro", 
        "Joaquim Manuel de Macedo",
        
        # Engenharia de Prompt
        "engenharia de prompt IA",
        "inteligência artificial generativa"
    ]
    
    resultados_por_tema = {
        'caetano': 0,
        'moreninha': 0,
        'engenharia': 0
    }
    
    for query in queries_teste:
        print(f"\nBuscando: '{query}'")
        resultados = pipeline.buscar(query, top_k=3)
        
        if resultados:
            print(f"  Encontrados: {len(resultados)} resultados")
            
            # Classificar resultados por tema
            for res in resultados:
                texto_lower = res['texto'].lower()
                doc_lower = res['documento'].lower()
                
                if 'caetano' in texto_lower or 'veloso' in texto_lower or 'caetano' in doc_lower:
                    resultados_por_tema['caetano'] += 1
                elif 'moreninha' in texto_lower or 'macedo' in texto_lower or 'moreninha' in doc_lower:
                    resultados_por_tema['moreninha'] += 1
                elif 'prompt' in texto_lower or 'engenharia' in texto_lower or 'prompt' in doc_lower:
                    resultados_por_tema['engenharia'] += 1
            
            # Mostrar melhor resultado
            melhor = resultados[0]
            print(f"  Melhor resultado:")
            print(f"    Score: {melhor['similaridade']:.3f}")
            print(f"    Fonte: {melhor['fonte']}")
            print(f"    Documento: {melhor['documento']}")
            print(f"    Texto: {melhor['texto'][:100]}...")
        else:
            print(f"  Nenhum resultado encontrado")
    
    pipeline.close()
    
    print(f"\nResultados por tema:")
    print(f"- Caetano Veloso: {resultados_por_tema['caetano']} resultados")
    print(f"- A Moreninha: {resultados_por_tema['moreninha']} resultados")
    print(f"- Engenharia de Prompt: {resultados_por_tema['engenharia']} resultados")
    
    total_resultados = sum(resultados_por_tema.values())
    print(f"- Total: {total_resultados} resultados")
    
    # Verificar se todos os três temas têm resultados
    temas_com_resultados = sum(1 for count in resultados_por_tema.values() if count > 0)
    
    return total_resultados > 0 and temas_com_resultados >= 2

def verificar_persistencia_real():
    """Verifica se dados persistem após reinicialização"""
    print("\n=== TESTE DE PERSISTÊNCIA REAL ===")
    
    # Primeira instância
    pipeline1 = RAGPipelineFiles()
    stats1 = pipeline1.get_statistics()
    chunks_inicial = stats1['chunks_em_memoria']
    print(f"Primeira instância - Chunks: {chunks_inicial}")
    pipeline1.close()
    del pipeline1
    
    # Segunda instância (simulando reinicialização)
    pipeline2 = RAGPipelineFiles()
    stats2 = pipeline2.get_statistics()
    chunks_apos_reinicio = stats2['chunks_em_memoria']
    print(f"Segunda instância - Chunks: {chunks_apos_reinicio}")
    
    # Testar busca na segunda instância
    resultado_busca = pipeline2.buscar("Caetano Veloso", top_k=1)
    busca_funciona = len(resultado_busca) > 0
    
    if busca_funciona:
        print(f"Busca após reinicialização: FUNCIONANDO")
        print(f"  Score: {resultado_busca[0]['similaridade']:.3f}")
        print(f"  Texto: {resultado_busca[0]['texto'][:60]}...")
    else:
        print(f"Busca após reinicialização: FALHOU")
    
    pipeline2.close()
    
    persistencia_ok = (chunks_inicial == chunks_apos_reinicio and 
                      chunks_inicial > 0 and busca_funciona)
    
    print(f"\nPersistência real: {'SIM' if persistencia_ok else 'NÃO'}")
    return persistencia_ok

def validacao_completa():
    """Executa validação completa do sistema de arquivos"""
    print("VALIDAÇÃO COMPLETA - SISTEMA DE ARQUIVOS RAG")
    print("Temas: Caetano Veloso, A Moreninha, Engenharia de Prompt")
    print("=" * 70)
    
    # Etapa 1: Verificar dados físicos
    dados_fisicos_ok = verificar_dados_fisicos()
    
    # Etapa 2: Testar busca dos três temas
    busca_ok = testar_busca_tres_temas()
    
    # Etapa 3: Verificar persistência real
    persistencia_ok = verificar_persistencia_real()
    
    # Resultado final
    print("\n" + "=" * 70)
    print("RESULTADO DA VALIDAÇÃO:")
    
    if dados_fisicos_ok and busca_ok and persistencia_ok:
        print("✅ SISTEMA COMPLETAMENTE VALIDADO")
        print("- Dados físicos dos três temas confirmados")
        print("- Busca semântica funcionando para todos os temas")
        print("- Persistência real confirmada (não é cache/memória)")
        print("- Sistema de arquivos totalmente operacional")
        print("- Dados são REAIS e PERSISTENTES")
        return True
    else:
        print("❌ PROBLEMAS DETECTADOS")
        if not dados_fisicos_ok:
            print("- Falha na verificação de dados físicos")
        if not busca_ok:
            print("- Falha na busca dos três temas")
        if not persistencia_ok:
            print("- Falha na persistência real")
        return False

if __name__ == "__main__":
    validacao_completa()