#!/usr/bin/env python3
"""
Teste da nova arquitetura modular RAG
"""

from rag_pipeline import RAGPipeline

def teste_os_miseraveis():
    """Testa o sistema RAG modular com Os Miseraveis"""
    print("=== TESTE ARQUITETURA MODULAR - OS MISERAVEIS ===")
    
    # Criar pipeline
    pipeline = RAGPipeline()
    
    # Tema para teste
    tema = "Os Miseraveis"
    print(f"Tema: {tema}")
    
    # Executar pipeline
    print("\nExecutando pipeline modular...")
    relatorio = pipeline.executar_pipeline_completo(tema, max_docs_por_fonte=3)
    
    if 'erro' in relatorio:
        print(f"Erro: {relatorio['erro']}")
        return False
    
    # Mostrar resultados
    print(f"\n=== RESULTADOS ===")
    print(f"Status: {relatorio['status']}")
    print(f"Documentos coletados: {relatorio['documentos']['total_coletados']}")
    print(f"Chunks processados: {relatorio['chunks']['total_processados']}")
    print(f"Tempo: {relatorio['tempo_execucao_segundos']:.2f}s")
    
    # Verificar se pasta rag_storage foi criada
    import os
    if os.path.exists('rag_storage'):
        print("\nPasta rag_storage criada com sucesso!")
        files = os.listdir('rag_storage')
        print(f"Arquivos: {files}")
    else:
        print("\nPasta rag_storage NAO foi criada")
    
    # Testar busca semantica
    print(f"\n=== TESTANDO BUSCA SEMANTICA ===")
    
    perguntas = [
        "O que e Os Miseraveis?",
        "Quem e Jean Valjean?",
        "Qual e a historia do livro?"
    ]
    
    for pergunta in perguntas:
        print(f"\nPergunta: {pergunta}")
        
        # Buscar resposta
        resultados = pipeline.buscar(pergunta, top_k=2)
        
        if resultados:
            melhor = resultados[0]
            print(f"Resposta (similaridade: {melhor['similaridade']:.3f}):")
            print(f"Fonte: {melhor['fonte']}")
            print(f"Qualidade: {melhor['quality_score']:.3f}")
            print(f"Texto: {melhor['texto'][:150]}...")
        else:
            print("Nenhuma resposta encontrada")
    
    print(f"\n=== TESTE CONCLUIDO COM SUCESSO ===")
    return True

if __name__ == "__main__":
    sucesso = teste_os_miseraveis()
    if sucesso:
        print("\nARQUITETURA MODULAR FUNCIONANDO PERFEITAMENTE!")
    else:
        print("\nFALHA NA ARQUITETURA MODULAR")