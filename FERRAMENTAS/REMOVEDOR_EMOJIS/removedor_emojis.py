#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Removedor de Emojis - ELIS v2
Conforme Regra 2: Proibição Absoluta de Emojis
Ferramenta para detectar e remover emojis de qualquer texto
"""

import re
import os
from typing import Dict, List, Tuple

class RemovedorEmojis:
    def __init__(self):
        # Ranges Unicode para emojis (conforme Regra 2)
        self.emoji_ranges = [
            (0x1F600, 0x1F64F),  # Emoticons
            (0x1F300, 0x1F5FF),  # Símbolos diversos
            (0x1F680, 0x1F6FF),  # Transporte e símbolos de mapa
            (0x1F1E0, 0x1F1FF),  # Bandeiras regionais
            (0x2600, 0x26FF),    # Símbolos diversos
            (0x2700, 0x27BF),    # Dingbats
            (0xFE00, 0xFE0F),    # Seletores de variação
            (0x1F900, 0x1F9FF),  # Símbolos suplementares
            (0x1F018, 0x1F270),  # Símbolos diversos adicionais
        ]
        
        # Padrão regex para detectar emojis
        self.emoji_pattern = self._criar_padrao_emoji()
        
    def _criar_padrao_emoji(self) -> str:
        """Cria padrão regex para detectar todos os emojis"""
        # Padrão simplificado e funcional para detectar emojis
        pattern = r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002600-\U000026FF\U00002700-\U000027BF\U0001F900-\U0001F9FF\U0001F018-\U0001F270\U0000FE00-\U0000FE0F]'
        
        return pattern
    
    def detectar_emojis(self, texto: str) -> List[Dict]:
        """Detecta todos os emojis no texto e retorna informações detalhadas"""
        emojis_encontrados = []
        
        for match in re.finditer(self.emoji_pattern, texto):
            emoji_info = {
                'emoji': match.group(),
                'posicao': match.start(),
                'unicode': f'U+{ord(match.group()):04X}',
                'nome': self._obter_nome_emoji(match.group())
            }
            emojis_encontrados.append(emoji_info)
            
        return emojis_encontrados
    
    def _obter_nome_emoji(self, emoji: str) -> str:
        """Obtém nome descritivo do emoji"""
        # Mapeamento básico de alguns emojis comuns
        nomes = {
            '😀': 'GRINNING_FACE',
            '😊': 'SMILING_FACE_WITH_SMILING_EYES',
            '❤️': 'RED_HEART',
            '👍': 'THUMBS_UP',
            '🔥': 'FIRE',
            '💯': 'HUNDRED_POINTS',
            '🎉': 'PARTY_POPPER',
            '🚀': 'ROCKET'
        }
        
        return nomes.get(emoji, f'EMOJI_U+{ord(emoji):04X}')
    
    def remover_emojis(self, texto: str, substituir_por: str = '') -> str:
        """Remove todos os emojis do texto"""
        texto_limpo = re.sub(self.emoji_pattern, substituir_por, texto)
        
        # Remove espaços duplos resultantes da remoção
        texto_limpo = re.sub(r'\s+', ' ', texto_limpo).strip()
        
        return texto_limpo
    
    def analisar_texto(self, texto: str) -> Dict:
        """Análise completa do texto: detecta emojis e gera relatório"""
        emojis = self.detectar_emojis(texto)
        texto_limpo = self.remover_emojis(texto)
        
        return {
            'texto_original': texto,
            'texto_limpo': texto_limpo,
            'total_emojis': len(emojis),
            'emojis_encontrados': emojis,
            'conforme_regra2': len(emojis) == 0,
            'tamanho_original': len(texto),
            'tamanho_limpo': len(texto_limpo),
            'reducao_caracteres': len(texto) - len(texto_limpo)
        }
    
    def processar_arquivo(self, caminho_arquivo: str, salvar_limpo: bool = True) -> Dict:
        """Processa arquivo removendo emojis"""
        try:
            # Ler arquivo
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                conteudo = f.read()
            
            # Analisar conteúdo
            resultado = self.analisar_texto(conteudo)
            resultado['arquivo_original'] = caminho_arquivo
            
            # Salvar versão limpa se solicitado
            if salvar_limpo and resultado['total_emojis'] > 0:
                nome_base, extensao = os.path.splitext(caminho_arquivo)
                arquivo_limpo = f"{nome_base}_sem_emojis{extensao}"
                
                with open(arquivo_limpo, 'w', encoding='utf-8') as f:
                    f.write(resultado['texto_limpo'])
                
                resultado['arquivo_limpo'] = arquivo_limpo
            
            return resultado
            
        except Exception as e:
            return {
                'erro': str(e),
                'arquivo_original': caminho_arquivo,
                'sucesso': False
            }
    
    def validar_conformidade_regra2(self, texto: str) -> Dict:
        """Valida se texto está conforme Regra 2 (sem emojis)"""
        emojis = self.detectar_emojis(texto)
        
        return {
            'conforme': len(emojis) == 0,
            'violacoes': len(emojis),
            'emojis_encontrados': [e['emoji'] for e in emojis],
            'posicoes': [e['posicao'] for e in emojis],
            'status': 'APROVADO' if len(emojis) == 0 else 'REJEITADO - CONTÉM EMOJIS',
            'acao_requerida': 'Nenhuma' if len(emojis) == 0 else 'Remover emojis antes de prosseguir'
        }

def main():
    """Exemplo de uso da ferramenta"""
    removedor = RemovedorEmojis()
    
    # Testes com diferentes tipos de texto
    textos_teste = [
        "Olá! Como você está? 😊",
        "Projeto finalizado! 🎉🚀 Muito bom! 👍",
        "Código Python sem emojis - conforme regra",
        "Erro no sistema 💥 precisa corrigir 🔧",
        "print('Hello World') # sem emojis"
    ]
    
    print("=== REMOVEDOR DE EMOJIS - ELIS v2 ===")
    print("Conforme Regra 2: Proibição Absoluta de Emojis\n")
    
    for i, texto in enumerate(textos_teste, 1):
        print(f"TESTE {i}:")
        resultado = removedor.analisar_texto(texto)
        
        print(f"Original: {resultado['texto_original']}")
        print(f"Limpo: {resultado['texto_limpo']}")
        print(f"Emojis encontrados: {resultado['total_emojis']}")
        print(f"Conforme Regra 2: {resultado['conforme_regra2']}")
        
        if resultado['emojis_encontrados']:
            print("Emojis detectados:")
            for emoji_info in resultado['emojis_encontrados']:
                print(f"  - {emoji_info['emoji']} ({emoji_info['nome']}) na posição {emoji_info['posicao']}")
        
        # Validação de conformidade
        validacao = removedor.validar_conformidade_regra2(texto)
        print(f"Status: {validacao['status']}")
        print(f"Ação: {validacao['acao_requerida']}")
        print("-" * 50)

if __name__ == "__main__":
    main()