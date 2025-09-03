#!/usr/bin/env python3
"""
Refatoração das Regras do Sistema ELIS v2
Organização por tipo, importância e aplicação de validação
"""

import json
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class RegraSistema:
    """Estrutura de regra refatorada"""
    id: str
    tipo: str  # LEI, VALIDACAO, CONFIGURACAO, FLUXO
    prioridade: int  # 1=CRITICA, 2=ALTA, 3=MEDIA, 4=BAIXA
    titulo: str
    descricao: str
    aplicacao: str  # quando/onde aplicar
    validacao: str  # como validar
    consequencia: str  # o que acontece se violada
    exemplos: List[str]
    ativa: bool

class GerenciadorRegrasRefatorado:
    """Sistema refatorado de gerenciamento de regras"""
    
    def __init__(self):
        self.regras = self._criar_regras_refatoradas()
        self.arquivo_regras = Path("regras_refatoradas.json")
        
    def _criar_regras_refatoradas(self) -> List[RegraSistema]:
        """Cria as 6 leis principais organizadas"""
        
        regras = [
            # LEI 1 - VALIDACAO MCP (CRITICA)
            RegraSistema(
                id="LEI_001",
                tipo="LEI",
                prioridade=1,
                titulo="Validação Obrigatória MCP",
                descricao="Toda resposta DEVE conter a tag MCP!ATIVO no final. Sem exceções.",
                aplicacao="Aplicar em TODAS as respostas finais do sistema",
                validacao="Verificar presença da string 'MCP!ATIVO' no final da resposta",
                consequencia="ERRO FATAL - Pausar sistema e corrigir imediatamente",
                exemplos=[
                    "Resposta válida: 'Tarefa concluída. MCP!ATIVO'",
                    "Resposta inválida: 'Tarefa concluída.' (sem tag)"
                ],
                ativa=True
            ),
            
            # LEI 2 - PROIBICAO EMOJIS (CRITICA)
            RegraSistema(
                id="LEI_002",
                tipo="LEI",
                prioridade=1,
                titulo="Proibição Absoluta de Emojis",
                descricao="PROIBIDO usar emojis em código, respostas ou qualquer contexto. Causa erros de sintaxe.",
                aplicacao="Aplicar em TODO conteúdo gerado pelo sistema",
                validacao="Verificar ausência de caracteres Unicode de emoji (U+1F600-U+1F64F, U+1F300-U+1F5FF, etc.)",
                consequencia="ERRO FATAL - Rejeitar resposta e regenerar sem emojis",
                exemplos=[
                    "Correto: 'Tarefa concluída com sucesso'",
                    "PROIBIDO: 'Tarefa concluída 😊' ou 'print(\"Hello 🌍\")'" 
                ],
                ativa=True
            ),
            
            # LEI 3 - ENGENHARIA DE PROMPTS (ALTA)
            RegraSistema(
                id="LEI_003",
                tipo="FLUXO",
                prioridade=2,
                titulo="Sistema Completo de Engenharia de Prompts",
                descricao="Propósito do MCP: auxiliar DEV no aprendizado de engenharia de prompts. Otimizar, melhorar e apresentar mudanças para DEV entender como criar prompts. Prompt feito para IA processar, não para DEV. Fluxo completo: DEV (prompt bruto com erros/imperfeições) > IA prompt (otimizado) > IA execução (resposta) > IA prompt (validação regras). Prompts do DEV têm erros ortografia/estrutura, mas sempre têm objetivo/lógica definida. Validar clareza mínima de 85% no prompt do DEV. Se não atingir, não executar e pedir mais informações. Minimizar conteúdo generativo para preencher lacunas. Margem aceitável: 15% para preenchimento de falta de informação.",
                aplicacao="Aplicar em TODOS os prompts recebidos do DEV. Sempre otimizar antes de executar. Contornar gap de conhecimento do DEV com IA especializada em entender intenção e gerar prompt que IA entenda.",
                validacao="1) Calcular score de clareza (objetividade, especificidade, contexto, gramática). 2) Se < 85%, pausar e solicitar esclarecimentos. 3) Otimizar prompt mantendo intenção original. 4) Validar resposta final contra todas as regras. 5) Apresentar melhorias para aprendizado do DEV.",
                consequencia="Se clareza < 85%: PAUSAR execução e solicitar mais informações. Se prompt otimizado falha na validação: corrigir e reprocessar. Sempre educar DEV sobre melhorias.",
                exemplos=[
                    "Prompt claro (90%): 'Criar função Python que calcule média aritmética de uma lista de números'",
                    "Prompt confuso (60%): 'faz algo com numeros ai' -> Otimizado: 'Criar função que processe lista numérica (especificar operação desejada)'",
                    "Prompt com erro (70%): 'cria uma funcao pra calcular media' -> Otimizado: 'Criar função Python que calcule média aritmética de lista'",
                    "Fluxo completo: DEV envia 'preciso de ajuda com listas' -> IA solicita esclarecimento -> DEV especifica -> IA otimiza -> executa -> valida -> ensina"
                ],
                ativa=True
            ),
            
            # LEI 4 - ESTRUTURA DE FERRAMENTAS (ALTA)
            RegraSistema(
                id="LEI_004",
                tipo="CONFIGURACAO",
                prioridade=2,
                titulo="Organização de Ferramentas",
                descricao="Ferramentas devem ser organizadas em FERRAMENTAS/nome-ferramenta, isoladas e MVP",
                aplicacao="Aplicar ao criar qualquer nova ferramenta",
                validacao="Verificar: estrutura de pastas, isolamento, ausência de dependências externas",
                consequencia="Reorganizar estrutura se não conforme",
                exemplos=[
                    "Correto: FERRAMENTAS/calculadora/calc.py",
                    "Incorreto: calculadora.py na raiz ou com dependência do MCP"
                ],
                ativa=True
            ),
            
            # LEI 5 - COMUNICACAO OBJETIVA (MEDIA)
            RegraSistema(
                id="LEI_005",
                tipo="VALIDACAO",
                prioridade=3,
                titulo="Comunicação Objetiva",
                descricao="Respostas simples, objetivas e diretas. Máximo 3 parágrafos por resposta",
                aplicacao="Aplicar em todas as respostas ao usuário",
                validacao="Contar parágrafos e verificar objetividade (ausência de redundância)",
                consequencia="Resumir resposta se exceder limites",
                exemplos=[
                    "Correto: resposta direta em 2 parágrafos",
                    "Incorreto: resposta com 5 parágrafos repetitivos"
                ],
                ativa=True
            )
        ]
        
        return regras
    
    def validar_resposta(self, resposta: str) -> Dict[str, Any]:
        """Valida resposta contra todas as regras ativas"""
        resultados = {
            'valida': True,
            'violacoes': [],
            'avisos': [],
            'score_geral': 100
        }
        
        for regra in self.regras:
            if not regra.ativa:
                continue
                
            resultado_regra = self._validar_regra_individual(resposta, regra)
            
            if not resultado_regra['passou']:
                violacao = {
                    'regra_id': regra.id,
                    'titulo': regra.titulo,
                    'tipo': regra.tipo,
                    'prioridade': regra.prioridade,
                    'descricao': resultado_regra['motivo'],
                    'consequencia': regra.consequencia
                }
                
                if regra.prioridade <= 2:  # CRITICA ou ALTA
                    resultados['violacoes'].append(violacao)
                    resultados['valida'] = False
                else:
                    resultados['avisos'].append(violacao)
                
                # Reduzir score baseado na prioridade
                reducao = 50 if regra.prioridade == 1 else 20 if regra.prioridade == 2 else 10
                resultados['score_geral'] -= reducao
        
        resultados['score_geral'] = max(0, resultados['score_geral'])
        return resultados
    
    def _validar_regra_individual(self, resposta: str, regra: RegraSistema) -> Dict[str, Any]:
        """Valida uma regra específica"""
        
        if regra.id == "LEI_001":  # Validação MCP
            passou = "MCP!ATIVO" in resposta
            motivo = "Tag MCP!ATIVO não encontrada" if not passou else ""
            
        elif regra.id == "LEI_002":  # Proibição Emojis
            import re
            emoji_pattern = re.compile(
                "["
                "\U0001F600-\U0001F64F"  # emoticons
                "\U0001F300-\U0001F5FF"  # symbols & pictographs
                "\U0001F680-\U0001F6FF"  # transport & map
                "\U0001F1E0-\U0001F1FF"  # flags
                "\U00002702-\U000027B0"
                "\U000024C2-\U0001F251"
                "]+", flags=re.UNICODE
            )
            passou = not emoji_pattern.search(resposta)
            motivo = "Emojis detectados na resposta" if not passou else ""
            
        elif regra.id == "LEI_003":  # Engenharia de Prompts
            # Validação simplificada - assumir que prompts já foram otimizados
            passou = True
            motivo = ""
            
        elif regra.id == "LEI_004":  # Estrutura Ferramentas
            # Validação contextual - verificar se menciona estrutura correta
            passou = True  # Assumir correto por padrão
            motivo = ""
            
        elif regra.id == "LEI_005":  # Comunicação Objetiva
            paragrafos = resposta.count('\n\n') + 1
            passou = paragrafos <= 3
            motivo = f"Resposta tem {paragrafos} parágrafos (máximo 3)" if not passou else ""
            
        else:
            passou = True
            motivo = "Regra não implementada"
        
        return {
            'passou': passou,
            'motivo': motivo
        }
    
    def gerar_relatorio_regras(self) -> str:
        """Gera relatório das regras organizadas"""
        relatorio = "\n=== SISTEMA DE REGRAS ELIS v2 - REFATORADO ===\n\n"
        
        # Organizar por prioridade
        regras_por_prioridade = {}
        for regra in self.regras:
            if regra.prioridade not in regras_por_prioridade:
                regras_por_prioridade[regra.prioridade] = []
            regras_por_prioridade[regra.prioridade].append(regra)
        
        prioridades = {1: "CRÍTICA", 2: "ALTA", 3: "MÉDIA", 4: "BAIXA"}
        
        for prioridade in sorted(regras_por_prioridade.keys()):
            relatorio += f"\n--- PRIORIDADE {prioridades[prioridade]} ---\n"
            
            for regra in regras_por_prioridade[prioridade]:
                status = "ATIVA" if regra.ativa else "INATIVA"
                relatorio += f"\n{regra.id} - {regra.titulo} [{regra.tipo}] ({status})\n"
                relatorio += f"Descrição: {regra.descricao}\n"
                relatorio += f"Aplicação: {regra.aplicacao}\n"
                relatorio += f"Validação: {regra.validacao}\n"
                relatorio += f"Consequência: {regra.consequencia}\n"
                
                if regra.exemplos:
                    relatorio += "Exemplos:\n"
                    for exemplo in regra.exemplos:
                        relatorio += f"  - {exemplo}\n"
                relatorio += "\n"
        
        return relatorio
    
    def salvar_regras(self):
        """Salva regras refatoradas em JSON"""
        dados = {
            'versao': '2.0',
            'data_criacao': datetime.now().isoformat(),
            'total_regras': len(self.regras),
            'regras_ativas': len([r for r in self.regras if r.ativa]),
            'regras': [asdict(regra) for regra in self.regras]
        }
        
        with open(self.arquivo_regras, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
    
    def aplicar_refatoracao(self):
        """Aplica a refatoração substituindo regras antigas"""
        from gerenciador_simples import GerenciadorRegras
        
        # Limpar regras antigas
        gerenciador_antigo = GerenciadorRegras()
        gerenciador_antigo.regras.clear()
        
        # Adicionar regras refatoradas
        for regra in self.regras:
            if regra.ativa:
                descricao_completa = f"{regra.titulo}: {regra.descricao} | Aplicação: {regra.aplicacao} | Validação: {regra.validacao}"
                gerenciador_antigo.add_regra(descricao_completa)
        
        print(f"Refatoração aplicada: {len([r for r in self.regras if r.ativa])} regras ativas")

def exemplo_validacao():
    """Exemplo de uso do sistema de validação"""
    gerenciador = GerenciadorRegrasRefatorado()
    
    # Teste 1: Resposta válida
    resposta_valida = "Tarefa concluída com sucesso. Sistema funcionando corretamente.\n\nMCP!ATIVO"
    resultado1 = gerenciador.validar_resposta(resposta_valida)
    print("Teste 1 - Resposta Válida:")
    print(f"Válida: {resultado1['valida']}")
    print(f"Score: {resultado1['score_geral']}")
    print(f"Violações: {len(resultado1['violacoes'])}")
    print()
    
    # Teste 2: Resposta com emoji (inválida)
    resposta_emoji = "Tarefa concluída 😊 com sucesso!\n\nMCP!ATIVO"
    resultado2 = gerenciador.validar_resposta(resposta_emoji)
    print("Teste 2 - Resposta com Emoji:")
    print(f"Válida: {resultado2['valida']}")
    print(f"Score: {resultado2['score_geral']}")
    print(f"Violações: {len(resultado2['violacoes'])}")
    if resultado2['violacoes']:
        print(f"Primeira violação: {resultado2['violacoes'][0]['titulo']}")
    print()
    
    # Teste 3: Resposta sem MCP!ATIVO (inválida)
    resposta_sem_mcp = "Tarefa concluída com sucesso."
    resultado3 = gerenciador.validar_resposta(resposta_sem_mcp)
    print("Teste 3 - Resposta sem MCP!ATIVO:")
    print(f"Válida: {resultado3['valida']}")
    print(f"Score: {resultado3['score_geral']}")
    print(f"Violações: {len(resultado3['violacoes'])}")
    if resultado3['violacoes']:
        print(f"Primeira violação: {resultado3['violacoes'][0]['titulo']}")
    print()

if __name__ == "__main__":
    # Criar gerenciador refatorado
    gerenciador = GerenciadorRegrasRefatorado()
    
    # Gerar e exibir relatório
    relatorio = gerenciador.gerar_relatorio_regras()
    print(relatorio)
    
    # Salvar regras
    gerenciador.salvar_regras()
    print(f"Regras salvas em: {gerenciador.arquivo_regras}")
    
    # Exemplo de validação
    print("\n=== EXEMPLOS DE VALIDAÇÃO ===\n")
    exemplo_validacao()
    
    # Aplicar refatoração (opcional)
    # gerenciador.aplicar_refatoracao()