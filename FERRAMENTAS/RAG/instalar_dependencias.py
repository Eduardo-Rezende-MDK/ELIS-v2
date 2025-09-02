#!/usr/bin/env python3
"""
Instalador de dependencias para sistema RAG
Executa pip install das dependencias necessarias
"""

import subprocess
import sys
from pathlib import Path

def instalar_dependencias():
    """Instala as dependencias do requirements.txt"""
    
    # Caminho do requirements.txt
    requirements_path = Path(__file__).parent / "requirements.txt"
    
    if not requirements_path.exists():
        print("Erro: requirements.txt nao encontrado")
        return False
    
    print("Instalando dependencias do sistema RAG...")
    print(f"Arquivo: {requirements_path}")
    
    try:
        # Executar pip install
        cmd = [sys.executable, "-m", "pip", "install", "-r", str(requirements_path)]
        
        print(f"Executando: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        print("Instalacao concluida com sucesso!")
        print("Output:")
        print(result.stdout)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Erro na instalacao: {e}")
        print(f"Stderr: {e.stderr}")
        return False
    except Exception as e:
        print(f"Erro inesperado: {e}")
        return False

def verificar_instalacao():
    """Verifica se as principais dependencias estao instaladas"""
    
    dependencias_principais = [
        "numpy",
        "sklearn",
        "transformers", 
        "sentence_transformers",
        "faiss",
        "requests",
        "bs4",
        "pandas",
        "nltk",
        "arxiv",
        "tqdm",
        "yaml"
    ]
    
    print("Verificando instalacao das dependencias...")
    
    instaladas = []
    nao_instaladas = []
    
    for dep in dependencias_principais:
        try:
            __import__(dep)
            instaladas.append(dep)
            print(f"  OK: {dep}")
        except ImportError:
            nao_instaladas.append(dep)
            print(f"  ERRO: {dep} nao encontrado")
    
    print(f"\nResumo:")
    print(f"  Instaladas: {len(instaladas)}/{len(dependencias_principais)}")
    
    if nao_instaladas:
        print(f"  Nao instaladas: {', '.join(nao_instaladas)}")
        return False
    else:
        print("  Todas as dependencias estao instaladas!")
        return True

if __name__ == "__main__":
    print("=== INSTALADOR DE DEPENDENCIAS RAG ===")
    
    # Instalar dependencias
    sucesso = instalar_dependencias()
    
    if sucesso:
        print("\n=== VERIFICANDO INSTALACAO ===")
        verificar_instalacao()
    else:
        print("\nFalha na instalacao. Verifique os erros acima.")
        sys.exit(1)
    
    print("\n=== CONCLUIDO ===")