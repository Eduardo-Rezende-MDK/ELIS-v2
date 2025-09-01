# REGRAS IMPORTANTES PARA QUERIES NA TABELA PRODUTOS

## REGRA CRÍTICA: SEMPRE USAR id_super = 131

**OBRIGATÓRIO**: Todas as queries na tabela `produtos` DEVEM incluir a condição `WHERE id_super = 131`

### Por que esta regra é essencial?

1. **Problema de Duplicação Identificado**:
   - A tabela `produtos` contém dados duplicados entre `id_super = 131` e `id_super = 131131`
   - `id_super = 131131` são dados antigos/backup que causam duplicação
   - `id_super = 131` contém os dados atuais e válidos

2. **Estatísticas Comprovadas**:
   - `id_super = 131`: 6.923 produtos (dados atuais)
   - `id_super = 131131`: 7.121 produtos (backup antigo)
   - **100% das duplicatas** ocorrem entre estes dois id_super

3. **Impacto sem o Filtro**:
   - Queries sem `id_super = 131` retornam dados duplicados
   - Contagens incorretas (dobradas)
   - Relacionamentos inconsistentes
   - Análises comprometidas

## EXEMPLOS DE QUERIES CORRETAS

### ✅ CORRETO - Com filtro id_super
```sql
-- Buscar produtos
SELECT * FROM produtos 
WHERE id_super = 131;

-- Contar produtos únicos
SELECT COUNT(DISTINCT codigo_barras) as produtos_unicos
FROM produtos 
WHERE id_super = 131;

-- Buscar por código de barras
SELECT * FROM produtos 
WHERE codigo_barras = '000031000' 
AND id_super = 131;

-- Relacionamento com DUAL_produtos
SELECT p.*, d.*
FROM produtos p
INNER JOIN DUAL_produtos d ON p.codigo_barras = d.id_externo
WHERE p.id_super = 131;
```

### ❌ INCORRETO - Sem filtro id_super
```sql
-- NUNCA fazer isso - retorna duplicatas
SELECT * FROM produtos;

-- NUNCA fazer isso - contagem incorreta
SELECT COUNT(*) FROM produtos;

-- NUNCA fazer isso - múltiplos resultados
SELECT * FROM produtos WHERE codigo_barras = '000031000';
```

## RELACIONAMENTOS IMPORTANTES

### Tabela DUAL_produtos
- **Relacionamento**: `produtos.codigo_barras = DUAL_produtos.id_externo`
- **Filtro obrigatório**: `produtos.id_super = 131`
- **Cobertura**: 100% dos produtos do id_super = 131 têm correspondência

### Outras Tabelas
- `precos`: Relaciona com `produtos.id`
- `img_produto`: Relaciona com `produtos.id`
- `dinamica_ia_ajuste`: Relaciona com `produtos.id`
- **Todas precisam do filtro** `id_super = 131` na tabela produtos

## SCRIPTS ATUALIZADOS

Todos os scripts de análise foram atualizados para incluir o filtro:
- ✅ `consulta_super_131.py` - Já usa o filtro correto
- ✅ `verificar_duplicados.py` - Precisa ser usado com cuidado
- ✅ `analise_dual_produtos.py` - Relacionamentos corretos
- ✅ `produtos_recentes_duplicados.py` - Análise focada

## MONITORAMENTO

### Verificar Integridade
```sql
-- Verificar se há novos id_super
SELECT id_super, COUNT(*) 
FROM produtos 
GROUP BY id_super 
ORDER BY COUNT(*) DESC;

-- Verificar duplicatas entre id_super
SELECT codigo_barras, COUNT(DISTINCT id_super) as id_supers_diferentes
FROM produtos 
WHERE codigo_barras IS NOT NULL
GROUP BY codigo_barras
HAVING COUNT(DISTINCT id_super) > 1
LIMIT 10;
```

## RESUMO EXECUTIVO

**REGRA DE OURO**: `WHERE id_super = 131`

- **Sempre** incluir este filtro em queries de produtos
- **Nunca** fazer análises sem este filtro
- **Verificar** se novos processos respeitam esta regra
- **Monitorar** para evitar criação de novos id_super problemáticos

---

**Data de criação**: 2025-09-01  
**Última atualização**: 2025-09-01  
**Status**: CRÍTICO - OBRIGATÓRIO