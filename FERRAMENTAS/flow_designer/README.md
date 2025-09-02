# Flow Designer - ELIS v2

Ferramenta especializada para criar diagramas de fluxo de navegação e user flows, ideal para mapear jornadas do usuário como "Login → Autenticação → Home → etc".

## Funcionalidades

- **Nós Especializados**: Páginas, processos, decisões e finalizadores
- **Conexões Visuais**: Sistema de setas para mapear fluxos
- **Templates Prontos**: Fluxos pré-definidos (Login, Cadastro)
- **Auto Layout**: Organização automática dos elementos
- **Exportação/Importação**: Salve e compartilhe diagramas em JSON
- **Zoom e Navegação**: Visualização em diferentes escalas

## Tipos de Nós

### 📄 Páginas
- **Uso**: Telas, interfaces, páginas web
- **Exemplo**: "Página Login", "Dashboard", "Perfil do Usuário"
- **Visual**: Retângulo azul com gradiente

### ⚙️ Processos
- **Uso**: Ações, funções, operações
- **Exemplo**: "Validar Credenciais", "Enviar Email", "Salvar Dados"
- **Visual**: Retângulo rosa com gradiente

### ❓ Decisões
- **Uso**: Condições, validações, bifurcações
- **Exemplo**: "Login Válido?", "Usuário Logado?", "Dados OK?"
- **Visual**: Círculo azul claro

### ✅ Finalizadores
- **Uso**: Término do fluxo, estados finais
- **Exemplo**: "Sucesso", "Erro", "Logout Completo"
- **Visual**: Círculo verde pequeno

## Como Usar

### 1. Criar Fluxo Básico
```
1. Arraste "Página" da sidebar → Canvas
2. Adicione "Processo" para ações
3. Use "Decisão" para condições
4. Finalize com "Fim"
```

### 2. Conectar Elementos
```
1. Clique em "🔗 Conectar" na toolbar
2. Clique no primeiro nó (origem)
3. Clique no segundo nó (destino)
4. Conexão criada automaticamente
```

### 3. Editar Propriedades
```
1. Clique em qualquer nó
2. Use painel direito para editar:
   - Título do nó
   - Descrição/subtítulo
   - Tipo do nó
   - Posição
```

## Templates Incluídos

### 🔐 Fluxo de Login
```
Página Login → Validar Credenciais → Válido? 
                                      ↓ Sim
                                   Dashboard
                                      ↓ Não
                                 Erro Login → (volta ao Login)
```

### 📝 Fluxo de Cadastro
```
Formulário → Validar Dados → Dados OK?
                               ↓ Sim
                          Salvar Usuário → Sucesso
                               ↓ Não
                         Erro Validação → (volta ao Formulário)
```

## Casos de Uso Práticos

### 1. App Educacional - Fluxo Principal
```
Splash Screen → Login/Cadastro → Dashboard → Criar Trabalho → Editor → Salvar → Biblioteca
```

### 2. Sistema de Autenticação
```
Login → Verificar Credenciais → 2FA? → Código SMS → Validar → Home
                                 ↓ Não
                               Home
```

### 3. Processo de Pagamento
```
Carrinho → Checkout → Escolher Pagamento → Processar → Sucesso/Erro
```

### 4. Fluxo de Recuperação de Senha
```
Esqueci Senha → Email → Verificar Token → Nova Senha → Confirmar → Login
```

## Ferramentas da Interface

### Toolbar Principal
- **🗑️ Limpar**: Remove todos os elementos
- **🔗 Conectar**: Ativa modo de conexão
- **📐 Auto Layout**: Organiza elementos automaticamente
- **💾 Exportar**: Salva diagrama em JSON
- **📂 Importar**: Carrega diagrama salvo
- **Zoom**: 50% a 150% de visualização

### Painel de Propriedades
- **Informações do Fluxo**: Contadores de nós e conexões
- **Propriedades do Nó**: Edição de título, descrição, tipo
- **Posicionamento**: Coordenadas X e Y
- **Ações**: Excluir nó selecionado

## Exportação e Documentação

### Formato JSON
```json
{
  "nodes": [
    {
      "id": "node_1",
      "type": "page",
      "title": "Página Login",
      "subtitle": "Tela de autenticação",
      "x": 100,
      "y": 100
    }
  ],
  "connections": [
    {
      "source": "node_1",
      "target": "node_2"
    }
  ],
  "metadata": {
    "created": "2025-01-09T...",
    "nodeCount": 5,
    "connectionCount": 4
  }
}
```

### Uso do JSON Exportado
- **Documentação**: Anexar em especificações
- **Comunicação**: Compartilhar com equipe
- **Versionamento**: Controlar mudanças no fluxo
- **Implementação**: Base para desenvolvimento

## Dicas e Melhores Práticas

### Organização Visual
- Use **Auto Layout** para organizar elementos
- Mantenha fluxos da **esquerda para direita**
- Agrupe elementos relacionados
- Use **zoom** para trabalhar com fluxos grandes

### Nomenclatura
- **Páginas**: Nomes claros ("Dashboard", "Perfil")
- **Processos**: Verbos de ação ("Validar", "Enviar")
- **Decisões**: Perguntas ("Logado?", "Válido?")
- **Fins**: Estados finais ("Sucesso", "Erro")

### Fluxos Complexos
- Divida em **sub-fluxos** menores
- Use **templates** como base
- Documente **condições** nas decisões
- Teste **todos os caminhos** possíveis

## Limitações Atuais

- Conexões apenas ponto-a-ponto
- Sem suporte a swimlanes
- Sem agrupamento de nós
- Sem anotações/comentários
- Sem exportação para imagem

## Próximas Melhorias

- [ ] Swimlanes para diferentes atores
- [ ] Agrupamento e layers
- [ ] Anotações e comentários
- [ ] Exportação PNG/SVG
- [ ] Mais templates (E-commerce, CRM, etc.)
- [ ] Validação de fluxos
- [ ] Colaboração em tempo real
- [ ] Integração com ferramentas de design

## Executar Ferramenta

```bash
# Navegar até a pasta
cd FERRAMENTAS/flow_designer

# Método 1: Abrir diretamente
start flow_designer.html

# Método 2: Servidor local
python -m http.server 8082
# Acessar: http://localhost:8082/flow_designer.html
```

## Integração com Projeto

Esta ferramenta é ideal para:
- **Planejamento**: Mapear fluxos antes do desenvolvimento
- **Documentação**: Criar especificações visuais
- **Comunicação**: Alinhar equipe sobre navegação
- **Testes**: Validar todos os caminhos possíveis
- **Manutenção**: Documentar mudanças no fluxo

---

**Flow Designer** - Ferramenta especializada para diagramas de fluxo de navegação no projeto ELIS v2.