# FLUXO DO SISTEMA RAG - EXPLICADO

## RESUMO: DIVINA COMEDIA

A Divina Comedia e um poema epico de Dante Alighieri (1265-1321), considerado uma das maiores obras da literatura mundial. A obra narra a jornada de Dante atraves de tres reinos do alem:

- **INFERNO**: Dante desce pelos nove circulos do inferno, guiado pelo poeta Virgilio, encontrando pecadores punidos conforme seus crimes
- **PURGATORIO**: Dante sobe a montanha do purgatorio, onde as almas se purificam dos sete pecados capitais
- **PARAISO**: Dante ascende pelos nove ceus do paraiso, guiado por Beatriz, ate encontrar Deus

A obra e uma alegoria da jornada da alma humana em busca da salvacao, combinando teologia crista, filosofia aristotelica e mitologia classica.

---

## FLUXO DO SISTEMA RAG - PROCESSAMENTO PASSO A PASSO

### ENTRADA: Usuario pergunta "O que e a Divina Comedia?"

### 1. COLETA DE DADOS (sources/) - DETALHADO

**1.1 WIKIPEDIA (sources/web_collector.py)**
- URL: https://pt.wikipedia.org/w/api.php
- Parametros: action=query, list=search, srsearch="Divina Comedia", srlimit=3
- Busca retorna: "Divina Comedia", "Inferno (Divina Comedia)", "Belchior"
- Segunda requisicao: prop=extracts, explaintext=True para conteudo completo
- Resultado: 3 documentos em portugues com milhares de caracteres

**1.2 ARXIV (sources/academic_collector.py)**
- Biblioteca Python: arxiv.Search(query="Divina Comedia", max_results=3)
- Busca retorna: artigos academicos em ingles sobre analises da obra
- Artigos: "Computational Analysis of Gender Depiction", "De Divino Errore", "Leonardo's drawings"
- Extrai: titulo, abstract, autores, data, categorias, DOI
- Resultado: 3 documentos academicos com abstracts cientificos

**1.3 PROCESSAMENTO INICIAL**
- Cada documento vira objeto RawDocument com metadados completos
- Calcula quality_score baseado em tamanho, fonte, metadados
- Total coletado: 6 documentos (3 Wikipedia + 3 ArXiv)

**NOTA IMPORTANTE - EXPANSAO DE PROVEDORES:**
O sistema pode ser expandido com novos coletores:
- **PubMed**: Artigos medicos (sources/academic_collector.py)
- **Semantic Scholar**: Papers cientificos com citacoes
- **Google Scholar**: Busca academica ampla
- **Repositorios Institucionais**: USP, UNICAMP, UFRJ
- **Bibliotecas Digitais**: Biblioteca Nacional, Europeana
- **APIs de Noticias**: G1, Folha, BBC Brasil
- **Bases Governamentais**: Portal Brasileiro de Dados Abertos
- **Redes Sociais**: Twitter Academic API, Reddit
Cada novo provedor requer implementacao de coletor especializado.

### 2. LIMPEZA DE TEXTO (processing/document_processor.py)
- Remove HTML, URLs, caracteres especiais
- Normaliza espacos em branco
- Filtra documentos muito pequenos ou de baixa qualidade

### 3. CHUNKING - DIVISAO EM PEDACOS (processing/document_processor.py)
- Divide cada documento em pedacos menores (chunks)
- Usa divisao por sentencas: "A Divina Comedia e um poema..." vira um chunk
- Cada chunk tem 100-500 caracteres
- Cria 12 chunks no total dos 6 documentos

### 4. EMBEDDINGS - TRANSFORMACAO EM NUMEROS (processing/document_processor.py)
- Cada chunk de texto vira um vetor de 384 numeros
- Usa modelo SentenceTransformers para converter texto em numeros
- Textos similares ficam com numeros similares
- Exemplo: "Dante" e "poeta" ficam proximos numericamente

### 5. ARMAZENAMENTO VETORIAL (storage/vector_store.py) - DETALHADO

**5.1 O QUE E FAISS:**
- FAISS (Facebook AI Similarity Search) e biblioteca do Facebook para busca vetorial
- Armazena os 12 vetores de 384 dimensoes (embeddings dos chunks)
- Permite busca rapida por similaridade coseno em milissegundos
- Usa IndexFlatIP (Inner Product) para calcular similaridade diretamente

**5.2 COMO FUNCIONA:**
- Normaliza vetores com faiss.normalize_L2 para similaridade coseno
- Quando pergunta "O que e Divina Comedia?", compara vetor da pergunta com 12 armazenados
- Retorna chunks mais similares em ordem decrescente de score
- Encontrou chunk mais relevante (score 0.763) instantaneamente

**5.3 ONDE SAO SALVOS OS INDICES:**
- Arquivos locais na pasta ./rag_storage/
- faiss_index.bin (indice vetorial binario)
- chunks.pkl (chunks em formato pickle)
- metadata.json (metadados em JSON)
- Persistencia local garante velocidade maxima e privacidade total

**NOTA IMPORTANTE - BANCOS VETORIAIS:**
Para sistemas maiores existem bancos vetoriais especializados como Pinecone, Weaviate, Chroma e Qdrant, mas sao necessidades ainda distantes. FAISS local e ideal para desenvolvimento e uso pessoal com milhares de documentos, oferecendo velocidade maxima sem latencia de rede.

### 6. BUSCA SEMANTICA (storage/vector_store.py)
- Pergunta "O que e a Divina Comedia?" vira vetor de numeros
- Sistema compara esse vetor com os 12 vetores guardados
- Encontra os vetores mais similares (cosine similarity)
- Retorna os chunks de texto correspondentes

### 7. RANKING E FILTRAGEM (rag_pipeline.py)
- Ordena resultados por similaridade (0.763 = muito similar)
- Filtra resultados com similaridade muito baixa
- Pega os 2-5 melhores resultados

### 8. RESPOSTA FINAL (rag_pipeline.py)
- Retorna o chunk mais similar: "A Divina Comedia e um poema..."
- Inclui metadados: fonte (Wikipedia), similaridade (0.763)
- Usuario recebe resposta relevante em portugues

---

## ARQUIVOS GERADOS NO TESTE

### resultados_Divina_Comedia/
- **documentos_originais.txt**: Os 6 documentos coletados completos
- **chunks_processados.txt**: Os 12 pedacos de texto processados
- **relatorio.json**: Estatisticas do processamento (tempo, quantidades, etc.)

---

## VANTAGENS DO SISTEMA RAG

1. **BUSCA SEMANTICA**: Entende significado, nao apenas palavras exatas
2. **MULTI-FONTE**: Combina Wikipedia + artigos academicos
3. **PORTUGUES**: Prioriza conteudo em portugues
4. **RAPIDO**: Busca em milissegundos depois de processado
5. **ESCALAVEL**: Pode processar milhares de documentos

---

## COMPONENTES TECNICOS

- **models/**: Classes de dados (RawDocument, ProcessedChunk, SearchResult)
- **sources/**: Coletores (Wikipedia, ArXiv, APIs)
- **processing/**: Processamento (limpeza, chunking, embeddings)
- **storage/**: Armazenamento (FAISS, busca vetorial)
- **SentenceTransformers**: Modelo de IA para embeddings
- **FAISS**: Biblioteca Facebook para busca vetorial rapida
- **NLTK**: Biblioteca para processamento de linguagem natural

---

## EXEMPLO PRATICO

**INPUT**: "Quem e Dante?"
**PROCESSO**: 
1. Converte pergunta em vetor [0.1, -0.3, 0.8, ...]
2. Compara com vetores dos chunks guardados
3. Encontra chunk similar: "Dante Alighieri foi um poeta..."
4. Retorna resposta com score 0.650

**OUTPUT**: Texto relevante sobre Dante da Wikipedia em portugues

---

**NOTA**: Numeros mencionados (1-8) correspondem aos passos principais do fluxo RAG.
Cada numero pode ser explicado em mais detalhes conforme necessario.