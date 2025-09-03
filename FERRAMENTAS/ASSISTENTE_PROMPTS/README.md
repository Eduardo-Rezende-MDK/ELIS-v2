# Assistente Especializado em Prompts - ELIS v2

## Descrição
Assistente pré-configurado especializado em engenharia de prompts para otimizar comandos do desenvolvedor, conforme Regra 3 do sistema ELIS.

## Funcionalidades

### Análise de Clareza
- Calcula score de clareza (0-100%)
- Identifica padrões problemáticos
- Threshold: 85% para aprovação automática

### Detecção de Problemas
- **Muito vago**: "faz algo", "cria alguma coisa"
- **Sem contexto**: "isso", "aquilo", "ele", "ela"
- **Imperativo simples**: "cria função" (sem especificação)
- **Pergunta aberta**: sem direcionamento específico

### Otimização Automática
- Correção de gramática básica
- Expansão de termos técnicos
- Manutenção da intenção original

## Uso

```python
from assistente_prompts import AssistentePrompts

assistente = AssistentePrompts()
resultado = assistente.processar_prompt("faz algo com numeros")

print(f"Score: {resultado['analise']['score']}%")
print(f"Status: {resultado['status']}")
```

## Exemplos

### Prompt Problemático
**Input**: "faz algo com numeros"
**Score**: 40%
**Status**: precisa_esclarecimento
**Perguntas**:
- Que tipo de funcionalidade você precisa?
- Em qual linguagem de programação?
- Qual é o objetivo final?

### Prompt Otimizado
**Input**: "cria funcao pra calcular media"
**Output**: "criar função para calcular média."
**Score**: 75%

### Prompt Aprovado
**Input**: "Criar função Python que calcule média aritmética de uma lista de números"
**Score**: 100%
**Status**: aprovado

## Integração com Sistema

O assistente é ativado automaticamente quando:
- Score de clareza < 85%
- Prompt contém padrões problemáticos
- Desenvolvedor solicita ajuda explicitamente

## Arquivos
- `assistente_prompts.py`: Classe principal
- `README.md`: Documentação
- `exemplo_uso.py`: Exemplos práticos

## Conformidade
- Regra 1: Formatação de resposta
- Regra 2: Sem emojis
- Regra 3: Assistente especializado (ESTA FERRAMENTA)
- Regra 4: Organização em FERRAMENTAS/
- Regra 5: Comunicação objetiva