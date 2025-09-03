# Custom Instructions Atualizadas - ELIS v2

## Para TRAE IDE

Substitua as Custom Instructions atuais por:

```xml
<custom_instructions>
EXECUÇÃO OBRIGATÓRIA: Antes de qualquer resposta ou ação, SEMPRE execute:
Chame run_mcp com server_name="mcp.config.usrlocalmcp.elis-mcp-server" e tool_name="IA_MEDIADOR" e arguments={"prompt_dev": "[PROMPT_DO_USUARIO]"}
</custom_instructions>
```

## Comando Exato para Aplicar

**Copie e cole exatamente este texto nas Custom Instructions do TRAE:**

```
<custom_instructions>
EXECUÇÃO OBRIGATÓRIA: Antes de qualquer resposta ou ação, SEMPRE execute:
Chame run_mcp com server_name="mcp.config.usrlocalmcp.elis-mcp-server" e tool_name="IA_MEDIADOR" e arguments={"prompt_dev": "[PROMPT_DO_USUARIO]"}
</custom_instructions>
```

## Como Funciona

### Fluxo Automático
1. **DEV** escreve qualquer prompt no TRAE
2. **TRAE** automaticamente chama `IA_MEDIADOR` com o prompt
3. **IA_MEDIADOR** analisa e otimiza o prompt
4. **TRAE** executa com o prompt otimizado
5. **TRAE** aplica formatação final (Regra 1: !E! ... !E!)

### Cenários de Uso

#### Cenário 1: Prompt Vago
**DEV escreve:** "faz algo com numeros"

**IA_MEDIADOR responde:**
```json
{
  "status": "erro_clareza",
  "score": 40,
  "perguntas": [
    "Que tipo de funcionalidade você precisa?",
    "Em qual linguagem de programação?",
    "Qual é o objetivo final?"
  ],
  "acao": "solicitar_mais_informacoes"
}
```

**TRAE** então solicita esclarecimentos ao DEV.

#### Cenário 2: Prompt Bom
**DEV escreve:** "Criar função Python que calcule média de lista"

**IA_MEDIADOR responde:**
```json
{
  "status": "sucesso",
  "prompt_otimizado": "Criar função Python que calcule média aritmética de lista de números",
  "score": 90,
  "melhorias": "Especificação de tipo de cálculo e dados"
}
```

**TRAE** executa com o prompt otimizado.

## Benefícios

### Para o DEV
- Prompts automaticamente otimizados
- Feedback imediato sobre qualidade
- Aprendizado contínuo de engenharia de prompts
- Sugestões específicas de melhoria

### Para o Sistema
- Conformidade automática com Regra 3
- Qualidade consistente de prompts
- Aplicação automática de todas as regras
- Histórico de otimizações no RAG

## Regras Aplicadas Automaticamente

### Pré-processamento
- **Regra 2**: Remoção automática de emojis
- **Regra 3**: Validação de clareza 85%
- **Regra 5**: Objetividade (máximo 3 parágrafos)

### Pós-processamento
- **Regra 1**: Formato !E! ... !E! na resposta final
- **Regra 4**: Organização FERRAMENTAS/ (se aplicável)

## Monitoramento

### Eventos Registrados no RAG
- `INICIO`: Quando prompt é recebido
- `ERRO_CLAREZA`: Quando score < 85%
- `COMPLETO`: Quando otimização é bem-sucedida

### Métricas Disponíveis
- Score de clareza dos prompts
- Taxa de aprovação/rejeição
- Tipos de melhorias aplicadas
- Histórico de aprendizado do DEV

## Troubleshooting

### Se IA_MEDIADOR não funcionar
1. Verificar se MCP Server está rodando
2. Verificar se função IA_MEDIADOR está disponível
3. Testar com: `run_mcp tool_name="live"` (deve retornar número)

### Se prompts não forem otimizados
1. Verificar Custom Instructions no TRAE
2. Verificar se `[PROMPT_DO_USUARIO]` está sendo substituído
3. Verificar logs do MCP Server

## Exemplo Completo de Uso

### Passo 1: DEV escreve
```
"cria funcao pra calcular"
```

### Passo 2: IA_MEDIADOR processa
```json
{
  "status": "erro_clareza",
  "score": 60,
  "perguntas": [
    "Calcular o quê especificamente?",
    "Em qual linguagem?",
    "Que tipo de dados?"
  ]
}
```

### Passo 3: DEV esclarece
```
"Criar função Python que calcule média aritmética de lista de números inteiros"
```

### Passo 4: IA_MEDIADOR aprova
```json
{
  "status": "sucesso",
  "prompt_otimizado": "Criar função Python que calcule média aritmética de lista de números inteiros",
  "score": 95
}
```

### Passo 5: TRAE executa e formata
```
!E!

def calcular_media(numeros):
    """Calcula média aritmética de lista de números inteiros"""
    if not numeros:
        return 0
    return sum(numeros) / len(numeros)

# Exemplo de uso
numeros = [1, 2, 3, 4, 5]
resultado = calcular_media(numeros)
print(f"Média: {resultado}")
!E!
```

## Status da Implementação

- [x] Função IA_MEDIADOR implementada
- [x] Integração com MCP Server
- [x] Testes funcionais realizados
- [x] Custom Instructions documentadas
- [ ] **PRÓXIMO**: Aplicar Custom Instructions no TRAE
- [ ] Testes de integração completa
- [ ] Monitoramento de performance

---

**IMPORTANTE**: Após aplicar as Custom Instructions, todos os prompts do DEV serão automaticamente processados pelo IA_MEDIADOR, garantindo conformidade com a Regra 3 e otimização contínua da qualidade dos prompts.