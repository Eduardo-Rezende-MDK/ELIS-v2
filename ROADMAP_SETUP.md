# ROADMAP DE SETUP - ELIS v2

Guia completo para configurar o projeto ELIS v2 após download do repositório Git.

## PRE-REQUISITOS

- Python 3.8+
- Git
- Editor de código (recomendado: Trae IDE)
- Conexão com internet

## PASSO 1: CLONE E ESTRUTURA

```bash
git clone [URL_DO_REPOSITORIO]
cd ELIS-v2
```

**Estrutura esperada:**
```
ELIS-v2/
├── FERRAMENTAS/
├── INTERFACE/
├── MCP/
├── regras.txt
└── ROADMAP_SETUP.md
```

## PASSO 2: CONFIGURAR CAMINHOS ABSOLUTOS

### Arquivos que precisam de ajuste de caminho:

**1. MCP/mcp_config.json**
```json
{
  "mcpServers": {
    "elis-mcp-server": {
      "command": "python",
      "args": [
        "[SEU_CAMINHO_COMPLETO]\\ELIS-v2\\MCP\\mcp_server_stdio.py"
      ],
      "env": {
        "PYTHONPATH": "[SEU_CAMINHO_COMPLETO]\\ELIS-v2\\MCP"
      }
    }
  }
}
```

**2. regras.txt**
```
RAIZ_PROJETO: [SEU_CAMINHO_COMPLETO]\ELIS-v2
PASTA_INTERFACE: [SEU_CAMINHO_COMPLETO]\ELIS-v2\INTERFACE
PASTA_MCP: [SEU_CAMINHO_COMPLETO]\ELIS-v2\MCP
ARQUIVO_REGRAS: [SEU_CAMINHO_COMPLETO]\ELIS-v2\regras.txt
```

**3. Arquivos Python com caminhos hardcoded:**
- Buscar por "c:\\ELIS\\ELIS-v2" em todos os arquivos .py
- Substituir pelo seu caminho completo

## PASSO 3: INSTALAR DEPENDENCIAS

### Sistema RAG
```bash
cd FERRAMENTAS/RAG
python instalar_dependencias.py
```

### MySQL Manager
```bash
cd FERRAMENTAS/mysql
pip install -r requirements.txt
```

### Interface Streamlit
```bash
cd INTERFACE
pip install -r requirements_streamlit.txt
```

### Dependências principais do projeto:
```bash
pip install sentence-transformers requests beautifulsoup4 arxiv nltk numpy pandas mysql-connector-python streamlit
```

## PASSO 4: CONFIGURAR MCP

### 1. Testar servidor MCP
```bash
cd MCP
python test_mcp_functions.py
```

### 2. Configurar no Trae IDE
- Abrir configurações do Trae
- Adicionar servidor MCP usando o arquivo mcp_config.json
- Verificar se o caminho está correto

### 3. Testar função iarules
```python
from MCP.mcp_rules import iarules
print(iarules())
```

### 4. Configurar Custom Agent no Trae

**Criar novo Custom Agent:**
1. Abrir Trae IDE
2. Ir em Settings > Custom Assistants
3. Criar novo assistant com nome "ELIS v2"
4. Adicionar as seguintes custom instructions:

```
<custom_instructions>
EXECUÇÃO OBRIGATÓRIA: Antes de qualquer resposta ou ação, SEMPRE execute:
1. Chame run_mcp com server_name="mcp.config.usrlocalmcp.elis-mcp-server" e tool_name="iarules"
2. Aplique RIGOROSAMENTE as regras retornadas em:
   - Estilo de resposta (objetividade, tamanho)
   - Restrições técnicas (linguagens permitidas)
   - Formato de saída (sem emojis/ícones)
   - Comportamento geral

Esta consulta é MANDATÓRIA para cada interação, sem exceções.
</custom_instructions>
```

**Configurar MCP Server:**
1. Na seção MCP Servers do custom agent
2. Adicionar servidor: "mcp.config.usrlocalmcp.elis-mcp-server"
3. Verificar se está conectado e funcionando
4. Testar com comando iarules()

**Validar configuração:**
- O assistant deve sempre consultar iarules() antes de responder
- Respostas devem seguir as regras do projeto
- Sem emojis ou ícones nas respostas
- Máximo 3 parágrafos por resposta

## PASSO 5: CONFIGURAR MYSQL (OPCIONAL)

### 1. Criar arquivo de configuração
```bash
cd FERRAMENTAS/mysql
python -c "from config import MySQLConfig; config = MySQLConfig(); config.adicionar_conexao('local', 'localhost', 'test', 'root', '')"
```

### 2. Testar conexão
```python
from FERRAMENTAS.mysql.mysql_ai import MySQLAI
mysql_ai = MySQLAI('local')
if mysql_ai.conectar():
    print('Conexão MySQL OK')
    mysql_ai.desconectar()
```

## PASSO 6: TESTAR COMPONENTES

### 1. Sistema RAG
```bash
cd FERRAMENTAS/RAG
python exemplo_uso.py
```

### 2. Interface Web
```bash
cd INTERFACE
python servidor_visualizador.py
```
Acessar: http://localhost:8000/visualizador_mcp.html

### 3. Interface Streamlit
```bash
cd INTERFACE
python iniciar_streamlit.py
```

## PASSO 7: VERIFICAÇÕES FINAIS

### Checklist de funcionamento:
- [ ] MCP servidor responde corretamente
- [ ] iarules() retorna regras do projeto
- [ ] RAG processa documentos
- [ ] Interface web carrega
- [ ] MySQL conecta (se configurado)
- [ ] Streamlit inicia sem erros

## ESTRUTURA DE ARQUIVOS IMPORTANTES

```
ELIS-v2/
├── MCP/
│   ├── mcp_config.json          # AJUSTAR CAMINHOS
│   ├── mcp_rules.py             # Função iarules
│   └── mcp_server_stdio.py      # Servidor MCP
├── FERRAMENTAS/
│   ├── RAG/
│   │   ├── requirements.txt     # Dependências RAG
│   │   └── instalar_dependencias.py
│   └── mysql/
│       ├── requirements.txt     # Dependências MySQL
│       └── config.py            # Configuração MySQL
├── INTERFACE/
│   ├── requirements_streamlit.txt
│   ├── servidor_visualizador.py
│   └── visualizador_mcp.html
└── regras.txt                   # AJUSTAR CAMINHOS
```

## SOLUÇÃO DE PROBLEMAS

### Erro de caminho absoluto
- Verificar se todos os caminhos foram atualizados
- Usar barras duplas (\\\\) no Windows
- Testar caminhos no terminal

### Erro de dependências
- Reinstalar com pip install --upgrade
- Verificar versão do Python
- Usar ambiente virtual se necessário

### MCP não funciona
- Verificar mcp_config.json
- Testar servidor manualmente
- Verificar logs do Trae IDE

### Interface não carrega
- Verificar se porta 8000 está livre
- Testar com porta alternativa
- Verificar firewall/antivirus

## COMANDOS ÚTEIS

### Buscar caminhos hardcoded
```bash
findstr /r /s "c:\\\\ELIS\\\\ELIS-v2" *.py
```

### Testar todas as importações
```python
# Testar imports principais
try:
    from MCP.mcp_rules import iarules
    from FERRAMENTAS.RAG.rag_pipeline import RAGPipeline
    from FERRAMENTAS.mysql.mysql_ai import MySQLAI
    print("Todas as importações OK")
except ImportError as e:
    print(f"Erro de importação: {e}")
```

### Verificar estrutura
```python
import os
from pathlib import Path

base_path = Path("[SEU_CAMINHO]\\ELIS-v2")
for pasta in ["MCP", "FERRAMENTAS", "INTERFACE"]:
    caminho = base_path / pasta
    print(f"{pasta}: {'OK' if caminho.exists() else 'ERRO'}")
```

## PRÓXIMOS PASSOS

Após setup completo:
1. Configurar custom assistant no Trae com MCP
2. Testar sistema RAG com temas específicos
3. Configurar conexões MySQL para projetos reais
4. Personalizar regras no arquivo regras_persistentes.json

---

**IMPORTANTE:** Este roadmap assume instalação no Windows. Para Linux/Mac, ajustar separadores de caminho e comandos conforme necessário.