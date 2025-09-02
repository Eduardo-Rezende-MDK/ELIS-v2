# Sistema RAG Simplificado

Sistema de Retrieval-Augmented Generation (RAG) simplificado para coleta, processamento e busca de conhecimento.

## Funcionalidades

- **Coleta Multi-Fonte**: Wikipedia (português) e ArXiv
- **Processamento Inteligente**: Chunking por sentenças, embeddings com SentenceTransformers
- **Busca Semântica**: Similaridade coseno para encontrar conteúdo relevante
- **Pipeline Completo**: Integração automática de todas as etapas

## Estrutura dos Arquivos

```
RAG/
├── requirements.txt           # Dependências necessárias
├── instalar_dependencias.py   # Instalador automático
├── coletor_basico.py          # Coleta de dados
├── processador_documentos.py  # Processamento e embeddings
├── rag_pipeline.py            # Pipeline principal
├── exemplo_uso.py             # Exemplos de uso
└── README.md                  # Esta documentação
```

## Instalação

1. **Instalar dependências**:
```bash
python instalar_dependencias.py
```

2. **Verificar instalação**:
O script automaticamente verifica se todas as dependências foram instaladas corretamente.

## Uso Básico

### Exemplo Simples

```python
from rag_pipeline import RAGPipeline

# Criar pipeline
pipeline = RAGPipeline()

# Executar pipeline completo
relatorio = pipeline.executar_pipeline_completo("machine learning", max_docs_por_fonte=3)

# Fazer perguntas
resultados = pipeline.buscar("O que é machine learning?", top_k=3)

# Obter contexto
contexto = pipeline.obter_contexto_para_query("Como funciona IA?", max_chars=1000)
```

### Executar Exemplo

```bash
python exemplo_uso.py
```

## Componentes Principais

### 1. ColetorBasico

**Funcionalidades**:
- Coleta artigos da Wikipedia em português
- Coleta papers do ArXiv
- Rate limiting automático
- Filtragem por tamanho mínimo

**Uso**:
```python
from coletor_basico import ColetorBasico

coletor = ColetorBasico()
documentos = coletor.coletar_por_tema("inteligência artificial", max_por_fonte=5)
```

### 2. ProcessadorDocumentos

**Funcionalidades**:
- Limpeza e normalização de texto
- Chunking por sentenças com overlap
- Geração de embeddings com SentenceTransformers
- Busca por similaridade coseno

**Uso**:
```python
from processador_documentos import ProcessadorDocumentos

processador = ProcessadorDocumentos()
chunks = processador.processar_documentos(documentos)
resultados = processador.buscar_similares("query", top_k=5)
```

### 3. RAGPipeline

**Funcionalidades**:
- Integração completa de coleta e processamento
- Salvamento automático de resultados
- Geração de relatórios
- Sistema de busca e resposta

**Uso**:
```python
from rag_pipeline import RAGPipeline

pipeline = RAGPipeline()
relatorio = pipeline.executar_pipeline_completo("tema")
resposta = pipeline.responder_pergunta("pergunta")
```

## Configurações

### Modelo de Embeddings

Por padrão usa `sentence-transformers/all-MiniLM-L6-v2`. Para alterar:

```python
pipeline = RAGPipeline(modelo_embedding="outro-modelo")
```

### Parâmetros de Chunking

```python
processador = ProcessadorDocumentos()
chunks = processador.dividir_em_chunks(
    texto, 
    tamanho_max=500,  # Tamanho máximo do chunk
    overlap=50        # Sobreposição entre chunks
)
```

### Limites de Coleta

```python
# Limitar documentos por fonte
documentos = coletor.coletar_por_tema("tema", max_por_fonte=10)

# Limitar resultados de busca
resultados = pipeline.buscar("query", top_k=5)
```

## Saídas do Sistema

### Estrutura de Resultados

O pipeline cria uma pasta `resultados_tema/` com:

- `documentos_originais.txt`: Documentos coletados
- `chunks_processados.txt`: Chunks gerados
- `relatorio.json`: Estatísticas e metadados

### Formato do Relatório

```json
{
  "tema": "machine learning",
  "timestamp": "2025-01-09T20:45:00",
  "tempo_execucao_segundos": 45.2,
  "documentos": {
    "total": 8,
    "estatisticas": {
      "distribuicao_fontes": {
        "wikipedia": 5,
        "arxiv": 3
      }
    }
  },
  "chunks": {
    "total": 42,
    "estatisticas": {
      "tamanho_medio": 387.5
    }
  }
}
```

## Limitações

- **Fontes**: Apenas Wikipedia (PT) e ArXiv
- **Idiomas**: Processamento otimizado para português
- **Armazenamento**: Em memória (não persistente entre execuções)
- **Busca**: Apenas similaridade semântica (sem filtros avançados)

## Dependências Principais

- `sentence-transformers`: Embeddings
- `requests`: HTTP requests
- `beautifulsoup4`: Web scraping
- `arxiv`: API do ArXiv
- `nltk`: Processamento de linguagem natural
- `numpy`: Operações matemáticas
- `pandas`: Manipulação de dados

## Exemplos de Uso

### 1. Pesquisa Acadêmica

```python
pipeline = RAGPipeline()
relatorio = pipeline.executar_pipeline_completo("quantum computing")
contexto = pipeline.obter_contexto_para_query("What is quantum supremacy?")
```

### 2. Análise de Tópicos

```python
# Coletar sobre múltiplos temas relacionados
temas = ["machine learning", "deep learning", "neural networks"]

for tema in temas:
    relatorio = pipeline.executar_pipeline_completo(tema, max_docs_por_fonte=3)
    print(f"{tema}: {relatorio['chunks']['total']} chunks")
```

### 3. Sistema de Perguntas e Respostas

```python
pipeline = RAGPipeline()
pipeline.executar_pipeline_completo("inteligência artificial")

perguntas = [
    "O que é IA?",
    "Como funciona machine learning?",
    "Quais são as aplicações da IA?"
]

for pergunta in perguntas:
    resposta = pipeline.responder_pergunta(pergunta)
    print(f"P: {pergunta}")
    print(f"R: {resposta['resposta'][:200]}...")
```

## Troubleshooting

### Erro de Dependências

```bash
# Reinstalar dependências
python instalar_dependencias.py
```

### Erro de NLTK

```python
import nltk
nltk.download('punkt')
```

### Erro de Memória

- Reduzir `max_docs_por_fonte`
- Usar chunks menores (`tamanho_max=300`)
- Processar temas menores

### Sem Resultados

- Verificar conexão com internet
- Tentar termos em inglês para ArXiv
- Verificar se o tema existe na Wikipedia

## Próximos Passos

Para expandir o sistema:

1. **Mais Fontes**: Google Scholar, PubMed, repositórios institucionais
2. **Persistência**: Banco de dados para armazenar embeddings
3. **Interface Web**: Streamlit ou Flask para interface gráfica
4. **Filtros Avançados**: Por data, autor, tipo de documento
5. **Múltiplos Idiomas**: Suporte para outros idiomas
6. **Cache**: Sistema de cache para evitar reprocessamento

## Suporte

Para dúvidas ou problemas:

1. Verificar se todas as dependências estão instaladas
2. Consultar os exemplos em `exemplo_uso.py`
3. Verificar logs de erro nos arquivos de saída
4. Testar com temas simples primeiro