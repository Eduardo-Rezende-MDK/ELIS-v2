#!/usr/bin/env python3
"""
Processador de documentos para sistema RAG
Realiza chunking, embeddings e preparacao para busca
"""

import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
from dataclasses import dataclass
import re
import nltk
from nltk.tokenize import sent_tokenize
from coletor_basico import Documento

# Download necessario do NLTK (executar uma vez)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

@dataclass
class Chunk:
    """Classe para representar um chunk de texto"""
    texto: str
    embedding: np.ndarray
    documento_origem: str
    fonte: str
    posicao: int
    tamanho: int
    
class ProcessadorDocumentos:
    """Processador de documentos com embeddings"""
    
    def __init__(self, modelo_embedding: str = "sentence-transformers/all-MiniLM-L6-v2"):
        print(f"Carregando modelo de embeddings: {modelo_embedding}")
        self.modelo = SentenceTransformer(modelo_embedding)
        self.chunks = []
        
    def limpar_texto(self, texto: str) -> str:
        """Limpa e normaliza texto"""
        # Remover caracteres especiais excessivos
        texto = re.sub(r'\s+', ' ', texto)  # Normalizar espacos
        texto = re.sub(r'[^\w\s.,!?;:()-]', '', texto)  # Manter apenas chars basicos
        texto = texto.strip()
        
        return texto
    
    def dividir_em_chunks(self, texto: str, tamanho_max: int = 500, overlap: int = 50) -> List[str]:
        """Divide texto em chunks por sentencas"""
        # Tokenizar em sentencas em portugues
        try:
            sentencas = sent_tokenize(texto, language='portuguese')
        except LookupError:
            # Se nao tiver portugues, usar tokenizacao simples por pontos
            sentencas = [s.strip() for s in texto.split('.') if s.strip()]
        
        chunks = []
        chunk_atual = ""
        
        for sentenca in sentencas:
            # Se adicionar a sentenca nao exceder o tamanho maximo
            if len(chunk_atual + " " + sentenca) <= tamanho_max:
                chunk_atual += " " + sentenca if chunk_atual else sentenca
            else:
                # Salvar chunk atual se nao estiver vazio
                if chunk_atual:
                    chunks.append(chunk_atual.strip())
                
                # Iniciar novo chunk
                chunk_atual = sentenca
        
        # Adicionar ultimo chunk
        if chunk_atual:
            chunks.append(chunk_atual.strip())
            
        # Aplicar overlap se necessario
        if overlap > 0 and len(chunks) > 1:
            chunks_com_overlap = []
            for i, chunk in enumerate(chunks):
                if i == 0:
                    chunks_com_overlap.append(chunk)
                else:
                    # Pegar ultimas palavras do chunk anterior
                    palavras_anteriores = chunks[i-1].split()[-overlap:]
                    chunk_com_overlap = " ".join(palavras_anteriores) + " " + chunk
                    chunks_com_overlap.append(chunk_com_overlap)
            return chunks_com_overlap
            
        return chunks
    
    def processar_documento(self, documento: Documento) -> List[Chunk]:
        """Processa um documento em chunks com embeddings"""
        # Limpar texto
        texto_limpo = self.limpar_texto(documento.conteudo)
        
        if len(texto_limpo) < 50:  # Muito pequeno
            return []
            
        # Dividir em chunks
        chunks_texto = self.dividir_em_chunks(texto_limpo)
        
        # Criar embeddings
        embeddings = self.modelo.encode(chunks_texto)
        
        # Criar objetos Chunk
        chunks = []
        for i, (texto_chunk, embedding) in enumerate(zip(chunks_texto, embeddings)):
            chunk = Chunk(
                texto=texto_chunk,
                embedding=embedding,
                documento_origem=documento.titulo,
                fonte=documento.fonte,
                posicao=i,
                tamanho=len(texto_chunk)
            )
            chunks.append(chunk)
            
        return chunks
    
    def processar_documentos(self, documentos: List[Documento]) -> List[Chunk]:
        """Processa lista de documentos"""
        todos_chunks = []
        
        print(f"Processando {len(documentos)} documentos...")
        
        for i, documento in enumerate(documentos, 1):
            print(f"Processando documento {i}/{len(documentos)}: {documento.titulo[:50]}...")
            
            chunks = self.processar_documento(documento)
            todos_chunks.extend(chunks)
            
            print(f"  Gerados {len(chunks)} chunks")
            
        self.chunks = todos_chunks
        print(f"\nTotal de chunks processados: {len(todos_chunks)}")
        
        return todos_chunks
    
    def buscar_similares(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Busca chunks similares a uma query"""
        if not self.chunks:
            return []
            
        # Gerar embedding da query
        query_embedding = self.modelo.encode([query])[0]
        
        # Calcular similaridades
        similaridades = []
        for chunk in self.chunks:
            # Similaridade coseno
            sim = np.dot(query_embedding, chunk.embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(chunk.embedding)
            )
            similaridades.append({
                'chunk': chunk,
                'similaridade': float(sim)
            })
            
        # Ordenar por similaridade
        similaridades.sort(key=lambda x: x['similaridade'], reverse=True)
        
        # Retornar top_k
        resultados = []
        for item in similaridades[:top_k]:
            chunk = item['chunk']
            resultados.append({
                'texto': chunk.texto,
                'similaridade': item['similaridade'],
                'documento': chunk.documento_origem,
                'fonte': chunk.fonte,
                'posicao': chunk.posicao
            })
            
        return resultados
    
    def obter_contexto(self, query: str, max_chars: int = 2000) -> str:
        """Obtem contexto relevante para uma query"""
        resultados = self.buscar_similares(query, top_k=10)
        
        contexto = ""
        chars_usados = 0
        
        for resultado in resultados:
            texto = resultado['texto']
            if chars_usados + len(texto) <= max_chars:
                contexto += f"\n[{resultado['fonte']}] {texto}\n"
                chars_usados += len(texto)
            else:
                break
                
        return contexto.strip()
    
    def salvar_chunks(self, arquivo: str = "chunks_processados.txt"):
        """Salva chunks processados em arquivo"""
        try:
            with open(arquivo, 'w', encoding='utf-8') as f:
                for i, chunk in enumerate(self.chunks, 1):
                    f.write(f"=== CHUNK {i} ===\n")
                    f.write(f"Documento: {chunk.documento_origem}\n")
                    f.write(f"Fonte: {chunk.fonte}\n")
                    f.write(f"Posicao: {chunk.posicao}\n")
                    f.write(f"Tamanho: {chunk.tamanho}\n")
                    f.write(f"Texto:\n{chunk.texto}\n")
                    f.write("\n" + "="*50 + "\n\n")
                    
            print(f"Chunks salvos em: {arquivo}")
            
        except Exception as e:
            print(f"Erro ao salvar chunks: {e}")
    
    def obter_estatisticas(self) -> Dict[str, Any]:
        """Obtem estatisticas dos chunks"""
        if not self.chunks:
            return {}
            
        fontes = {}
        tamanhos = []
        
        for chunk in self.chunks:
            fontes[chunk.fonte] = fontes.get(chunk.fonte, 0) + 1
            tamanhos.append(chunk.tamanho)
            
        return {
            'total_chunks': len(self.chunks),
            'distribuicao_fontes': fontes,
            'tamanho_medio': np.mean(tamanhos) if tamanhos else 0,
            'tamanho_min': min(tamanhos) if tamanhos else 0,
            'tamanho_max': max(tamanhos) if tamanhos else 0
        }

def exemplo_uso():
    """Exemplo de uso do processador"""
    from coletor_basico import ColetorBasico
    
    # Coletar documentos
    coletor = ColetorBasico()
    documentos = coletor.coletar_por_tema("machine learning", max_por_fonte=2)
    
    if not documentos:
        print("Nenhum documento coletado")
        return
        
    # Processar documentos
    processador = ProcessadorDocumentos()
    chunks = processador.processar_documentos(documentos)
    
    # Salvar chunks
    processador.salvar_chunks("chunks_ml.txt")
    
    # Mostrar estatisticas
    stats = processador.obter_estatisticas()
    print("\nEstatisticas dos chunks:")
    for chave, valor in stats.items():
        print(f"  {chave}: {valor}")
    
    # Exemplo de busca
    print("\n=== EXEMPLO DE BUSCA ===")
    query = "o que e aprendizado de maquina?"
    resultados = processador.buscar_similares(query, top_k=3)
    
    print(f"Query: {query}")
    print(f"Encontrados {len(resultados)} resultados:")
    
    for i, resultado in enumerate(resultados, 1):
        print(f"\n{i}. Similaridade: {resultado['similaridade']:.3f}")
        print(f"   Fonte: {resultado['fonte']}")
        print(f"   Texto: {resultado['texto'][:200]}...")
    
    # Exemplo de contexto
    print("\n=== CONTEXTO GERADO ===")
    contexto = processador.obter_contexto(query, max_chars=1000)
    print(contexto[:500] + "..." if len(contexto) > 500 else contexto)

if __name__ == "__main__":
    exemplo_uso()