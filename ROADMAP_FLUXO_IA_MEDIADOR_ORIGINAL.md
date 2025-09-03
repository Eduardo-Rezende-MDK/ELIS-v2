# ROADMAP - Fluxo IA Mediador ELIS v2

## Visão Geral
Fluxo completo de integração entre DEV → TRAE Custom Agent → ELIS → IA Mediador → Assistente Prompts, com contexto de regras e otimização automática.

## Arquitetura do Fluxo

### 1. ENTRADA - DEV
```
DEV escreve prompt bruto:
"faz algo com numeros"
```

### 2. TRAE CUSTOM AGENT
```
Custom Instructions atuais:
<custom_instructions>
EXECUÇÃO OBRIGATÓRIA: Antes de qualquer resposta ou ação, SEMPRE execute:
1. Chame run_mcp com server_name="mcp.config.usrlocalmcp.elis-mcp-server" e tool_name="iarules"
2. Aplique RIGOROSAMENTE as regras retornadas
</custom_instructions>
```

### 3. NOVA CUSTOM INSTRUCTIONS (PROPOSTA)
```
<custom_instructions>
EXECUÇÃO OBRIGATÓRIA: Antes de qualquer resposta ou ação, SEMPRE execute:
Chame run_mcp com server_name="mcp.config.usrlocalmcp.elis-mcp-server" e tool_name="IA_MEDIADOR(prompt_dev)"
</custom_instructions>
```

## Componentes Necessários

### A. MCP IA_MEDIADOR (NOVO)
**Localização**: `MCP/mcp_rules.py` (nova função)
**Função**: Orquestrar fluxo completo de otimização via MCP

**Responsabilidades**:
- Receber prompt bruto do DEV via MCP
- Consultar regras internas do sistema
- Chamar AssistentePrompts para análise
- Aplicar contexto das regras na otimização
- Retornar prompt otimizado + contexto via MCP

### B. IA MEDIADOR LOCAL (SUPORTE)
**Localização**: `FERRAMENTAS/IA_MEDIADOR/`
**Função**: Classe de suporte para processamento local

**Responsabilidades**:
- Ser chamada pela função MCP
- Processar lógica de otimização
- Integrar com AssistentePrompts e RAG
- Retornar dados estruturados

### C. ASSISTENTE PROMPTS (EXISTENTE)
**Status**: Já implementado
**Localização**: `FERRAMENTAS/ASSISTENTE_PROMPTS/`
**Função**: Analisar e otimizar prompts

### D. GERENCIADOR REGRAS (EXISTENTE)
**Status**: Já implementado
**Localização**: `FERRAMENTAS/GERENCIADOR_REGRAS/`
**Função**: Fornecer regras via MCP

### E. RAG ELIS (EXISTENTE + EXTENSÃO)
**Status**: Já implementado + Extensão necessária
**Localização**: `FERRAMENTAS/RAG/`
**Função**: Armazenar histórico e contexto

**Nova função necessária**:
- `historico_store()`: Registrar eventos do fluxo IA_MEDIADOR

### F. IA_ERRO (NOVO)
**Localização**: `FERRAMENTAS/IA_ERRO/` ou função MCP
**Função**: Gerenciar erros e solicitar esclarecimentos

**Responsabilidades**:
- Detectar prompts com clareza < 85%
- Gerar perguntas específicas para o DEV
- Registrar eventos de erro no RAG
- Interromper fluxo até nova entrada do DEV

### G. CATEGORIZADOR DE REGRAS (NOVO)
**Localização**: `FERRAMENTAS/IA_MEDIADOR/categorizador_regras.py`
**Função**: Organizar regras por momento de aplicação

**Categorias**:
- PRE_PROCESSAMENTO: Regras 2, 3, 5
- POS_PROCESSAMENTO: Regra 1
- ESTRUTURAL: Regra 4

## Fluxo Detalhado com Eventos e Categorização

### FASE 1: RECEPÇÃO E REGISTRO
```
1. DEV → TRAE: "faz algo com numeros"
2. TRAE → Custom Instructions: Executar fluxo obrigatório
3. Custom Instructions → MCP: Chamar IA_MEDIADOR(prompt_dev)
4. MCP IA_MEDIADOR → RAG historico_store(): EVENTO "INICIO_MEDIACAO"
   - Salvar: prompt_original, timestamp, dev_id
```

### FASE 2: ANÁLISE E CATEGORIZAÇÃO DE REGRAS
```
5. MCP IA_MEDIADOR → Carregar regras por categoria:
   - CATEGORIA "PRE_PROCESSAMENTO": Regras 2, 3, 5
     * Regra 2: Proibição Emojis (aplicar durante otimização)
     * Regra 3: Clareza 85% (validar antes de prosseguir)
     * Regra 5: Comunicação Objetiva (aplicar na otimização)
   - CATEGORIA "POS_PROCESSAMENTO": Regra 1
     * Regra 1: Formato resposta (!E! ... !E!) (aplicar no final)
   - CATEGORIA "ESTRUTURAL": Regra 4
     * Regra 4: Organização FERRAMENTAS/ (aplicar se criar arquivos)

6. MCP IA_MEDIADOR → Aplicar Regra 3 (85% clareza):
   - Se score < 85%: Chamar IA_ERRO(prompt_dev, "informações insuficientes")
   - IA_ERRO → RAG historico_store(): EVENTO "ERRO_CLAREZA"
   - IA_ERRO → DEV: Solicitar mais informações
   - INTERROMPER fluxo até nova entrada do DEV
```

### FASE 3: OTIMIZAÇÃO COM PROMPT INTERNO
```
7. MCP IA_MEDIADOR → Prompt interno para IA:
   "Corrija erros gramaticais e ortográficos, otimize para melhor performance 
   do prompt alinhado a técnicas de engenharia de prompts. Aplique regras:
   - Sem emojis (Regra 2)
   - Comunicação objetiva máximo 3 parágrafos (Regra 5)
   - Manter clareza acima de 85% (Regra 3)
   
   PROMPT ORIGINAL DO DEV: [prompt_dev]"

8. IA → MCP IA_MEDIADOR: Prompt otimizado
9. MCP IA_MEDIADOR → RAG historico_store(): EVENTO "PROMPT_OTIMIZADO"
   - Salvar: prompt_otimizado, score_melhoria, regras_aplicadas
```

### FASE 4: EXECUÇÃO E VALIDAÇÃO FINAL
```
10. MCP IA_MEDIADOR → IA_EXECUTA: Prompt otimizado
11. IA_EXECUTA → Processar tarefa com prompt melhorado
12. IA_EXECUTA → MCP IA_MEDIADOR: Resposta processada
13. MCP IA_MEDIADOR → Aplicar Regra 1 (formato !E! ... !E!)
14. MCP IA_MEDIADOR → RAG historico_store(): EVENTO "EXECUCAO_COMPLETA"
15. MCP IA_MEDIADOR → TRAE: Resposta final formatada
16. TRAE → DEV: Resposta + aprendizado sobre melhorias
```

## Implementação

### 1. CRIAR FUNÇÃO MCP IA_MEDIADOR
```python
# Em MCP/mcp_rules.py - Adicionar nova função
def IA_MEDIADOR(prompt_dev: str) -> dict:
    """Função MCP para processar e otimizar prompts do desenvolvedor"""
    try:
        # Importar classe local
        from FERRAMENTAS.IA_MEDIADOR.ia_mediador import IAMediador
        
        # Obter regras atuais
        regras_contexto = obter_regras_atuais()
        
        # Processar via IA Mediador local
        mediador = IAMediador()
        resultado = mediador.processar_fluxo(prompt_dev, regras_contexto)
        
        return {
            'prompt_otimizado': resultado['prompt_otimizado'],
            'contexto_regras': resultado['contexto_regras'],
            'score_clareza': resultado['score_clareza'],
            'melhorias_aplicadas': resultado['melhorias_aplicadas'],
            'status': 'sucesso'
        }
    except Exception as e:
        return {
            'erro': str(e),
            'prompt_original': prompt_dev,
            'status': 'erro'
        }
```

### 2. IMPLEMENTAR historico_store() NO RAG
```python
# Em FERRAMENTAS/RAG/rag_elis.py - Adicionar função
def historico_store(evento_tipo: str, dados: dict) -> bool:
    """Registra eventos do fluxo IA_MEDIADOR no RAG"""
    try:
        evento = {
            'tipo': evento_tipo,
            'timestamp': datetime.now().isoformat(),
            'dados': dados,
            'sessao_id': self.obter_sessao_id()
        }
        
        # Salvar no RAG com categoria específica
        self.adicionar_documento(
            tipo='EVENTO_MEDIADOR',
            conteudo=evento,
            metadados={
                'categoria': 'historico_fluxo',
                'evento_tipo': evento_tipo
            }
        )
        return True
    except Exception as e:
        print(f"Erro ao registrar evento: {e}")
        return False
```

### 3. CRIAR FUNÇÃO MCP IA_ERRO
```python
# Em MCP/mcp_rules.py - Adicionar função
def IA_ERRO(prompt_dev: str, tipo_erro: str) -> dict:
    """Gerencia erros e solicita esclarecimentos do DEV"""
    try:
        # Registrar evento de erro
        from FERRAMENTAS.RAG.rag_elis import RAGElis
        rag = RAGElis()
        rag.historico_store('ERRO_CLAREZA', {
            'prompt_original': prompt_dev,
            'tipo_erro': tipo_erro,
            'score_clareza': 'abaixo_85%'
        })
        
        # Gerar perguntas específicas
        perguntas = gerar_perguntas_esclarecimento(prompt_dev, tipo_erro)
        
        return {
            'status': 'erro',
            'tipo': tipo_erro,
            'prompt_original': prompt_dev,
            'perguntas_esclarecimento': perguntas,
            'acao_requerida': 'aguardar_mais_informacoes_dev'
        }
    except Exception as e:
        return {'erro': str(e), 'status': 'erro_critico'}
```

### 4. CRIAR CATEGORIZADOR DE REGRAS
```python
# Em FERRAMENTAS/IA_MEDIADOR/categorizador_regras.py
class CategorizadorRegras:
    def __init__(self):
        self.categorias = {
            'PRE_PROCESSAMENTO': {
                'regras': [2, 3, 5],
                'momento': 'antes_otimizacao',
                'descricao': 'Regras aplicadas durante análise e otimização'
            },
            'POS_PROCESSAMENTO': {
                'regras': [1],
                'momento': 'apos_execucao',
                'descricao': 'Regras aplicadas na resposta final'
            },
            'ESTRUTURAL': {
                'regras': [4],
                'momento': 'se_necessario',
                'descricao': 'Regras aplicadas se criar arquivos/estruturas'
            }
        }
    
    def obter_regras_por_categoria(self, categoria: str) -> list:
        return self.categorias.get(categoria, {}).get('regras', [])
    
    def obter_momento_aplicacao(self, regra_id: int) -> str:
        for cat, info in self.categorias.items():
            if regra_id in info['regras']:
                return info['momento']
        return 'indefinido'
```

### 5. CRIAR CLASSE IA_MEDIADOR LOCAL
```python
class IAMediador:
    def __init__(self):
        self.assistente_prompts = AssistentePrompts()
        self.rag_elis = RAGElis()
    
    def processar_fluxo(self, prompt_dev: str, regras_contexto: dict) -> dict:
        # 1. Analisar prompt com AssistentePrompts
        analise = self.assistente_prompts.processar_prompt(prompt_dev)
        
        # 2. Aplicar contexto das regras
        contexto_otimizado = self.aplicar_contexto_regras(analise, regras_contexto)
        
        # 3. Gerar prompt final otimizado
        prompt_otimizado = self.gerar_prompt_otimizado(contexto_otimizado)
        
        # 4. Registrar no RAG para aprendizado
        self.rag_elis.registrar_otimizacao(prompt_dev, prompt_otimizado)
        
        return {
            'prompt_original': prompt_dev,
            'prompt_otimizado': prompt_otimizado,
            'contexto_regras': contexto_otimizado,
            'score_clareza': analise['analise']['score'],
            'melhorias_aplicadas': contexto_otimizado['melhorias']
        }
```

### 2. ATUALIZAR CUSTOM INSTRUCTIONS
```
<custom_instructions>
EXECUÇÃO OBRIGATÓRIA: Antes de qualquer resposta ou ação, SEMPRE execute:
Chame run_mcp com server_name="mcp.config.usrlocalmcp.elis-mcp-server" e tool_name="IA_MEDIADOR(prompt_dev)"
</custom_instructions>
```

### 3. INTEGRAÇÃO COM RAG
```python
# Registrar no RAG para aprendizado
def registrar_otimizacao(self, prompt_original, prompt_otimizado, resultado_execucao):
    self.rag_elis.adicionar_documento(
        tipo='OTIMIZACAO_PROMPT',
        conteudo={
            'prompt_original': prompt_original,
            'prompt_otimizado': prompt_otimizado,
            'score_melhoria': self.calcular_score_melhoria(),
            'regras_aplicadas': self.regras_contexto,
            'resultado_execucao': resultado_execucao
        },
        metadados={
            'timestamp': datetime.now(),
            'dev_id': self.obter_dev_id(),
            'tipo_otimizacao': self.classificar_tipo_otimizacao()
        }
    )
```

## Benefícios do Fluxo

### Para o DEV
- Prompts automaticamente otimizados
- Aprendizado contínuo de engenharia de prompts
- Feedback imediato sobre qualidade do prompt
- Sugestões de melhoria específicas

### Para o Sistema
- Conformidade automática com todas as regras
- Qualidade consistente de prompts
- Histórico de otimizações no RAG
- Melhoria contínua do sistema

### Para a IA
- Contexto rico das regras em cada execução
- Prompts de alta qualidade para processamento
- Redução de ambiguidade e erros
- Melhor compreensão das intenções do DEV

## Cronograma de Implementação Atualizado

### FASE 1 - Extensão RAG e Categorização (1 dia)
- [ ] Implementar historico_store() no RAG
- [ ] Criar CategorizadorRegras
- [ ] Testes de registro de eventos
- [ ] Validar categorização de regras

### FASE 2 - Função MCP IA_ERRO (1 dia)
- [ ] Adicionar função IA_ERRO em MCP/mcp_rules.py
- [ ] Implementar geração de perguntas específicas
- [ ] Integrar com historico_store()
- [ ] Testes de interrupção de fluxo

### FASE 3 - Função MCP IA_MEDIADOR (1-2 dias)
- [ ] Adicionar função IA_MEDIADOR em MCP/mcp_rules.py
- [ ] Implementar prompt interno de otimização
- [ ] Integrar com categorização de regras
- [ ] Implementar sistema de eventos
- [ ] Testes básicos da função MCP

### FASE 4 - Classe IA Mediador Local (1-2 dias)
- [ ] Criar classe IAMediador em FERRAMENTAS/IA_MEDIADOR/
- [ ] Implementar integração com AssistentePrompts
- [ ] Implementar fluxo completo com eventos
- [ ] Integrar com IA_ERRO para validação 85%
- [ ] Testes de funcionamento local

### FASE 5 - Custom Instructions e Integração (1 dia)
- [ ] Atualizar custom instructions do TRAE
- [ ] Implementar chamada automática via MCP
- [ ] Testes de integração completa
- [ ] Validar fluxo end-to-end com eventos

### FASE 6 - Validação e Otimização (1-2 dias)
- [ ] Testes com prompts reais do DEV
- [ ] Validar sistema de eventos no RAG
- [ ] Testar fluxo de erro e recuperação
- [ ] Ajustes de performance
- [ ] Documentação completa
- [ ] Treinamento do DEV

## Arquivos a Criar/Modificar

### Modificar
1. `MCP/mcp_rules.py` - Adicionar função IA_MEDIADOR

### Modificar
1. `MCP/mcp_rules.py` - Adicionar funções IA_MEDIADOR e IA_ERRO
2. `FERRAMENTAS/RAG/rag_elis.py` - Adicionar historico_store()

### Criar
3. `FERRAMENTAS/IA_MEDIADOR/ia_mediador.py`
4. `FERRAMENTAS/IA_MEDIADOR/categorizador_regras.py`
5. `FERRAMENTAS/IA_MEDIADOR/contexto_regras.py`
6. `FERRAMENTAS/IA_MEDIADOR/otimizador_prompts.py`
7. `FERRAMENTAS/IA_MEDIADOR/README.md`
8. `FERRAMENTAS/IA_MEDIADOR/exemplo_uso.py`
9. `CUSTOM_INSTRUCTIONS_ATUALIZADA.md`
10. `FERRAMENTAS/IA_ERRO/` (se implementado como ferramenta separada)

## Exemplo de Uso Completo

### Input DEV
```
"faz algo com numeros"
```

### Processamento IA_Mediador
```
1. Análise AssistentePrompts: Score 40% - Muito vago
2. Contexto Regras: Aplicar Regra 3 (85% clareza mínima)
3. Otimização: "Criar função Python que processe lista de números"
4. Validação: Score 85% - Aprovado
5. Contexto Final: + Regras 1,2,4,5 aplicadas
```

### Output para TRAE
```
{
  "prompt_otimizado": "Criar função Python que processe lista de números inteiros e retorne resultado específico",
  "contexto_regras": {
    "formato_resposta": "!E! ... !E!",
    "sem_emojis": true,
    "max_paragrafos": 3,
    "organizacao": "FERRAMENTAS/"
  },
  "melhorias_aplicadas": [
    "Especificação de linguagem (Python)",
    "Definição de tipo de dados (números inteiros)",
    "Clarificação de objetivo (processar e retornar)"
  ]
}
```

## Conclusão

Este fluxo garante que:
1. Todo prompt do DEV seja automaticamente otimizado
2. Todas as regras sejam aplicadas consistentemente
3. O sistema aprenda continuamente
4. O DEV receba feedback educativo
5. A qualidade geral do sistema melhore constantemente

O IA_Mediador é o componente central que orquestra todo este processo, garantindo que a engenharia de prompts seja aplicada de forma sistemática e educativa.