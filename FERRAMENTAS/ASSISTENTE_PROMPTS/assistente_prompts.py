#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Assistente Especializado em Prompts - ELIS v2
Conforme Regra 3: Assistente pré-configurado para otimizar prompts do desenvolvedor
"""

import re
from typing import Dict, List, Tuple

class AssistentePrompts:
    def __init__(self):
        self.threshold_clareza = 85
        self.padroes_problematicos = {
            'muito_vago': r'^(faz|cria|ajuda|preciso)\s*(algo|alguma coisa)?\s*$',
            'sem_contexto': r'^(isso|aquilo|ele|ela)\s+',
            'imperativo_simples': r'^(cria|faz|gera)\s+\w+\s*$',
            'pergunta_aberta': r'^(como|o que|qual)\s+.*\?\s*$'
        }
        
    def analisar_clareza(self, prompt: str) -> Dict:
        """Analisa clareza do prompt e retorna score + problemas identificados"""
        score = 100
        problemas = []
        
        # Verificações de clareza
        if len(prompt.strip()) < 10:
            score -= 30
            problemas.append("Prompt muito curto")
            
        if not any(char in prompt for char in '.?!'):
            score -= 10
            problemas.append("Falta pontuação")
            
        # Verificar padrões problemáticos
        for tipo, padrao in self.padroes_problematicos.items():
            if re.search(padrao, prompt.lower()):
                score -= 25
                problemas.append(f"Padrão problemático: {tipo}")
                
        # Verificar especificidade
        palavras_especificas = ['python', 'javascript', 'função', 'classe', 'lista', 'arquivo']
        if not any(palavra in prompt.lower() for palavra in palavras_especificas):
            score -= 15
            problemas.append("Falta especificidade técnica")
            
        return {
            'score': max(0, score),
            'problemas': problemas,
            'precisa_otimizacao': score < self.threshold_clareza
        }
    
    def gerar_perguntas_esclarecimento(self, prompt: str, analise: Dict) -> List[str]:
        """Gera perguntas para esclarecer prompt vago"""
        perguntas = []
        
        if 'muito_vago' in str(analise['problemas']):
            perguntas.extend([
                "Que tipo de funcionalidade você precisa?",
                "Em qual linguagem de programação?",
                "Qual é o objetivo final?"
            ])
            
        if 'sem_contexto' in str(analise['problemas']):
            perguntas.append("Pode especificar melhor o que 'isso' se refere?")
            
        if 'Falta especificidade técnica' in analise['problemas']:
            perguntas.extend([
                "Que tecnologia ou linguagem você está usando?",
                "Qual tipo de dados você está processando?"
            ])
            
        return perguntas[:3]  # Máximo 3 perguntas
    
    def otimizar_prompt(self, prompt: str) -> str:
        """Otimiza prompt mantendo intenção original"""
        prompt_otimizado = prompt.strip()
        
        # Correções básicas
        if not prompt_otimizado.endswith(('.', '!', '?')):
            prompt_otimizado += '.'
            
        # Expansões comuns
        expansoes = {
            r'\bcria\b': 'criar',
            r'\bfaz\b': 'fazer',
            r'\bfuncao\b': 'função',
            r'\bmedia\b': 'média',
            r'\blista\b': 'lista de dados'
        }
        
        for padrao, substituicao in expansoes.items():
            prompt_otimizado = re.sub(padrao, substituicao, prompt_otimizado, flags=re.IGNORECASE)
            
        return prompt_otimizado
    
    def processar_prompt(self, prompt: str) -> Dict:
        """Processa prompt completo: analisa, otimiza e gera resposta"""
        analise = self.analisar_clareza(prompt)
        
        resultado = {
            'prompt_original': prompt,
            'analise': analise,
            'status': 'aprovado' if not analise['precisa_otimizacao'] else 'precisa_esclarecimento'
        }
        
        if analise['precisa_otimizacao']:
            resultado['perguntas'] = self.gerar_perguntas_esclarecimento(prompt, analise)
            resultado['prompt_otimizado'] = self.otimizar_prompt(prompt)
            resultado['sugestao'] = f"Prompt otimizado: {resultado['prompt_otimizado']}"
        else:
            resultado['prompt_final'] = prompt
            
        return resultado

def main():
    """Exemplo de uso do assistente"""
    assistente = AssistentePrompts()
    
    # Testes com prompts problemáticos
    prompts_teste = [
        "faz algo com numeros",
        "cria funcao",
        "preciso de ajuda com listas",
        "Criar função Python que calcule média aritmética de uma lista de números"
    ]
    
    for prompt in prompts_teste:
        print(f"\n=== PROMPT: {prompt} ===")
        resultado = assistente.processar_prompt(prompt)
        print(f"Score: {resultado['analise']['score']}%")
        print(f"Status: {resultado['status']}")
        
        if 'perguntas' in resultado:
            print("Perguntas para esclarecimento:")
            for pergunta in resultado['perguntas']:
                print(f"  - {pergunta}")
                
        if 'sugestao' in resultado:
            print(f"Sugestão: {resultado['sugestao']}")

if __name__ == "__main__":
    main()