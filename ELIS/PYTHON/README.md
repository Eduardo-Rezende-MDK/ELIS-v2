# ELIS Python Modules

Este diretório contém todos os módulos Python do sistema ELIS v2.

## Estrutura de Arquivos

```
ELIS/PYTHON/
├── __init__.py              # Inicialização do pacote Python
├── sistema_elis.py          # Módulo principal do sistema ELIS
├── elis_com_tag.py         # Sistema ELIS com suporte a tags
├── config_manager.py       # Gerenciador de configurações
├── requirements.txt        # Dependências do projeto
├── setup_env.bat          # Script de configuração do ambiente
├── venv/                  # Ambiente virtual (criado pelo setup_env.bat)
└── README.md              # Este arquivo
```

## Configuração do Ambiente

### Primeira Configuração

1. Execute o script de configuração:
   ```bash
   setup_env.bat
   ```

2. O script irá:
   - Verificar se o Python está instalado
   - Criar um ambiente virtual em `venv/`
   - Ativar o ambiente virtual
   - Instalar dependências do `requirements.txt`

### Uso Diário

**Ativar ambiente virtual:**
```bash
venv\Scripts\activate.bat
```

**Desativar ambiente virtual:**
```bash
deactivate
```

## Regras de Desenvolvimento

### ⚠️ IMPORTANTE: Gerenciamento de Dependências

1. **NUNCA instale pacotes globalmente**
   ```bash
   # ❌ ERRADO
   pip install pacote
   
   # ✅ CORRETO
   venv\Scripts\activate.bat
   pip install pacote
   ```

2. **Sempre use o ambiente virtual**
   - Ative o ambiente antes de executar qualquer código Python
   - Mantenha o `requirements.txt` atualizado

3. **Atualize o requirements.txt após instalar novos pacotes**
   ```bash
   pip freeze > requirements.txt
   ```

## Módulos Principais

### config_manager.py
- **Função:** Gerencia configurações do sistema
- **Uso:** Carrega e fornece acesso ao `config.ini`
- **Classe principal:** `ConfigManager`

### sistema_elis.py
- **Função:** Módulo principal do sistema ELIS
- **Uso:** Análise e melhoria de prompts
- **Classe principal:** `ELIS_AnaliseContexto`

### elis_com_tag.py
- **Função:** Sistema ELIS com suporte a tags
- **Uso:** Processamento de comandos com tags (ELIS:, IA:)
- **Classe principal:** `ProcessadorComandos`

## Exemplo de Uso

```python
# Importar módulos do pacote ELIS
from ELIS.PYTHON import ProcessadorComandos, obter_config

# Inicializar processador
processador = ProcessadorComandos()

# Processar comando
resultado = processador.processar_comando("ELIS: criar arquivo teste.py")
```

## Troubleshooting

### Problema: "Módulo não encontrado"
**Solução:** Verifique se o ambiente virtual está ativo

### Problema: "Erro de permissão ao instalar pacotes"
**Solução:** Use o ambiente virtual, nunca instale globalmente

### Problema: "Config.ini não encontrado"
**Solução:** O arquivo está em `../../config.ini` (raiz do projeto)

## Versionamento

- **Versão atual:** 2.0
- **Python mínimo:** 3.8+
- **Padrão de código:** PEP8
- **Documentação:** Português (pt-BR)