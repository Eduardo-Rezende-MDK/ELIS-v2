#!/usr/bin/env python3
"""
Teste do sistema RAG com tema Divina Comedia
"""

from rag_pipeline import RAGPipeline

def teste_divina_comedia():
    """Testa o sistema RAG com tema Divina Comedia"""
    print("=== TESTE RAG - DIVINA COMEDIA ===")
    
    # Criar pipeline
    pipeline = RAGPipeline()
    
    # Tema para teste
    tema = "Divina Comedia"
    print(f"Tema: {tema}")
    
    # Executar pipeline
    print("\nExecutando pipeline...")
    relatorio = pipeline.executar_pipeline_completo(tema, max_docs_por_fonte=3)
    
    if 'erro' in relatorio:
        print(f"Erro: {relatorio['erro']}")
        return
    
    # Mostrar resultados
    print(f"\n=== RESULTADOS ===")
    print(f"Documentos coletados: {relatorio['documentos']['total']}")
    print(f"Chunks gerados: {relatorio['chunks']['total']}")
    print(f"Tempo: {relatorio['tempo_execucao_segundos']:.2f}s")
    
    # Distribuicao por fonte
    fontes = relatorio['documentos']['estatisticas'].get('distribuicao_fontes', {})
    print(f"\nFontes:")
    for fonte, count in fontes.items():
        print(f"- {fonte}: {count} documentos")
    
    # Testar perguntas
    perguntas = [
        "O que e a Divina Comedia?",
        "Quem e Dante Alighieri?",
        "Quais sao as tres partes da obra?",
        "O que representa o Inferno?"
    ]
    
    print(f"\n=== TESTANDO PERGUNTAS ===")
    
    for pergunta in perguntas:
        print(f"\nPergunta: {pergunta}")
        
        # Buscar resposta
        resultados = pipeline.buscar(pergunta, top_k=2)
        
        if resultados:
            melhor = resultados[0]
            print(f"Resposta (sim: {melhor['similaridade']:.3f}):")
            print(f"Fonte: {melhor['fonte']}")
            print(f"Texto: {melhor['texto'][:200]}...")
        else:
            print("Nenhuma resposta encontrada")
    
    print(f"\n=== TESTE CONCLUIDO ===")

if __name__ == "__main__":
    teste_divina_comedia()