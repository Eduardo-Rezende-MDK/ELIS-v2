#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo do Gerenciador de Regras ELIS v2
Script de demonstração das funcionalidades
"""

from gerenciador_regras import GerenciadorRegras
import time

def demo_completa():
    """Demonstração completa das funcionalidades"""
    print("=== DEMO GERENCIADOR DE REGRAS ELIS v2 ===")
    print()
    
    # Inicializa o gerenciador
    gerenciador = GerenciadorRegras()
    
    # 1. Lista regras atuais
    print("1. LISTANDO REGRAS ATUAIS:")
    gerenciador.listar_regras()
    time.sleep(2)
    
    # 2. Insere nova regra
    print("\n2. INSERINDO NOVA REGRA:")
    nova_regra = "Respostas devem ser técnicas, detalhadas e incluir exemplos práticos"
    gerenciador.inserir_regra(nova_regra)
    print("\nNOTA: Para ativar a regra, faça refresh manual no Trae AI")
    time.sleep(2)
    
    # 3. Lista regras após inserção
    print("\n3. VERIFICANDO REGRA INSERIDA:")
    gerenciador.listar_regras()
    time.sleep(2)
    
    # 4. Lista backups criados
    print("\n4. LISTANDO BACKUPS CRIADOS:")
    gerenciador.listar_backups()
    time.sleep(2)
    
    # 5. Edita a regra
    print("\n5. EDITANDO REGRA:")
    regra_editada = "Respostas objetivas, máximo 3 parágrafos, sem emojis ou imagens"
    gerenciador.editar_regra(regra_editada)
    print("\nNOTA: Para ativar a regra editada, faça refresh manual no Trae AI")
    time.sleep(2)
    
    # 6. Verifica regra editada
    print("\n6. VERIFICANDO REGRA EDITADA:")
    gerenciador.listar_regras()
    time.sleep(2)
    
    # 7. Lista backups finais
    print("\n7. BACKUPS FINAIS:")
    gerenciador.listar_backups()
    
    print("\n=== DEMO CONCLUÍDA COM SUCESSO! ===")
    print("\nFuncionalidades demonstradas:")
    print("- Listagem de regras")
    print("- Inserção de novas regras")
    print("- Edição de regras existentes")
    print("- Backup automático")
    print("- Instruções para refresh manual")
    print("\nA ferramenta está pronta para uso!")
    print("\nLEMBRETE: Faça refresh manual no Trae AI para ativar as regras.")

if __name__ == "__main__":
    demo_completa()