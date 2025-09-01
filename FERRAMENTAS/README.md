# FERRAMENTAS ELIS v2

Diretório de ferramentas auxiliares para o sistema ELIS v2.

## Gerenciador de Regras

### Descrição
Ferramenta completa para gerenciar as regras do sistema MCP de forma interativa.

### Funcionalidades
- **Listar regras**: Visualiza as regras atualmente ativas
- **Inserir regra**: Adiciona uma nova regra ao sistema
- **Editar regra**: Modifica a regra atual
- **Excluir regra**: Remove a regra atual (volta ao padrão)
- **Backup automático**: Cria backup antes de cada modificação
- **Restaurar backup**: Permite restaurar versões anteriores
- **Instruções de refresh**: Orienta sobre como aplicar alterações manualmente

### Como usar

```bash
cd FERRAMENTAS
python gerenciador_regras.py
```

### Menu de opções

1. **Listar regras atuais** - Mostra a regra ativa no sistema
2. **Inserir nova regra** - Permite inserir uma nova regra
3. **Editar regra atual** - Modifica a regra existente
4. **Excluir regra atual** - Remove a regra (volta ao padrão)
5. **Listar backups** - Mostra todos os backups disponíveis
6. **Restaurar backup** - Restaura uma versão anterior
7. **Instruções de refresh manual** - Mostra como ativar as regras
0. **Sair** - Encerra a ferramenta

### Estrutura de arquivos

```
FERRAMENTAS/
├── gerenciador_regras.py    # Ferramenta principal
├── backups/                 # Diretório de backups automáticos
│   ├── mcp_rules_backup_20241201_143000.py
│   └── mcp_rules_backup_20241201_144500.py
└── README.md               # Esta documentação
```

### Recursos de segurança

- **Backup automático**: Antes de cada modificação, um backup é criado automaticamente
- **Timestamp único**: Cada backup tem data/hora única para identificação
- **Restauração fácil**: Interface simples para restaurar qualquer versão anterior
- **Validação**: Verifica se as regras não estão vazias antes de aplicar

### Integração com MCP

A ferramenta integra com:
- `mcp_rules.py` - Arquivo principal de regras
- Sistema de backup automático
- Requer refresh manual no Trae AI para ativar alterações

### Exemplo de uso

1. Execute a ferramenta: `python gerenciador_regras.py`
2. Escolha opção 2 para inserir nova regra
3. Digite: "Respostas devem ser técnicas e detalhadas"
4. A ferramenta criará backup e aplicará a regra no arquivo
5. Faça refresh manual no Trae AI (configurações > MCP > Refresh)
6. Use opção 1 para confirmar que a regra foi aplicada

### Troubleshooting

- Use a opção 7 para ver instruções de refresh manual
- Em caso de problemas, use a opção 6 para restaurar um backup
- Verifique se o diretório MCP existe e contém os arquivos necessários
- Sempre faça refresh manual no Trae AI após alterações