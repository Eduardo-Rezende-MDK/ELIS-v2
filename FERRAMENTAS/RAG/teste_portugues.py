#!/usr/bin/env python3
"""
Teste do sistema RAG com foco em conteudo em portugues
"""

from rag_pipeline import RAGPipeline

def teste_tema_portugues():
    """Testa o sistema com tema tipicamente brasileiro"""
    print("=== TESTE RAG EM PORTUGUES ===")
    
    # Criar pipeline
    pipeline = RAGPipeline()
    
    # Tema em portugues
    tema = "inteligencia artificial"
    print(f"Tema: {tema}")
    
    # Executar pipeline
    relatorio = pipeline.executar_pipeline_completo(tema, max_docs_por_fonte=3)
    
    if 'erro' in relatorio:
        print(f"Erro: {relatorio['erro']}")
        return
    
    print(f"\nResultados:")
    print(f"- Documentos coletados: {relatorio['documentos']['total']}")
    print(f"- Chunks gerados: {relatorio['chunks']['total']}")
    print(f"- Tempo: {relatorio['tempo_execucao_segundos']:.2f}s")
    
    # Distribuicao por fonte
    fontes = relatorio['documentos']['estatisticas'].get('distribuicao_fontes', {})
    print(f"\nDistribuicao por fonte:")
    for fonte, count in fontes.items():
        print(f"- {fonte}: {count} documentos")
    
    # Perguntas em portugues
    perguntas = [
        "O que e inteligencia artificial?",
        "Como funciona a IA?",
        "Quais sao as aplicacoes da inteligencia artificial?",
        "Qual a diferenca entre IA e machine learning?"
    ]
    
    print(f"\n=== TESTANDO PERGUNTAS EM PORTUGUES ===")
    
    for pergunta in perguntas:
        print(f"\nPergunta: {pergunta}")
        
        # Buscar resposta
        resultados = pipeline.buscar(pergunta, top_k=2)
        
        if resultados:
            melhor_resultado = resultados[0]
            print(f"Melhor resultado:")
            print(f"- Fonte: {melhor_resultado['fonte']}")
            print(f"- Similaridade: {melhor_resultado['similaridade']:.3f}")
            print(f"- Documento: {melhor_resultado['documento']}")
            print(f"- Texto: {melhor_resultado['texto'][:150]}...")
            
            # Verificar se e conteudo em portugues
            texto = melhor_resultado['texto'].lower()
            palavras_pt = ['que', 'uma', 'para', 'com', 'por', 'dos', 'das', 'como', 'mais']
            score_pt = sum(1 for palavra in palavras_pt if palavra in texto)
            
            if score_pt >= 3:
                print(f"- Status: CONTEUDO EM PORTUGUES (score: {score_pt})")
            else:
                print(f"- Status: Possivel conteudo em ingles (score: {score_pt})")
        else:
            print("Nenhum resultado encontrado")
    
    print(f"\n=== ANALISE DE QUALIDADE ===")
    
    # Contar chunks por fonte
    chunks_stats = relatorio['chunks']['estatisticas'].get('distribuicao_fontes', {})
    total_chunks = relatorio['chunks']['total']
    
    print(f"Chunks por fonte:")
    for fonte, count in chunks_stats.items():
        percentual = (count / total_chunks) * 100 if total_chunks > 0 else 0
        print(f"- {fonte}: {count} chunks ({percentual:.1f}%)")
    
    # Verificar se Wikipedia em portugues esta funcionando
    wiki_docs = fontes.get('wikipedia', 0)
    if wiki_docs > 0:
        print(f"\nSUCESSO: Wikipedia em portugues funcionando ({wiki_docs} documentos)")
    else:
        print(f"\nAVISO: Wikipedia em portugues nao retornou documentos")
    
    print(f"\n=== TESTE CONCLUIDO ===")

if __name__ == "__main__":
    teste_tema_portugues()