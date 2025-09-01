#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo do Configurador de Prompt ELIS v2
Script de demonstração das funcionalidades
"""

from configurador_prompt import ConfiguradorPrompt
import time

def demo_completa():
    """Demonstração completa das funcionalidades"""
    print("=== DEMO CONFIGURADOR DE PROMPT ELIS v2 ===")
    print()
    
    # Inicializa o configurador
    configurador = ConfiguradorPrompt()
    
    # 1. Obtém regras atuais
    print("1. OBTENDO REGRAS ATUAIS DO MCP:")
    regras = configurador.obter_regras_atuais()
    if regras:
        print(f"Regras obtidas: {regras}")
    else:
        print("Erro ao obter regras")
    time.sleep(2)
    
    # 2. Atualiza configuração baseada nas regras
    print("\n2. ATUALIZANDO CONFIGURAÇÃO:")
    sucesso = configurador.atualizar_configuracao_automatica()
    if sucesso:
        print("Configuração atualizada com sucesso!")
    time.sleep(2)
    
    # 3. Exibe configuração atual
    print("\n3. EXIBINDO CONFIGURAÇÃO ATUAL:")
    configurador.exibir_configuracao_atual()
    time.sleep(2)
    
    # 4. Gera prompt personalizado
    print("\n4. GERANDO PROMPT PERSONALIZADO:")
    config = configurador.carregar_configuracao()
    if config:
        contexto = "Responder sobre programação Python"
        prompt = configurador.gerar_prompt_personalizado(config, contexto)
        print("\n=== PROMPT GERADO ===")
        print(prompt)
    time.sleep(2)
    
    # 5. Testa extração de formato
    print("\n5. TESTANDO EXTRAÇÃO DE FORMATO:")
    if regras:
        formato = configurador.extrair_formato_resposta(regras)
        print(f"Formato extraído: {formato}")
        
        restricoes = configurador.extrair_restricoes(regras)
        print(f"Restrições extraídas: {restricoes}")
    time.sleep(2)
    
    print("\n=== DEMO CONCLUÍDA COM SUCESSO! ===")
    print("\nFuncionalidades demonstradas:")
    print("- Obtenção automática de regras do MCP")
    print("- Criação de configuração de prompt")
    print("- Extração inteligente de formato e restrições")
    print("- Geração de prompts personalizados")
    print("- Salvamento e carregamento de configurações")
    print("\nO configurador está pronto para uso!")

def teste_diferentes_regras():
    """Testa o configurador com diferentes tipos de regras"""
    print("\n=== TESTE COM DIFERENTES REGRAS ===")
    
    configurador = ConfiguradorPrompt()
    
    # Testa diferentes tipos de regras
    regras_teste = [
        "Respostas curtas e objetivas, máximo 3 parágrafos, sem emojis",
        "Respostas técnicas e detalhadas com exemplos práticos",
        "Respostas concisas, sem uso de imagem, ícone ou emojis",
        "Estilo formal, máximo 2 parágrafos, foco em soluções práticas"
    ]
    
    for i, regra in enumerate(regras_teste, 1):
        print(f"\n{i}. TESTANDO REGRA: {regra}")
        
        # Cria configuração para esta regra
        config = configurador.criar_configuracao_prompt(regra)
        
        # Exibe formato extraído
        formato = configurador.extrair_formato_resposta(regra)
        restricoes = configurador.extrair_restricoes(regra)
        
        print(f"   Formato: {formato}")
        print(f"   Restrições: {restricoes}")
        
        # Gera prompt
        prompt = configurador.gerar_prompt_personalizado(config, "Teste")
        print(f"   Prompt gerado: {len(prompt)} caracteres")
        
        time.sleep(1)
    
    print("\n=== TESTE CONCLUÍDO ===")

if __name__ == "__main__":
    demo_completa()
    teste_diferentes_regras()