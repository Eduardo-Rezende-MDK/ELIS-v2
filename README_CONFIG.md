# Sistema de Configuração INI - ELIS v2

## Visão Geral

O sistema ELIS v2 agora utiliza um arquivo de configuração INI (`config.ini`) para centralizar todas as configurações do sistema, simplificando o processo de nova sessão e personalização.

## Arquivo config.ini

O arquivo `config.ini` está localizado na raiz do projeto e contém as seguintes seções:

### [ELIS]
Configurações do componente ELIS (Enhanced Language Intelligence System):
- `versao`: Versão atual do ELIS
- `nome_sistema`: Nome do sistema
- `tag_ativacao`: Tag para ativar processamento completo (padrão: "ELIS:" - OBSOLETA)
- `tag_bypass`: Tag para bypass do ELIS e execução direta (padrão: "IA:")

### [IA]
Configurações do componente IA (Execução):
- `ativo`: Se o IA está ativo (true/false)
- `log_execucao`: Se deve fazer log da execução (true/false)

### [CONTEXTO]
Configurações de contexto e análise:
- `arquivo_contexto`: Caminho para o arquivo de contexto
- `idioma_padrao`: Idioma padrão do sistema
- `formato_resposta`: Formato das respostas (markdown)

### [ARQUIVOS]
Configurações de arquivos do sistema:
- `diretorio_ia`: Diretório dos arquivos de IA
- `arquivo_andamento`: Arquivo de andamento da sessão
- `diretorio_ferramentas`: Diretório das ferramentas

### [DESENVOLVIMENTO]
Configurações para desenvolvimento:
- `versao_python`: Versão do Python (3.8+)
- `padrao_codigo`: Padrão de código (PEP8)
- `idioma_documentacao`: Idioma da documentação (pt-BR)
- `ide_recomendado`: IDE recomendado (Trae)

### [LOGS]
Configurações de logging:
- `nivel_log`: Nível de log (INFO)
- `arquivo_log`: Arquivo de log
- `log_detalhado`: Log detalhado (true/false)

### [SESSAO]
Configurações de sessão:
- `salvar_historico`: Se deve salvar histórico (true/false)
- `max_tentativas`: Máximo de tentativas
- `timeout_execucao`: Timeout de execução em segundos

## Como Usar

### 1. Configuração Automática
O sistema carrega automaticamente as configurações do `config.ini` ao inicializar.

### 2. Personalização da Tag de Ativação
Você pode alterar a tag de ativação editando o valor `tag_ativacao` na seção `[ELIS]`:

```ini
[ELIS]
tag_ativacao = MINHA_TAG:
```

### 3. Configuração de Caminhos
Os caminhos dos arquivos são configuráveis através das seções `[CONTEXTO]` e `[ARQUIVOS]`.

### 4. Gerenciador de Configurações
O sistema inclui um gerenciador de configurações (`config_manager.py`) que:
- Carrega automaticamente o arquivo INI
- Fornece métodos para acessar configurações
- Suporta valores padrão
- Valida tipos de dados (bool, int, string)

## Arquivos Principais

### config_manager.py
Gerenciador principal das configurações:
```python
from config_manager import obter_config

config = obter_config()
tag = config.obter_configuracao('ELIS', 'tag_ativacao', 'ELIS:')
```

### sistema_ia1_ia2.py
Sistema principal integrado com configurações INI.

### sistema_ia1_ia2_com_tag.py
Versão com sistema de tag integrado com configurações INI.

## Benefícios

1. **Centralização**: Todas as configurações em um local
2. **Flexibilidade**: Fácil personalização sem alterar código
3. **Simplicidade**: Processo de nova sessão simplificado
4. **Manutenibilidade**: Configurações separadas da lógica
5. **Reutilização**: Configurações podem ser compartilhadas

## Migração

O arquivo `RESUMO_SESSAO_IA1_IA2.md` foi movido para `IA/andamento.md` para melhor organização dos arquivos de sessão.

## Teste

Para testar o sistema de configuração:

```bash
# Testar o gerenciador de configurações
python config_manager.py

# Testar o sistema ELIS/IA
python sistema_ia1_ia2.py
```

## Nova Lógica do Sistema
**PADRÃO**: Todos os comandos são processados pelo ELIS
**BYPASS**: Use a tag "IA:" para execução direta sem ELIS

## Exemplo de Uso

```bash
# Comando padrão (processamento ELIS)
python sistema_elis.py "crie um arquivo teste.py"

# Comando com bypass (execução direta)
python sistema_elis.py "IA: crie um arquivo teste.py"
```

O sistema agora é mais flexível e fácil de configurar para diferentes necessidades e ambientes de desenvolvimento.