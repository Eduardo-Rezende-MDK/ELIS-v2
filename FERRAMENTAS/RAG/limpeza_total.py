#!/usr/bin/env python3
"""
Script de limpeza total do sistema RAG
Remove todos os dados: arquivos, pastas, SQLite, cache Python
"""

import os
import sys
import time
import shutil
from pathlib import Path
import sqlite3
import gc

def fechar_todas_conexoes():
    """Fecha todas as conexões possíveis"""
    print("=== FECHANDO TODAS AS CONEXÕES ===")
    
    try:
        # Importar e fechar componentes do sistema
        from storage.sqlite_manager import SQLiteManager
        from storage.vector_store import RAGVectorStore
        from rag_pipeline import RAGPipeline
        
        # Fechar múltiplas instâncias
        for i in range(5):
            try:
                manager = SQLiteManager()
                manager.close()
                del manager
                
                vector = RAGVectorStore()
                vector.close()
                del vector
                
                pipeline = RAGPipeline()
                pipeline.close()
                del pipeline
                
            except Exception as e:
                print(f"Tentativa {i+1}: {e}")
        
        print("Conexões fechadas")
        
    except Exception as e:
        print(f"Erro ao fechar conexões: {e}")
    
    # Forçar garbage collection agressivo
    for i in range(10):
        gc.collect()
        time.sleep(0.2)
    
    print("Garbage collection executado")

def limpar_cache_python():
    """Remove cache Python"""
    print("\n=== LIMPANDO CACHE PYTHON ===")
    
    try:
        # Remover arquivos __pycache__
        for root, dirs, files in os.walk('.'):
            for dir_name in dirs[:]:
                if dir_name == '__pycache__':
                    pycache_path = os.path.join(root, dir_name)
                    try:
                        shutil.rmtree(pycache_path)
                        print(f"Removido: {pycache_path}")
                    except Exception as e:
                        print(f"Erro ao remover {pycache_path}: {e}")
                    dirs.remove(dir_name)
        
        # Remover arquivos .pyc
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.endswith('.pyc'):
                    pyc_path = os.path.join(root, file)
                    try:
                        os.remove(pyc_path)
                        print(f"Removido: {pyc_path}")
                    except Exception as e:
                        print(f"Erro ao remover {pyc_path}: {e}")
        
        print("Cache Python limpo")
        
    except Exception as e:
        print(f"Erro na limpeza de cache: {e}")

def limpar_banco_sqlite():
    """Remove completamente o banco SQLite"""
    print("\n=== LIMPANDO BANCO SQLite ===")
    
    db_path = Path("rag_storage/rag_database.db")
    
    if db_path.exists():
        try:
            # Tentar conectar e dropar todas as tabelas
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Obter lista de tabelas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            # Dropar cada tabela
            for table in tables:
                table_name = table[0]
                cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
                print(f"Tabela removida: {table_name}")
            
            conn.commit()
            conn.close()
            
            # Aguardar e remover arquivo
            time.sleep(1)
            db_path.unlink()
            print(f"Banco SQLite removido: {db_path}")
            
        except Exception as e:
            print(f"Erro ao limpar SQLite: {e}")
            # Tentar remoção forçada
            try:
                time.sleep(2)
                db_path.unlink()
                print(f"Remoção forçada: {db_path}")
            except Exception as e2:
                print(f"Falha na remoção forçada: {e2}")
    else:
        print("Banco SQLite não encontrado")

def limpar_arquivos_dados():
    """Remove todos os arquivos de dados"""
    print("\n=== LIMPANDO ARQUIVOS DE DADOS ===")
    
    # Remover pasta rag_storage
    storage_path = Path("rag_storage")
    if storage_path.exists():
        try:
            shutil.rmtree(storage_path)
            print(f"Pasta removida: {storage_path}")
        except Exception as e:
            print(f"Erro ao remover pasta: {e}")
            # Tentar remover arquivos individualmente
            for file in storage_path.glob("*"):
                if file.is_file():
                    try:
                        file.unlink()
                        print(f"Arquivo removido: {file.name}")
                    except Exception as e2:
                        print(f"Erro ao remover {file.name}: {e2}")
    
    # Remover pastas de resultados
    for pasta in Path(".").glob("resultados_*"):
        if pasta.is_dir():
            try:
                shutil.rmtree(pasta)
                print(f"Pasta removida: {pasta.name}")
            except Exception as e:
                print(f"Erro ao remover {pasta.name}: {e}")
    
    # Remover arquivos temporários
    temp_files = [
        "chunks.pkl",
        "metadata.json",
        "faiss_index.bin",
        "*.tmp",
        "*.log"
    ]
    
    for pattern in temp_files:
        for file in Path(".").glob(pattern):
            if file.is_file():
                try:
                    file.unlink()
                    print(f"Arquivo temporário removido: {file.name}")
                except Exception as e:
                    print(f"Erro ao remover {file.name}: {e}")

def verificar_limpeza():
    """Verifica se a limpeza foi bem-sucedida"""
    print("\n=== VERIFICAÇÃO DA LIMPEZA ===")
    
    problemas = []
    
    # Verificar pasta rag_storage
    if Path("rag_storage").exists():
        problemas.append("Pasta rag_storage ainda existe")
    
    # Verificar pastas de resultados
    resultados = list(Path(".").glob("resultados_*"))
    if resultados:
        problemas.append(f"Pastas de resultados ainda existem: {[p.name for p in resultados]}")
    
    # Verificar cache Python
    pycache = list(Path(".").glob("**/__pycache__"))
    if pycache:
        problemas.append(f"Cache Python ainda existe: {len(pycache)} pastas")
    
    # Verificar arquivos temporários
    temp_files = list(Path(".").glob("*.pkl")) + list(Path(".").glob("*.tmp"))
    if temp_files:
        problemas.append(f"Arquivos temporários ainda existem: {[f.name for f in temp_files]}")
    
    if problemas:
        print("PROBLEMAS ENCONTRADOS:")
        for problema in problemas:
            print(f"- {problema}")
        return False
    else:
        print("LIMPEZA COMPLETA - NENHUM PROBLEMA ENCONTRADO")
        return True

def limpeza_total():
    """Executa limpeza total do sistema"""
    print("LIMPEZA TOTAL DO SISTEMA RAG")
    print("=" * 50)
    
    # Etapa 1: Fechar conexões
    fechar_todas_conexoes()
    
    # Aguardar liberação de recursos
    print("\nAguardando liberação de recursos...")
    time.sleep(5)
    
    # Etapa 2: Limpar banco SQLite
    limpar_banco_sqlite()
    
    # Etapa 3: Limpar arquivos de dados
    limpar_arquivos_dados()
    
    # Etapa 4: Limpar cache Python
    limpar_cache_python()
    
    # Etapa 5: Verificar limpeza
    sucesso = verificar_limpeza()
    
    print("\n" + "=" * 50)
    if sucesso:
        print("LIMPEZA TOTAL CONCLUÍDA COM SUCESSO")
        print("Sistema pronto para reinicialização limpa")
    else:
        print("LIMPEZA PARCIAL - ALGUNS PROBLEMAS PERSISTEM")
        print("Pode ser necessário reiniciar o terminal/IDE")
    
    return sucesso

def limpeza_emergencial():
    """Limpeza de emergência mais agressiva"""
    print("\n=== LIMPEZA EMERGENCIAL ===")
    
    # Forçar fechamento de processos Python
    try:
        import psutil
        current_pid = os.getpid()
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] == 'python.exe' and proc.info['pid'] != current_pid:
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    if 'rag' in cmdline.lower() or 'sqlite' in cmdline.lower():
                        print(f"Terminando processo: {proc.info['pid']} - {cmdline[:50]}...")
                        proc.terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    except ImportError:
        print("psutil não disponível - pulando terminação de processos")
    
    # Aguardar e tentar limpeza novamente
    time.sleep(3)
    return limpeza_total()

if __name__ == "__main__":
    try:
        sucesso = limpeza_total()
        
        if not sucesso:
            print("\nTentando limpeza emergencial...")
            sucesso = limpeza_emergencial()
        
        if sucesso:
            print("\nSISTEMA LIMPO - PRONTO PARA REINICIALIZAÇÃO")
            print("Recomendação: Reinicie o terminal/IDE para garantir limpeza completa da memória")
        else:
            print("\nFALHA NA LIMPEZA - INTERVENÇÃO MANUAL NECESSÁRIA")
            print("Recomendação: Feche completamente o IDE e reinicie")
            
    except KeyboardInterrupt:
        print("\nLimpeza interrompida pelo usuário")
    except Exception as e:
        print(f"\nErro durante limpeza: {e}")
        import traceback
        traceback.print_exc()