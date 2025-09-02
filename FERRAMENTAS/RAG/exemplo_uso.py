#!/usr/bin/env python3
"""
Exemplo de uso do sistema RAG simplificado
Demonstra as funcionalidades principais
"""

from rag_pipeline import RAGPipeline
import time

def exemplo_basico():
    """Exemplo basico de uso"""
    print("=== SISTEMA RAG SIMPLIFICADO ===")
    print("Exemplo de uso basico\n")
    
    # Criar pipeline
    print("Inicializando pipeline RAG...")
    pipeline = RAGPipeline()
    
    # Tema para pesquisa
    tema = "machine learning"
    print(f"Tema escolhido: {tema}")
    
    # Executar pipeline completo
    print("\nExecutando pipeline completo...")
    relatorio = pipeline.executar_pipeline_completo(tema, max_docs_por_fonte=2)
    
    if 'erro' in relatorio:
        print(f"Erro: {relatorio['erro']}")
        return
    
    # Mostrar resultados
    print("\n=== RESULTADOS DO PIPELINE ===")
    print(f"Documentos coletados: {relatorio['documentos']['total']}")
    print(f"Chunks gerados: {relatorio['chunks']['total']}")
    print(f"Tempo de execucao: {relatorio['tempo_execucao_segundos']:.2f}s")
    
    # Exemplo de perguntas
    perguntas = [
        "O que e machine learning?",
        "Como funciona aprendizado de maquina?"
    ]
    
    print("\n=== TESTANDO PERGUNTAS ===")
    
    for pergunta in perguntas:
        print(f"\nPergunta: {pergunta}")
        print("-" * 50)
        
        # Buscar documentos relevantes
        resultados = pipeline.buscar(pergunta, top_k=2)
        
        if resultados:
            print(f"Encontrados {len(resultados)} resultados:")
            for i, resultado in enumerate(resultados, 1):
                print(f"\n{i}. Fonte: {resultado['fonte']}")
                print(f"   Similaridade: {resultado['similaridade']:.3f}")
                print(f"   Documento: {resultado['documento']}")
                print(f"   Texto: {resultado['texto'][:200]}...")
        else:
            print("Nenhum resultado encontrado")
        
        # Obter contexto
        print("\nContexto relevante:")
        contexto = pipeline.obter_contexto_para_query(pergunta, max_chars=500)
        if contexto:
            print(contexto[:300] + "..." if len(contexto) > 300 else contexto)
        else:
            print("Nenhum contexto encontrado")
        
        time.sleep(1)  # Pausa para leitura

def exemplo_interativo():
    """Exemplo interativo com input do usuario"""
    print("=== MODO INTERATIVO ===")
    print("Digite um tema para pesquisa (ou 'sair' para encerrar)")
    
    pipeline = RAGPipeline()
    
    while True:
        tema = input("\nTema: ").strip()
        
        if tema.lower() in ['sair', 'exit', 'quit', '']:
            print("Encerrando...")
            break
            
        print(f"\nProcessando tema: {tema}")
        
        # Executar pipeline
        relatorio = pipeline.executar_pipeline_completo(tema, max_docs_por_fonte=2)
        
        if 'erro' in relatorio:
            print(f"Erro: {relatorio['erro']}")
            continue
            
        print(f"\nColetados {relatorio['documentos']['total']} documentos")
        print(f"Gerados {relatorio['chunks']['total']} chunks")
        
        # Perguntas interativas
        while True:
            pergunta = input("\nFaca uma pergunta (ou 'voltar' para novo tema): ").strip()
            
            if pergunta.lower() in ['voltar', 'back', '']:
                break
                
            # Buscar resposta
            resultados = pipeline.buscar(pergunta, top_k=1)
            
            if resultados:
                resultado = resultados[0]
                print(f"\nResposta encontrada (similaridade: {resultado['similaridade']:.3f}):")
                print(f"Fonte: {resultado['fonte']}")
                print(f"Texto: {resultado['texto']}")
            else:
                print("\nNenhuma resposta encontrada para sua pergunta.")

def exemplo_comparacao_fontes():
    """Exemplo comparando diferentes fontes"""
    print("=== COMPARACAO DE FONTES ===")
    
    pipeline = RAGPipeline()
    
    # Tema tecnico
    tema = "neural networks"
    print(f"Analisando fontes para: {tema}")
    
    relatorio = pipeline.executar_pipeline_completo(tema, max_docs_por_fonte=3)
    
    if 'erro' in relatorio:
        print(f"Erro: {relatorio['erro']}")
        return
        
    # Analisar distribuicao por fonte
    stats_docs = relatorio['documentos']['estatisticas']
    stats_chunks = relatorio['chunks']['estatisticas']
    
    print("\n=== DISTRIBUICAO POR FONTE ===")
    print("Documentos:")
    for fonte, count in stats_docs.get('distribuicao_fontes', {}).items():
        print(f"  {fonte}: {count} documentos")
        
    print("\nChunks:")
    for fonte, count in stats_chunks.get('distribuicao_fontes', {}).items():
        print(f"  {fonte}: {count} chunks")
    
    # Testar pergunta especifica
    pergunta = "What are neural networks?"
    print(f"\nTestando pergunta: {pergunta}")
    
    resultados = pipeline.buscar(pergunta, top_k=5)
    
    print("\nResultados por fonte:")
    for resultado in resultados:
        print(f"  [{resultado['fonte']}] Sim: {resultado['similaridade']:.3f}")
        print(f"    {resultado['texto'][:100]}...\n")

def menu_principal():
    """Menu principal de exemplos"""
    print("=== SISTEMA RAG - EXEMPLOS ===")
    print("Escolha um exemplo:")
    print("1. Exemplo basico")
    print("2. Modo interativo")
    print("3. Comparacao de fontes")
    print("4. Sair")
    
    while True:
        try:
            opcao = input("\nOpcao (1-4): ").strip()
            
            if opcao == '1':
                exemplo_basico()
            elif opcao == '2':
                exemplo_interativo()
            elif opcao == '3':
                exemplo_comparacao_fontes()
            elif opcao == '4':
                print("Encerrando...")
                break
            else:
                print("Opcao invalida. Tente novamente.")
                
        except KeyboardInterrupt:
            print("\nEncerrando...")
            break
        except Exception as e:
            print(f"Erro: {e}")

if __name__ == "__main__":
    # Executar exemplo basico por padrao
    # Para menu interativo, descomente a linha abaixo:
    # menu_principal()
    
    exemplo_basico()