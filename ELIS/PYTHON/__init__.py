#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pacote ELIS Python

Este pacote contém todos os módulos Python do sistema ELIS:
- sistema_elis.py: Módulo principal do sistema ELIS
- elis_com_tag.py: Sistema ELIS com suporte a tags
- config_manager.py: Gerenciador de configurações

Autor: Sistema ELIS v2
Data: 2025
"""

__version__ = "2.0"
__author__ = "Sistema ELIS"

# Importações principais do pacote
from .config_manager import ConfigManager, obter_config
from .sistema_elis import ELIS_AnaliseContexto
from .elis_com_tag import ProcessadorComandos

__all__ = [
    'ConfigManager',
    'obter_config', 
    'ELIS_AnaliseContexto',
    'ProcessadorComandos'
]