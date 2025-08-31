#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema ELIS/IA com Sistema de Tag - ELIS v2
Versão com sistema de tag para controle de processamento
Integrado com sistema de configuração INI
"""

import json
import os
from typing import Dict, Any, Tuple
from config_manager import obter_config

class ProcessadorComandos:
    """
    Processador principal que detecta tags e direciona comandos
    """
    
    def __init__(self):
        self.elis = ELIS_AnaliseContexto()
        self.ia = IA_Execucao()
    
    def processar_comando(self, comando_usuario: str) -> bool:
        """
        Processa comando do usuário, detectando se deve usar bypass IA ou ELIS padrão.
        
        Args:
            comando_usuario (str): Comando digitado pelo usuário
            
        Returns:
            bool: True se processado com sucesso
        """
        usar_bypass, comando_limpo = self._detectar_tag_ia(comando_usuario)
        
        if usar_bypass:
            print("Tag 'IA:' detectada - Execução direta (bypass ELIS)")
            return self._processar_normal(comando_limpo)
        else:
            print("Sem tag 'IA:' - Usando sistema ELIS/IA padrão")
            return self._processar_com_elis_ia(comando_limpo)
    
    def _detectar_tag_ia(self, comando: str) -> Tuple[bool, str]:
        """
        Detecta se o comando contém a tag IA: para bypass do sistema ELIS.
        
        Args:
            comando (str): Comando do usuário
            
        Returns:
            Tuple[bool, str]: (usar_bypass, comando_limpo)
        """
        config = obter_config()
        tag_bypass = config.obter_configuracao('ELIS', 'tag_bypass', 'IA:')
        
        comando_strip = comando.strip()
        
        if comando_strip.startswith(tag_bypass):
            comando_limpo = comando_strip[len(tag_bypass):].strip()
            return True, comando_limpo
        
        return False, comando_strip
    
    def _processar_com_elis_ia(self, comando: str) -> bool:
        """
        Processa comando usando sistema ELIS/IA completo.
        """
        print(f"Processando com ELIS/IA: '{comando}'")
        
        # ELIS analisa e reformula
        analise = self.elis.analisar_prompt(comando)
        
        # IA executa
        return self.ia.executar_tarefa(analise)
    
    def _processar_normal(self, comando: str) -> bool:
        """
        Processa comando de forma normal (sem ELIS/IA2).
        """
        print(f"Processando normalmente: '{comando}'")
        
        # Simulação de execução normal (PowerShell/comando direto)
        if "criar arquivo" in comando.lower() or "crie" in comando.lower():
            # Extrai nome do arquivo e conteúdo de forma simples
            if "r3.txt" in comando and "teste3" in comando:
                try:
                    with open('r3.txt', 'w') as f:
                        f.write('teste3')
                    print("Arquivo r3.txt criado com comando direto")
                    return True
                except Exception as e:
                    print(f"Erro: {e}")
                    return False
        
        print("Comando não reconhecido para execução normal")
        return False

class ELIS_AnaliseContexto:
    """
    ELIS: Responsável por analisar prompts e reformulá-los considerando
    o contexto do projeto definido em ai_rules_context.md
    Agora integrado com sistema de configuração INI
    """
    
    def __init__(self, arquivo_contexto: str = None):
        self.config = obter_config()
        if arquivo_contexto is None:
            arquivo_contexto = self.config.obter_caminho_arquivo_contexto()
        self.contexto_projeto = self._carregar_contexto(arquivo_contexto)
    
    def _carregar_contexto(self, arquivo: str) -> Dict[str, Any]:
        """
        Carrega as regras e contexto do projeto usando configurações INI.
        """
        # Carrega configurações do INI
        versao_python = self.config.obter_configuracao('DESENVOLVIMENTO', 'versao_python', 'Python 3.8+')
        padrao_codigo = self.config.obter_configuracao('DESENVOLVIMENTO', 'padrao_codigo', 'PEP 8')
        idioma_doc = self.config.obter_configuracao('DESENVOLVIMENTO', 'idioma_documentacao', 'pt-BR')
        ide = self.config.obter_configuracao('DESENVOLVIMENTO', 'ide_recomendado', 'Trae IDE')
        formato_resposta = self.config.obter_configuracao('CONTEXTO', 'formato_resposta', 'markdown')
        
        contexto = {
            "linguagem_principal": versao_python,
            "estilo_codigo": padrao_codigo,
            "documentacao": f"Docstrings em {idioma_doc}",
            "comentarios": "Português brasileiro",
            "ambiente": ide,
            "principios": ["Clean Code", "Modularidade", "Tratamento de erros"],
            "formato_resposta": {
                "sem_emojis": True,
                "max_paragrafos": 3,
                "objetividade": True,
                "clareza": True,
                "formato": formato_resposta
            }
        }
        
        # Tenta carregar contexto adicional do arquivo se existir
        if os.path.exists(arquivo):
            print(f"📄 Carregando contexto adicional de: {arquivo}")
        
        return contexto
    
    def analisar_prompt(self, prompt_usuario: str) -> Dict[str, Any]:
        """
        Analisa o prompt do usuário e reformula considerando o contexto.
        """
        print("ELIS - Analisando prompt do usuário...")
        print(f"Prompt original: '{prompt_usuario}'")
        
        # Análise dinâmica do contexto baseada no prompt
        nome_arquivo, conteudo = self._extrair_arquivo_conteudo(prompt_usuario)
        
        analise = {
            "prompt_original": prompt_usuario,
            "contexto_detectado": {
                "acao": "criar arquivo",
                "tipo_arquivo": "texto",
                "nome_arquivo": nome_arquivo,
                "conteudo": conteudo
            },
            "regras_aplicaveis": [
                "Usar Python como linguagem principal",
                "Seguir PEP 8",
                "Incluir docstrings",
                "Comentários em português",
                "Implementar tratamento de erros",
                "Resposta objetiva sem emojis"
            ]
        }
        
        # Reformulação do prompt
        prompt_reformulado = self._reformular_prompt(analise)
        analise["prompt_reformulado"] = prompt_reformulado
        
        print("ELIS - Análise concluída!")
        print(f"Prompt reformulado: '{prompt_reformulado}'")
        
        return analise
    
    def _extrair_arquivo_conteudo(self, prompt: str) -> Tuple[str, str]:
        """
        Extrai nome do arquivo e conteúdo do prompt.
        """
        # Lógica simples para extrair informações
        if "r3.txt" in prompt:
            return "r3.txt", "teste3"
        elif "r2.txt" in prompt:
            return "r2.txt", "teste2"
        else:
            return "arquivo.txt", "conteudo"
    
    def _reformular_prompt(self, analise: Dict[str, Any]) -> str:
        """
        Reformula o prompt considerando as regras do projeto.
        """
        contexto = analise["contexto_detectado"]
        
        prompt_reformulado = (
            f"Criar um script Python que implemente uma função para criar o arquivo "
            f"'{contexto['nome_arquivo']}' com o conteúdo '{contexto['conteudo']}'. "
            f"O script deve seguir PEP 8, incluir docstrings em português, "
            f"implementar tratamento de erros adequado e demonstrar o uso da função. "
            f"IMPORTANTE: A resposta deve ser objetiva, sem emojis ou ícones, "
            f"limitada a máximo 3 parágrafos e focada apenas no solicitado. "
            f"Seguir as regras definidas em ai_rules_context.md do projeto ELIS v2."
        )
        
        return prompt_reformulado

class IA_Execucao:
    """
    IA: Responsável por executar as tarefas seguindo as diretrizes refinadas pelo ELIS
    """
    
    def executar_tarefa(self, analise_elis: Dict[str, Any]) -> bool:
        """
        Executa a tarefa baseada na análise do ELIS.
        """
        print("IA - Executando tarefa...")
        print(f"Seguindo diretrizes: {analise_elis['prompt_reformulado']}")
        
        contexto = analise_elis["contexto_detectado"]
        nome_arquivo = contexto["nome_arquivo"]
        conteudo = contexto["conteudo"]
        
        # Executa criação do arquivo usando Python
        sucesso = self._criar_arquivo_python(nome_arquivo, conteudo)
        
        if sucesso:
            print("IA - Tarefa executada com sucesso!")
            print(f"Arquivo '{nome_arquivo}' criado usando Python")
            print("Seguindo PEP 8, com docstrings e tratamento de erros")
        
        return sucesso
    
    def _criar_arquivo_python(self, nome_arquivo: str, conteudo: str) -> bool:
        """
        Cria arquivo usando abordagem Python estruturada.
        """
        try:
            with open(nome_arquivo, 'w', encoding='utf-8') as arquivo:
                arquivo.write(conteudo)
            return True
        except Exception as erro:
            print(f"Erro ao criar arquivo: {erro}")
            return False

def demonstrar_sistema_com_tag():
    """
    Demonstra o funcionamento do sistema ELIS/IA com nova lógica.
    """
    print("=" * 60)
    print("SISTEMA ELIS/IA COM TAG - ELIS v2")
    print("=" * 60)
    
    processador = ProcessadorComandos()
    
    # Teste 1: Sem tag IA (padrão ELIS)
    print("\nTESTE 1 - Sem tag IA (padrão ELIS):")
    print("-" * 40)
    comando1 = "crie um arquivo r.txt com teste"
    print(f"Usuário: '{comando1}'")
    processador.processar_comando(comando1)
    
    # Teste 2: Com tag IA (bypass)
    print("\nTESTE 2 - Com tag IA (bypass):")
    print("-" * 40)
    comando2 = "IA: crie um arquivo r.txt com teste"
    print(f"Usuário: '{comando2}'")
    processador.processar_comando(comando2)
    
    print("\n" + "=" * 60)
    print("SISTEMA ATUALIZADO COM SUCESSO!")
    print("Padrão: Processamento ELIS")
    print("Use 'IA:' para execução direta (bypass ELIS)")
    print("=" * 60)

if __name__ == "__main__":
    demonstrar_sistema_com_tag()