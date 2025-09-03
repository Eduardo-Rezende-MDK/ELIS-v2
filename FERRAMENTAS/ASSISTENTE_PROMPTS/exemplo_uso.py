#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exemplo de Uso - Assistente Especializado em Prompts
Demonstra como usar o assistente para melhorar prompts do desenvolvedor
"""

from assistente_prompts import AssistentePrompts

def demonstrar_casos_uso():
    """Demonstra diferentes cenários de uso do assistente"""
    assistente = AssistentePrompts()
    
    print("=== ASSISTENTE ESPECIALIZADO EM PROMPTS ===")
    print("Demonstração de casos de uso\n")
    
    # Caso 1: Prompt muito vago
    print("CASO 1: Prompt Vago")
    prompt1 = "faz algo com numeros"
    resultado1 = assistente.processar_prompt(prompt1)
    
    print(f"Prompt original: '{prompt1}'")
    print(f"Score de clareza: {resultado1['analise']['score']}%")
    print(f"Status: {resultado1['status']}")
    print("Problemas identificados:")
    for problema in resultado1['analise']['problemas']:
        print(f"  - {problema}")
    print("Perguntas para esclarecimento:")
    for pergunta in resultado1['perguntas']:
        print(f"  ? {pergunta}")
    print(f"Sugestão: {resultado1['sugestao']}\n")
    
    # Caso 2: Prompt com erros
    print("CASO 2: Prompt com Erros")
    prompt2 = "cria funcao pra calcular media"
    resultado2 = assistente.processar_prompt(prompt2)
    
    print(f"Prompt original: '{prompt2}'")
    print(f"Score de clareza: {resultado2['analise']['score']}%")
    print(f"Status: {resultado2['status']}")
    if 'sugestao' in resultado2:
        print(f"Sugestão: {resultado2['sugestao']}")
    print()
    
    # Caso 3: Prompt sem contexto
    print("CASO 3: Prompt Sem Contexto")
    prompt3 = "isso não está funcionando"
    resultado3 = assistente.processar_prompt(prompt3)
    
    print(f"Prompt original: '{prompt3}'")
    print(f"Score de clareza: {resultado3['analise']['score']}%")
    print(f"Status: {resultado3['status']}")
    if 'perguntas' in resultado3:
        print("Perguntas para esclarecimento:")
        for pergunta in resultado3['perguntas']:
            print(f"  ? {pergunta}")
    print()
    
    # Caso 4: Prompt bem estruturado
    print("CASO 4: Prompt Bem Estruturado")
    prompt4 = "Criar função Python que calcule média aritmética de uma lista de números inteiros"
    resultado4 = assistente.processar_prompt(prompt4)
    
    print(f"Prompt original: '{prompt4}'")
    print(f"Score de clareza: {resultado4['analise']['score']}%")
    print(f"Status: {resultado4['status']}")
    print("Prompt aprovado para execução!\n")

def simular_interacao_desenvolvedor():
    """Simula interação real com desenvolvedor"""
    assistente = AssistentePrompts()
    
    print("=== SIMULAÇÃO DE INTERAÇÃO ===")
    print("Desenvolvedor envia prompt vago...\n")
    
    # Prompt inicial vago
    prompt_dev = "preciso de ajuda com listas"
    print(f"DEV: {prompt_dev}")
    
    resultado = assistente.processar_prompt(prompt_dev)
    
    print(f"\nASSISTENTE: Score de clareza: {resultado['analise']['score']}%")
    print("ASSISTENTE: Seu prompt precisa de mais detalhes. Posso ajudar com estas perguntas:")
    
    for i, pergunta in enumerate(resultado['perguntas'], 1):
        print(f"  {i}. {pergunta}")
    
    # Resposta do desenvolvedor
    print("\nDEV: Quero criar uma função Python que ordene uma lista de números")
    
    prompt_melhorado = "Criar função Python que ordene uma lista de números"
    resultado_final = assistente.processar_prompt(prompt_melhorado)
    
    print(f"\nASSISTENTE: Score de clareza: {resultado_final['analise']['score']}%")
    
    if resultado_final['status'] == 'aprovado':
        print("ASSISTENTE: Prompt aprovado! Executando tarefa...")
    else:
        print(f"ASSISTENTE: {resultado_final['sugestao']}")

def testar_padroes_problematicos():
    """Testa detecção de padrões problemáticos"""
    assistente = AssistentePrompts()
    
    print("=== TESTE DE PADRÕES PROBLEMÁTICOS ===")
    
    padroes_teste = [
        ("faz algo", "Muito vago"),
        ("isso não funciona", "Sem contexto"),
        ("cria função", "Imperativo simples"),
        ("como fazer?", "Pergunta aberta"),
        ("ajuda", "Muito curto")
    ]
    
    for prompt, tipo_esperado in padroes_teste:
        resultado = assistente.processar_prompt(prompt)
        print(f"Prompt: '{prompt}'")
        print(f"  Score: {resultado['analise']['score']}%")
        print(f"  Problemas: {', '.join(resultado['analise']['problemas'])}")
        print(f"  Tipo esperado: {tipo_esperado}")
        print()

if __name__ == "__main__":
    demonstrar_casos_uso()
    print("\n" + "="*50 + "\n")
    simular_interacao_desenvolvedor()
    print("\n" + "="*50 + "\n")
    testar_padroes_problematicos()