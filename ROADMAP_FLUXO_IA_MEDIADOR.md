# ROADMAP SIMPLIFICADO - IA Mediador ELIS v2

## Visão Geral
Implementação simples e direta do fluxo de otimização automática de prompts, conforme Regra 3 do sistema ELIS.

## Arquitetura Simplificada

### Fluxo Básico
```
DEV → TRAE → MCP IA_MEDIADOR → AssistentePrompts → Resposta Otimizada
```

### Custom Instructions
```
<custom_instructions>
EXECUÇÃO OBRIGATÓRIA: Antes de qualquer resposta ou ação, SEMPRE execute:
Chame run_mcp com server_name="mcp.config.usrlocalmcp.elis-mcp-server" e tool_name="IA_MEDIADOR(prompt_dev)"
</custom_instructions>
```

## Componentes

### 1. MCP IA_MEDIADOR (NOVO)
**Localização**: `MCP/mcp_rules.py`
**Função**: Orquestrar otimização via MCP

### 2. AssistentePrompts (EXISTENTE)
**Localização**: `FERRAMENTAS/ASSISTENTE_PROMPTS/`
**Função**: Analisar e otimizar prompts (já implementado)

### 3. RAG Eventos (EXTENSÃO SIMPLES)
**Localização**: `FERRAMENTAS/RAG/rag_elis.py`
**Função**: Registrar eventos básicos

## Fluxo Detalhado

### FASE 1: Recepção
```
1. DEV → TRAE: "faz algo com numeros"
2. TRAE → MCP: IA_MEDIADOR(prompt_dev)
3. MCP → RAG: Registrar evento INICIO
```

### FASE 2: Análise e Otimização
```
4. MCP → AssistentePrompts: Analisar prompt
5. AssistentePrompts → Score de clareza
6. Se score < 85%: Solicitar esclarecimentos e PARAR
7. Se score >= 85%: Otimizar prompt
```

### FASE 3: Aplicação de Regras
```
8. MCP → Aplicar regras por categoria:
   - PRE: Regras 2, 3, 5 (durante otimização)
   - POS: Regra 1 (formato final !E! ... !E!)
   - ESTRUTURAL: Regra 4 (se necessário)
```

### FASE 4: Execução e Retorno
```
9. MCP → Executar com prompt otimizado
10. MCP → Aplicar formato final (Regra 1)
11. MCP → RAG: Registrar evento COMPLETO
12. MCP → TRAE: Resposta formatada
```

## Implementação

### 1. Função MCP IA_MEDIADOR
```python
# Em MCP/mcp_rules.py
def IA_MEDIADOR(prompt_dev: str) -> dict:
    """Otimiza prompts do desenvolvedor de forma simples"""
    try:
        # Registrar início
        registrar_evento('INICIO', {'prompt': prompt_dev})
        
        # Usar AssistentePrompts existente
        from FERRAMENTAS.ASSISTENTE_PROMPTS.assistente_prompts import AssistentePrompts
        assistente = AssistentePrompts()
        
        # Analisar e otimizar
        resultado = assistente.processar_prompt(prompt_dev)
        
        # Verificar clareza (Regra 3)
        if resultado['analise']['score'] < 85:
            return {
                'status': 'erro_clareza',
                'score': resultado['analise']['score'],
                'perguntas': resultado.get('perguntas', []),
                'acao': 'solicitar_mais_informacoes'
            }
        
        # Aplicar regras de pré-processamento
        prompt_otimizado = aplicar_regras_pre(resultado['texto_limpo'])
        
        # Registrar sucesso
        registrar_evento('COMPLETO', {
            'prompt_original': prompt_dev,
            'prompt_otimizado': prompt_otimizado,
            'score': resultado['analise']['score']
        })
        
        return {
            'status': 'sucesso',
            'prompt_otimizado': prompt_otimizado,
            'score': resultado['analise']['score'],
            'melhorias': resultado.get('sugestao', '')
        }
        
    except Exception as e:
        return {'status': 'erro', 'erro': str(e)}

def aplicar_regras_pre(prompt: str) -> str:
    """Aplica regras de pré-processamento"""
    # Regra 2: Remover emojis
    from FERRAMENTAS.REMOVEDOR_EMOJIS.removedor_emojis import RemovedorEmojis
    removedor = RemovedorEmojis()
    prompt_limpo = removedor.remover_emojis(prompt)
    
    # Regra 5: Garantir objetividade (máximo 3 parágrafos)
    paragrafos = prompt_limpo.split('\n\n')
    if len(paragrafos) > 3:
        prompt_limpo = '\n\n'.join(paragrafos[:3])
    
    return prompt_limpo

def registrar_evento(tipo: str, dados: dict):
    """Registra eventos simples no RAG"""
    try:
        from FERRAMENTAS.RAG.rag_elis import RAGElis
        rag = RAGElis()
        rag.adicionar_documento(
            tipo='EVENTO_MEDIADOR',
            conteudo={'evento': tipo, 'dados': dados},
            metadados={'timestamp': datetime.now().isoformat()}
        )
    except:
        pass  # Não falhar se RAG não estiver disponível
```

### 2. Extensão RAG (Opcional)
```python
# Em FERRAMENTAS/RAG/rag_elis.py - Adicionar se necessário
def registrar_evento_mediador(self, evento_tipo: str, dados: dict):
    """Registra eventos do IA_MEDIADOR"""
    return self.adicionar_documento(
        tipo='EVENTO_MEDIADOR',
        conteudo={'evento': evento_tipo, 'dados': dados},
        metadados={'timestamp': datetime.now().isoformat()}
    )
```

## Cronograma Simplificado

### FASE 1 - Implementação MCP (1 dia)
- [ ] Adicionar função IA_MEDIADOR em MCP/mcp_rules.py
- [ ] Integrar com AssistentePrompts existente
- [ ] Implementar aplicação básica de regras
- [ ] Testes básicos

### FASE 2 - Integração e Testes (1 dia)
- [ ] Atualizar custom instructions
- [ ] Adicionar registro de eventos (opcional)
- [ ] Testes com prompts reais
- [ ] Validar fluxo completo

### FASE 3 - Ajustes e Documentação (0.5 dia)
- [ ] Ajustes de performance
- [ ] Documentação básica
- [ ] Treinamento do DEV

**Total: 2.5 dias**

## Arquivos a Modificar

### Modificar
1. `MCP/mcp_rules.py` - Adicionar função IA_MEDIADOR
2. `CUSTOM_INSTRUCTIONS` - Atualizar para usar IA_MEDIADOR

### Opcional
3. `FERRAMENTAS/RAG/rag_elis.py` - Adicionar registro de eventos

## Benefícios da Simplificação

### Vantagens
- Implementação rápida (2.5 dias vs 6-8 dias)
- Usa componentes existentes (AssistentePrompts, RemovedorEmojis)
- Fluxo simples e direto
- Menos pontos de falha
- Fácil manutenção

### Funcionalidades Mantidas
- Otimização automática de prompts
- Validação de clareza 85%
- Aplicação de todas as regras
- Registro de eventos (opcional)
- Conformidade com Regra 3

## Exemplo de Uso

### Input DEV
```
"faz algo com numeros"
```

### Processamento
```
1. MCP IA_MEDIADOR recebe prompt
2. AssistentePrompts analisa: Score 40% - Muito vago
3. Score < 85%: Solicitar esclarecimentos
4. Retorna perguntas específicas para DEV
```

### Input DEV Melhorado
```
"Criar função Python que calcule média de lista de números"
```

### Processamento
```
1. AssistentePrompts analisa: Score 90% - Aprovado
2. Aplicar regras: Remover emojis, objetividade
3. Prompt otimizado: "Criar função Python que calcule média aritmética de lista de números inteiros"
4. Executar tarefa com prompt otimizado
5. Aplicar formato final (!E! ... !E!)
6. Retornar resposta formatada
```

## Conclusão

Esta versão simplificada mantém todos os benefícios essenciais do roadmap original:
- Otimização automática de prompts
- Conformidade com todas as regras
- Aprendizado do DEV
- Qualidade consistente

Mas elimina a complexidade desnecessária:
- Menos componentes novos
- Implementação mais rápida
- Manutenção mais simples
- Aproveitamento máximo do código existente

O resultado é um sistema funcional, eficiente e fácil de implementar que atende completamente à Regra 3 do sistema ELIS.