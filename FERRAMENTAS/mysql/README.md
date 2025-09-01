# MySQL Manager - ELIS v2

Ferramenta Python para conexao e execucao de queries MySQL com assistencia de IA.

## Funcionalidades

- Conexao segura ao MySQL
- Execucao de queries SELECT
- Execucao de comandos INSERT/UPDATE/DELETE
- Gerenciamento de configuracoes de conexao
- Analise automatica de estrutura do banco
- Sugestoes de queries basicas
- Relatorios de banco de dados

## Instalacao

```bash
pip install -r requirements.txt
```

## Uso Basico

### 1. Configuracao de Conexao

```python
from config import MySQLConfig

# Criar configuracao
config = MySQLConfig()
config.adicionar_conexao(
    nome="minha_conexao",
    host="localhost",
    database="meu_banco",
    user="usuario",
    password="senha"
)
```

### 2. Conexao e Queries Simples

```python
from mysql_manager import MySQLManager

# Conectar
manager = MySQLManager()
manager.conectar("localhost", "meu_banco", "usuario", "senha")

# Executar query
resultados = manager.executar_query("SELECT * FROM usuarios LIMIT 10")
print(resultados)

# Desconectar
manager.desconectar()
```

### 3. Usando MySQL AI Assistant

```python
from mysql_ai import MySQLAI

# Conectar usando configuracao salva
mysql_ai = MySQLAI("minha_conexao")
mysql_ai.conectar()

# Executar query com contexto
resultado = mysql_ai.executar_query_com_contexto("SELECT COUNT(*) FROM produtos")
print(f"Total de registros: {resultado['total_registros']}")

# Analisar tabela
analise = mysql_ai.executar_analise_rapida("produtos")
print(f"Estrutura: {analise['estrutura']}")
print(f"Queries sugeridas: {analise['queries_sugeridas']}")

# Gerar relatorio do banco
relatorio = mysql_ai.gerar_relatorio_banco()
print(f"Total de tabelas: {relatorio['total_tabelas']}")

mysql_ai.desconectar()
```

### 4. Funcoes Utilitarias

```python
from mysql_ai import conectar_e_executar, analisar_tabela_rapido

# Execucao rapida
resultado = conectar_e_executar("minha_conexao", "SELECT * FROM clientes LIMIT 5")

# Analise rapida de tabela
analise = analisar_tabela_rapido("minha_conexao", "pedidos")
```

## Estrutura de Arquivos

```
mysql/
├── mysql_manager.py    # Classe principal para MySQL
├── config.py          # Gerenciamento de configuracoes
├── mysql_ai.py        # Assistente IA para MySQL
├── requirements.txt   # Dependencias
└── README.md         # Esta documentacao
```

## Configuracao JSON

O arquivo `mysql_config.json` e criado automaticamente:

```json
{
  "conexoes": {
    "local": {
      "host": "localhost",
      "port": 3306,
      "database": "test",
      "user": "root",
      "password": ""
    }
  }
}
```

## Recursos de IA

- **Analise de Estrutura**: Mapeia automaticamente tabelas e colunas
- **Sugestoes de Queries**: Gera queries basicas baseadas na estrutura
- **Contexto Enriquecido**: Retorna metadados junto com resultados
- **Relatorios Automaticos**: Gera visao geral do banco de dados

## Seguranca

- Senhas armazenadas em arquivo de configuracao local
- Uso de parametros preparados para prevenir SQL injection
- Conexoes seguras com tratamento de erros

## Limitacoes

- Versao MVP focada em operacoes basicas
- Suporte apenas para MySQL
- Configuracoes armazenadas localmente

## Exemplo Completo

```python
from mysql_ai import MySQLAI
from config import MySQLConfig

# 1. Configurar conexao
config = MySQLConfig()
config.adicionar_conexao(
    "producao",
    "servidor.empresa.com",
    "sistema_vendas",
    "user_app",
    "senha_segura"
)

# 2. Conectar e analisar
mysql_ai = MySQLAI("producao")
if mysql_ai.conectar():
    # Listar tabelas
    estrutura = mysql_ai.analisar_estrutura_banco()
    print(f"Banco tem {estrutura['total_tabelas']} tabelas")
    
    # Analisar tabela especifica
    if "vendas" in estrutura["tabelas"]:
        analise = mysql_ai.executar_analise_rapida("vendas")
        print(f"Tabela vendas tem {analise['total_registros']} registros")
        
        # Executar queries sugeridas
        for query in analise["queries_sugeridas"][:3]:
            resultado = mysql_ai.executar_query_com_contexto(query)
            print(f"Query: {query}")
            print(f"Resultados: {resultado['total_registros']} registros")
    
    mysql_ai.desconectar()
else:
    print("Falha na conexao")
```