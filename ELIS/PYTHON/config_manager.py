#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerenciador de Configurações do Sistema ELIS/IA2

Este módulo é responsável por carregar e gerenciar as configurações
do sistema ELIS a partir do arquivo config.ini.

Autor: Sistema ELIS v2
Data: 2024
"""

import configparser
import os
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigManager:
    """
    Gerenciador de configurações do sistema ELIS.
    
    Carrega e fornece acesso às configurações definidas no arquivo config.ini.
    """
    
    def __init__(self, config_path: str = "../../config.ini"):
        """
        Inicializa o gerenciador de configurações.
        
        Args:
            config_path (str): Caminho para o arquivo de configuração
        """
        self.config_path = config_path
        self.config = configparser.ConfigParser()
        self._carregar_configuracoes()
    
    def _carregar_configuracoes(self) -> None:
        """
        Carrega as configurações do arquivo INI.
        
        Raises:
            FileNotFoundError: Se o arquivo de configuração não for encontrado
            configparser.Error: Se houver erro na leitura do arquivo INI
        """
        try:
            if not os.path.exists(self.config_path):
                raise FileNotFoundError(f"Arquivo de configuração não encontrado: {self.config_path}")
            
            self.config.read(self.config_path, encoding='utf-8')
            print(f"✅ Configurações carregadas de: {self.config_path}")
            
        except Exception as e:
            print(f"❌ Erro ao carregar configurações: {e}")
            raise
    
    def obter_configuracao(self, secao: str, chave: str, padrao: Any = None) -> Any:
        """
        Obtém uma configuração específica.
        
        Args:
            secao (str): Nome da seção no arquivo INI
            chave (str): Nome da chave na seção
            padrao (Any): Valor padrão se a configuração não existir
            
        Returns:
            Any: Valor da configuração ou valor padrão
        """
        try:
            return self.config.get(secao, chave)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return padrao
    
    def obter_configuracao_bool(self, secao: str, chave: str, padrao: bool = False) -> bool:
        """
        Obtém uma configuração booleana.
        
        Args:
            secao (str): Nome da seção no arquivo INI
            chave (str): Nome da chave na seção
            padrao (bool): Valor padrão se a configuração não existir
            
        Returns:
            bool: Valor booleano da configuração
        """
        try:
            return self.config.getboolean(secao, chave)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return padrao
    
    def obter_configuracao_int(self, secao: str, chave: str, padrao: int = 0) -> int:
        """
        Obtém uma configuração inteira.
        
        Args:
            secao (str): Nome da seção no arquivo INI
            chave (str): Nome da chave na seção
            padrao (int): Valor padrão se a configuração não existir
            
        Returns:
            int: Valor inteiro da configuração
        """
        try:
            return self.config.getint(secao, chave)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return padrao
    
    def obter_todas_configuracoes(self, secao: str) -> Dict[str, str]:
        """
        Obtém todas as configurações de uma seção.
        
        Args:
            secao (str): Nome da seção no arquivo INI
            
        Returns:
            Dict[str, str]: Dicionário com todas as configurações da seção
        """
        try:
            return dict(self.config.items(secao))
        except configparser.NoSectionError:
            return {}
    
    def listar_secoes(self) -> list:
        """
        Lista todas as seções disponíveis no arquivo de configuração.
        
        Returns:
            list: Lista com nomes das seções
        """
        return self.config.sections()
    
    def configuracao_existe(self, secao: str, chave: str = None) -> bool:
        """
        Verifica se uma seção ou configuração específica existe.
        
        Args:
            secao (str): Nome da seção
            chave (str, optional): Nome da chave (se None, verifica apenas a seção)
            
        Returns:
            bool: True se existir, False caso contrário
        """
        if not self.config.has_section(secao):
            return False
        
        if chave is None:
            return True
        
        return self.config.has_option(secao, chave)
    
    def recarregar_configuracoes(self) -> None:
        """
        Recarrega as configurações do arquivo INI.
        """
        self._carregar_configuracoes()
    
    def obter_status_ia(self) -> bool:
        """
        Obtém o status de ativação do IA.
        
        Returns:
            bool: True se IA está ativo
        """
        return self.obter_configuracao('IA', 'ativo', 'true').lower() == 'true'
    
    def obter_tag_bypass(self) -> str:
        """
        Obtém a tag de bypass do ELIS.
        
        Returns:
            str: Tag de bypass (padrão: 'IA:')
        """
        return self.obter_configuracao('ELIS', 'tag_bypass', 'IA:')
    
    def obter_caminho_arquivo_contexto(self) -> str:
        """
        Obtém o caminho completo para o arquivo de contexto.
        
        Returns:
            str: Caminho para o arquivo de contexto
        """
        arquivo_contexto = self.obter_configuracao('CONTEXTO', 'arquivo_contexto', 'IA/ai_rules_context.md')
        return os.path.abspath(arquivo_contexto)
    
    def obter_caminho_arquivo_andamento(self) -> str:
        """
        Obtém o caminho completo para o arquivo de andamento.
        
        Returns:
            str: Caminho para o arquivo de andamento
        """
        arquivo_andamento = self.obter_configuracao('ARQUIVOS', 'arquivo_andamento', 'IA/andamento.md')
        return os.path.abspath(arquivo_andamento)

# Instância global do gerenciador de configurações
config_manager = ConfigManager()

def obter_config() -> ConfigManager:
    """
    Função utilitária para obter a instância do gerenciador de configurações.
    
    Returns:
        ConfigManager: Instância do gerenciador de configurações
    """
    return config_manager

if __name__ == "__main__":
    # Teste do gerenciador de configurações
    try:
        config = ConfigManager()
        print("\n=== Teste do Gerenciador de Configurações ===")
        print(f"Seções disponíveis: {config.listar_secoes()}")
        print(f"Nome do sistema: {config.obter_configuracao('ELIS', 'nome_sistema')}")
        print(f"Tag de ativação: {config.obter_configuracao('ELIS', 'tag_ativacao')}")
        print(f"IA ativo: {config.obter_configuracao_bool('IA', 'ativo')}")
        print(f"Arquivo de contexto: {config.obter_caminho_arquivo_contexto()}")
        print(f"Arquivo de andamento: {config.obter_caminho_arquivo_andamento()}")
        print("✅ Teste concluído com sucesso!")
    except Exception as e:
        print(f"❌ Erro no teste: {e}")