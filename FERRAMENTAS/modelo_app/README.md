# Modelo App - ELIS v2

Ferramenta para criar interfaces básicas de aplicativo com estrutura de header, corpo e rodapé. Inclui template StudyAI baseado em interface acadêmica.

## Funcionalidades

- Criação de interface com 3 seções: header, corpo e rodapé
- Template StudyAI com módulos acadêmicos (Ensaio, Pesquisa, Exercícios, Estudos, RAG)
- Menu interativo com navegação entre módulos
- Personalização do título e usuário
- Renderização como string ou exibição direta
- Estrutura simples e reutilizável

## Uso Básico - Interface StudyAI

```python
from modelo_app import ModeloApp

# Criar app StudyAI
app = ModeloApp("StudyAI", "Administrador")

# Exibir interface padrão StudyAI
app.exibir()

# Menu interativo
app.menu_interativo()
```

## Uso Básico - Interface Personalizada

```python
from modelo_app import ModeloApp

# Criar app personalizado
app = ModeloApp("Meu Sistema", "Usuário")

# Definir conteúdo
conteudo = "Bem-vindo ao sistema!"

# Exibir
app.exibir(conteudo)
```

## Exemplo Completo

```python
from modelo_app import ModeloApp

app = ModeloApp("Sistema de Vendas")

conteudo = """
Menu Principal:
1. Cadastrar produto
2. Listar produtos
3. Relatórios
4. Sair

Escolha uma opção:
"""

app.exibir(conteudo)
```

## Métodos Disponíveis

- `criar_header()`: Gera o cabeçalho
- `criar_corpo(conteudo)`: Gera o corpo com conteúdo
- `criar_rodape()`: Gera o rodapé
- `renderizar_app(conteudo)`: Retorna app completo como string
- `exibir(conteudo)`: Exibe o app no terminal

## Estrutura de Saída

```
========================================
           TÍTULO DO APP
========================================

Conteúdo do corpo aqui

----------------------------------------
    © 2025 - ELIS v2 - Modelo App
----------------------------------------
```

## Executar Exemplo

```bash
cd FERRAMENTAS/modelo_app
python exemplo_uso.py
```