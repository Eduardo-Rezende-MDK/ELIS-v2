# 🎨 INTERFACE - Visualizador MCP ELIS v2

Este diretório contém os arquivos da interface web para visualizar o funcionamento do sistema MCP (Model Context Protocol) e a função `iarules()`.

## 📁 Estrutura de Arquivos

```
INTERFACE/
├── README.md                    # Este arquivo
├── visualizador_mcp.html        # Interface HTML principal
└── servidor_visualizador.py     # Servidor web Python
```

## 🚀 Como Usar

### 1. **Iniciar o Servidor**
```bash
# A partir do diretório raiz do projeto
cd INTERFACE
python servidor_visualizador.py
```

### 2. **Acessar a Interface**
- **URL:** http://localhost:8000/visualizador_mcp.html
- **Porta padrão:** 8000
- **Navegador:** Abre automaticamente

### 3. **Porta Personalizada**
```bash
python servidor_visualizador.py 8080  # Usa porta 8080
```

## 🎯 Funcionalidades da Interface

### **Comparação Visual**
- **❌ Contexto Fixo:** Limitações do método tradicional
- **✅ Contexto Dinâmico:** Vantagens do sistema ELIS MCP

### **Demonstrações Práticas**
- Conteúdo gerado pela função `iarules()`
- Exemplo de uso com OpenAI API
- Formato JSON estruturado
- Fluxo de funcionamento do sistema

### **Design Responsivo**
- Interface moderna e profissional
- Compatível com desktop e mobile
- Animações e efeitos visuais
- Syntax highlighting para código

## 📊 O que a Interface Mostra

### **1. Comparação Lado a Lado**
```
❌ TRADICIONAL                    ✅ ELIS MCP
"Você é um assistente útil"       iarules() - Dinâmico
• Sem contexto do projeto         • Regras específicas do projeto
• Respostas inconsistentes        • Consistência garantida
• Difícil manutenção             • Configuração centralizada
```

### **2. Conteúdo Dinâmico Gerado**
```
Você é um assistente de programação especializado no projeto ELIS v2.0.

REGRAS DO PROJETO:
- Linguagem principal: Python 3.8+
- Padrão de código: PEP8
- Documentação: Docstrings em pt-BR
- Comentários: Português brasileiro
- IDE: Trae
- Princípios: Clean Code, Modularidade, Tratamento de erros

FORMATO DE RESPOSTA:
- Sem emojis ou ícones
- Máximo 3 parágrafos
- Objetividade e clareza
- Foco apenas no solicitado
```

### **3. Exemplo de Integração**
```python
from mcp_rules import iarules

messages = [
    {"role": "system", "content": iarules()},  # ✅ DINÂMICO
    {"role": "user", "content": "Pergunta do usuário"}
]
```

## 🔧 Requisitos

### **Arquivos Necessários**
- `../MCP/mcp_rules.py` - Função iarules()
- `../FERRAMENTAS/GERENCIADOR_REGRAS/` - Sistema de regras persistentes
- `visualizador_mcp.html` - Interface HTML

### **Python**
- Python 3.8+
- Módulos padrão: `http.server`, `socketserver`, `webbrowser`

## 🎨 Características Visuais

### **Design Moderno**
- Gradientes e cores profissionais
- Cards interativos com hover effects
- Indicadores visuais de status
- Typography moderna (Segoe UI)

### **Responsividade**
- Grid layout adaptativo
- Mobile-first approach
- Breakpoints para diferentes telas
- Navegação otimizada

### **Código Destacado**
- Syntax highlighting
- Blocos de código formatados
- JSON com cores diferenciadas
- Exemplos práticos

## 🚀 Vantagens do Sistema MCP

1. **Regras Persistentes** - Todas as regras vêm do arquivo JSON
2. **Atualização Automática** - Mudanças refletem imediatamente
3. **Consistência Garantida** - Mesmo contexto em todos os assistants
4. **Fácil Manutenção** - Sem necessidade de alterar código
5. **Reutilização** - Pode ser usado em qualquer custom assistant
6. **Flexibilidade** - Personalizável por projeto

## 📚 Integração com Trae IDE

Esta interface demonstra como o sistema MCP pode ser integrado com custom assistants do Trae IDE, proporcionando:

- **Contexto Específico do Projeto**
- **Regras Dinâmicas Baseadas em Configuração**
- **Consistência Entre Diferentes Assistants**
- **Facilidade de Manutenção e Atualização**

## 🎉 Status

**✅ Interface Funcionando Perfeitamente**
- Servidor ativo na porta 8000
- Todos os arquivos organizados
- Demonstração completa do sistema MCP
- Pronta para uso e demonstrações

---

**ELIS v2.0 - Sistema de Regras Dinâmicas para Custom Assistants**