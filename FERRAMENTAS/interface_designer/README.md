# Interface Designer - ELIS v2

Ferramenta visual para criar diagramas e wireframes de interface de usuário através de drag-and-drop.

## Funcionalidades

- **Editor Visual Drag-and-Drop**: Arraste componentes da sidebar para o canvas
- **Componentes Pré-definidos**: Header, navbar, botões, inputs, cards, etc.
- **Responsividade**: Visualização em diferentes dispositivos (Desktop, Tablet, Mobile)
- **Propriedades Editáveis**: Ajuste posição, tamanho e outras propriedades
- **Grid de Alinhamento**: Sistema de grid para posicionamento preciso
- **Exportação**: Salve o design em JSON para reutilização

## Como Usar

### 1. Abrir a Ferramenta
```bash
# Navegar até a pasta
cd FERRAMENTAS/interface_designer

# Abrir no navegador
start interface_designer.html
```

### 2. Criar Interface
1. **Arrastar Componentes**: Selecione componentes da sidebar esquerda
2. **Posicionar**: Arraste para o canvas central
3. **Editar Propriedades**: Clique no elemento e use o painel direito
4. **Ajustar Layout**: Mova e redimensione elementos conforme necessário

### 3. Componentes Disponíveis

#### Layout
- **Header**: Cabeçalho da página
- **Navbar**: Barra de navegação
- **Sidebar**: Barra lateral
- **Footer**: Rodapé
- **Container**: Container genérico

#### Formulários
- **Input**: Campo de entrada de texto
- **Button**: Botão de ação
- **Checkbox**: Caixa de seleção
- **Select**: Lista suspensa
- **Textarea**: Área de texto

#### Conteúdo
- **Text**: Texto simples
- **Title**: Título/cabeçalho
- **Image**: Placeholder para imagem
- **List**: Lista de itens
- **Card**: Card de conteúdo

#### Navegação
- **Menu**: Menu de navegação
- **Breadcrumb**: Trilha de navegação
- **Pagination**: Paginação
- **Tabs**: Abas/guias

### 4. Ferramentas do Canvas

- **Limpar**: Remove todos os elementos
- **Grid**: Liga/desliga o grid de alinhamento
- **Dispositivo**: Altera visualização (Desktop/Tablet/Mobile)
- **Exportar**: Baixa o design em formato JSON
- **Salvar**: Salva no localStorage do navegador

### 5. Painel de Propriedades

Ao selecionar um elemento, você pode editar:
- **Largura e Altura**: Dimensões do elemento
- **Posição X e Y**: Coordenadas no canvas
- **Excluir**: Remove o elemento selecionado

## Casos de Uso

### 1. Wireframes Rápidos
```
1. Selecione "Header" e posicione no topo
2. Adicione "Navbar" abaixo do header
3. Insira "Container" para conteúdo principal
4. Adicione "Footer" na parte inferior
```

### 2. Formulários
```
1. Arraste "Input" para campos de entrada
2. Adicione "Button" para ações
3. Use "Select" para opções
4. Posicione "Text" para labels
```

### 3. Dashboards
```
1. Crie layout com "Sidebar" e "Container"
2. Adicione múltiplos "Card" no container
3. Use "Menu" na sidebar
4. Insira "Title" para seções
```

## Exportação e Reutilização

### Formato JSON
O design é exportado em formato JSON estruturado:

```json
[
  {
    "type": "header",
    "id": "element_1",
    "x": 0,
    "y": 0,
    "width": 800,
    "height": 80
  },
  {
    "type": "button",
    "id": "element_2",
    "x": 100,
    "y": 150,
    "width": 120,
    "height": 40
  }
]
```

### Integração com Projeto
O JSON exportado pode ser usado para:
- Documentação de requisitos
- Comunicação com desenvolvedores
- Base para implementação real
- Versionamento de designs

## Atalhos e Dicas

- **Clique no canvas**: Desseleciona elemento atual
- **Arrastar elemento**: Move elemento selecionado
- **Grid ativo**: Facilita alinhamento preciso
- **Múltiplos dispositivos**: Teste responsividade
- **Salvar frequentemente**: Use a função salvar regularmente

## Limitações Atuais

- Componentes básicos (versão MVP)
- Sem suporte a cores personalizadas
- Sem layers ou agrupamento
- Sem desfazer/refazer
- Sem importação de designs salvos

## Próximas Melhorias

- [ ] Mais componentes (gráficos, tabelas, modais)
- [ ] Sistema de cores e temas
- [ ] Layers e agrupamento
- [ ] Histórico de ações (undo/redo)
- [ ] Importação de designs
- [ ] Exportação para HTML/CSS
- [ ] Colaboração em tempo real
- [ ] Templates pré-definidos

## Executar Ferramenta

```bash
# Método 1: Abrir diretamente
start interface_designer.html

# Método 2: Servidor local
python -m http.server 8080
# Acessar: http://localhost:8080/interface_designer.html
```

---

**Interface Designer** - Ferramenta visual para prototipagem rápida de interfaces no projeto ELIS v2.