#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configurador de Prompt ELIS v2
Ferramenta para usar o retorno da função iarules como configuração de prompt
"""

import os
import sys
import json
import datetime
from pathlib import Path

class ConfiguradorPrompt:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.mcp_dir = self.project_root / "MCP"
        self.rules_file = self.mcp_dir / "mcp_rules.py"
        self.config_dir = self.project_root / "FERRAMENTAS" / "configs"
        self.config_dir.mkdir(exist_ok=True)
        self.prompt_config_file = self.config_dir / "prompt_config.json"
    
    def obter_regras_atuais(self):
        """Obtém as regras atuais da função iarules"""
        try:
            # Adiciona o diretório MCP ao path
            sys.path.insert(0, str(self.mcp_dir))
            
            # Importa o módulo mcp_rules
            import mcp_rules
            
            # Força reload para pegar alterações
            import importlib
            importlib.reload(mcp_rules)
            
            # Obtém as regras
            regras = mcp_rules.iarules()
            
            return regras
            
        except Exception as e:
            print(f"Erro ao obter regras: {e}")
            return None
    
    def criar_configuracao_prompt(self, regras):
        """Cria configuração de prompt baseada nas regras"""
        config = {
            "timestamp": datetime.datetime.now().isoformat(),
            "regras_fonte": regras,
            "configuracao_prompt": {
                "system_message": f"Você é um assistente AI. Siga estas regras: {regras}",
                "instructions": regras,
                "behavior_rules": regras.split(", ") if ", " in regras else [regras],
                "response_format": self.extrair_formato_resposta(regras),
                "restrictions": self.extrair_restricoes(regras)
            }
        }
        
        return config
    
    def extrair_formato_resposta(self, regras):
        """Extrai informações sobre formato de resposta das regras"""
        formato = {
            "max_paragrafos": None,
            "estilo": "normal",
            "elementos_proibidos": []
        }
        
        regras_lower = regras.lower()
        
        # Extrai número máximo de parágrafos
        if "3 paragrafos" in regras_lower or "3 parágrafos" in regras_lower:
            formato["max_paragrafos"] = 3
        elif "2 paragrafos" in regras_lower or "2 parágrafos" in regras_lower:
            formato["max_paragrafos"] = 2
        elif "1 paragrafo" in regras_lower or "1 parágrafo" in regras_lower:
            formato["max_paragrafos"] = 1
        
        # Identifica estilo
        if "curtas" in regras_lower and "objetivas" in regras_lower:
            formato["estilo"] = "conciso"
        elif "técnicas" in regras_lower and "detalhadas" in regras_lower:
            formato["estilo"] = "técnico_detalhado"
        elif "objetivas" in regras_lower:
            formato["estilo"] = "objetivo"
        
        # Identifica elementos proibidos
        if "sem" in regras_lower:
            if "emoji" in regras_lower:
                formato["elementos_proibidos"].append("emojis")
            if "imagem" in regras_lower:
                formato["elementos_proibidos"].append("imagens")
            if "icone" in regras_lower or "ícone" in regras_lower:
                formato["elementos_proibidos"].append("ícones")
        
        return formato
    
    def extrair_restricoes(self, regras):
        """Extrai restrições específicas das regras"""
        restricoes = []
        
        regras_lower = regras.lower()
        
        if "sem uso de imagem" in regras_lower:
            restricoes.append("Não usar imagens")
        if "sem emoji" in regras_lower:
            restricoes.append("Não usar emojis")
        if "sem icone" in regras_lower or "sem ícone" in regras_lower:
            restricoes.append("Não usar ícones")
        if "máximo" in regras_lower and "paragrafo" in regras_lower:
            restricoes.append("Respeitar limite de parágrafos")
        if "curtas" in regras_lower:
            restricoes.append("Manter respostas concisas")
        if "objetivas" in regras_lower:
            restricoes.append("Ser direto e objetivo")
        
        return restricoes
    
    def salvar_configuracao(self, config):
        """Salva a configuração de prompt em arquivo JSON"""
        try:
            with open(self.prompt_config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print(f"Configuração salva em: {self.prompt_config_file}")
            return True
            
        except Exception as e:
            print(f"Erro ao salvar configuração: {e}")
            return False
    
    def carregar_configuracao(self):
        """Carrega a configuração de prompt do arquivo JSON"""
        try:
            if self.prompt_config_file.exists():
                with open(self.prompt_config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                return config
            else:
                print("Arquivo de configuração não encontrado")
                return None
                
        except Exception as e:
            print(f"Erro ao carregar configuração: {e}")
            return None
    
    def gerar_prompt_personalizado(self, config, contexto=""):
        """Gera um prompt personalizado baseado na configuração"""
        if not config:
            return None
        
        prompt_config = config.get("configuracao_prompt", {})
        
        prompt = f"""
=== CONFIGURAÇÃO DE PROMPT ELIS v2 ===

REGRAS BASE: {config.get('regras_fonte', '')}

INSTRUÇÕES ESPECÍFICAS:
- System Message: {prompt_config.get('system_message', '')}
- Estilo: {prompt_config.get('response_format', {}).get('estilo', 'normal')}
- Máximo de parágrafos: {prompt_config.get('response_format', {}).get('max_paragrafos', 'Não especificado')}

RESTRIÇÕES:
"""
        
        restricoes = prompt_config.get('restrictions', [])
        for restricao in restricoes:
            prompt += f"- {restricao}\n"
        
        elementos_proibidos = prompt_config.get('response_format', {}).get('elementos_proibidos', [])
        if elementos_proibidos:
            prompt += f"\nELEMENTOS PROIBIDOS: {', '.join(elementos_proibidos)}\n"
        
        if contexto:
            prompt += f"\nCONTEXTO ADICIONAL: {contexto}\n"
        
        prompt += f"\n=== GERADO EM: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')} ===\n"
        
        return prompt
    
    def atualizar_configuracao_automatica(self):
        """Atualiza a configuração automaticamente baseada nas regras atuais"""
        print("Atualizando configuração baseada nas regras atuais...")
        
        # Obtém regras atuais
        regras = self.obter_regras_atuais()
        
        if not regras:
            print("Não foi possível obter as regras atuais")
            return False
        
        print(f"Regras obtidas: {regras}")
        
        # Cria configuração
        config = self.criar_configuracao_prompt(regras)
        
        # Salva configuração
        if self.salvar_configuracao(config):
            print("Configuração atualizada com sucesso!")
            return True
        else:
            return False
    
    def exibir_configuracao_atual(self):
        """Exibe a configuração atual de forma formatada"""
        config = self.carregar_configuracao()
        
        if not config:
            print("Nenhuma configuração encontrada")
            return
        
        print("\n=== CONFIGURAÇÃO ATUAL ===")
        print(f"Timestamp: {config.get('timestamp', 'N/A')}")
        print(f"Regras fonte: {config.get('regras_fonte', 'N/A')}")
        
        prompt_config = config.get('configuracao_prompt', {})
        response_format = prompt_config.get('response_format', {})
        
        print(f"\nEstilo: {response_format.get('estilo', 'N/A')}")
        print(f"Máx. parágrafos: {response_format.get('max_paragrafos', 'N/A')}")
        print(f"Elementos proibidos: {', '.join(response_format.get('elementos_proibidos', []))}")
        
        restricoes = prompt_config.get('restrictions', [])
        if restricoes:
            print("\nRestrições:")
            for restricao in restricoes:
                print(f"  - {restricao}")
    
    def menu_principal(self):
        """Menu principal da ferramenta"""
        while True:
            print("\n" + "="*50)
            print("    CONFIGURADOR DE PROMPT ELIS v2")
            print("="*50)
            print("1. Atualizar configuração (baseado nas regras atuais)")
            print("2. Exibir configuração atual")
            print("3. Gerar prompt personalizado")
            print("4. Ver regras atuais do MCP")
            print("5. Exportar configuração")
            print("0. Sair")
            print("="*50)
            
            opcao = input("Escolha uma opção: ").strip()
            
            if opcao == "1":
                self.atualizar_configuracao_automatica()
            
            elif opcao == "2":
                self.exibir_configuracao_atual()
            
            elif opcao == "3":
                config = self.carregar_configuracao()
                if config:
                    contexto = input("\nDigite contexto adicional (opcional): ").strip()
                    prompt = self.gerar_prompt_personalizado(config, contexto)
                    print("\n=== PROMPT GERADO ===")
                    print(prompt)
                else:
                    print("\nPrimeiro atualize a configuração (opção 1)")
            
            elif opcao == "4":
                regras = self.obter_regras_atuais()
                if regras:
                    print(f"\nRegras atuais: {regras}")
                else:
                    print("\nNão foi possível obter as regras")
            
            elif opcao == "5":
                config = self.carregar_configuracao()
                if config:
                    export_file = self.config_dir / f"prompt_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    try:
                        with open(export_file, 'w', encoding='utf-8') as f:
                            json.dump(config, f, indent=2, ensure_ascii=False)
                        print(f"\nConfiguração exportada para: {export_file}")
                    except Exception as e:
                        print(f"\nErro ao exportar: {e}")
                else:
                    print("\nNenhuma configuração para exportar")
            
            elif opcao == "0":
                print("\nSaindo do configurador de prompt...")
                break
            
            else:
                print("\nOpção inválida! Tente novamente.")

def main():
    """Função principal"""
    configurador = ConfiguradorPrompt()
    configurador.menu_principal()

if __name__ == "__main__":
    main()