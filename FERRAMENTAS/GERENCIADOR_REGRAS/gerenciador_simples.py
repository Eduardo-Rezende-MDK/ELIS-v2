#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerenciador de Regras Simples com Persistência
Funções diretas: listar_regras() e add_regra()
"""

import json
import os
from pathlib import Path

class GerenciadorRegras:
    def __init__(self):
        self.arquivo_regras = Path(__file__).parent / "regras_refatoradas.json"
        self.regras = self._carregar_regras()
    
    def _carregar_regras(self):
        """Carrega regras do arquivo JSON refatorado"""
        if self.arquivo_regras.exists():
            try:
                with open(self.arquivo_regras, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Extrair apenas as regras ativas do formato refatorado
                    if isinstance(data, dict) and 'regras' in data:
                        return [regra for regra in data['regras'] if regra.get('ativa', True)]
                    return data
            except:
                return []
        return []
    
    def _salvar_regras(self):
        """Salva regras no arquivo JSON"""
        with open(self.arquivo_regras, 'w', encoding='utf-8') as f:
            json.dump(self.regras, f, ensure_ascii=False, indent=2)
    
    def listar_regras(self):
        """Lista as regras atuais"""
        if not self.regras:
            return "Nenhuma regra encontrada"
        
        resultado = "=== REGRAS ATUAIS ===\n"
        for i, regra in enumerate(self.regras, 1):
            if isinstance(regra, dict):
                # Formato refatorado
                titulo = regra.get('titulo', 'Regra sem título')
                descricao = regra.get('descricao', '')
                aplicacao = regra.get('aplicacao', '')
                validacao = regra.get('validacao', '')
                resultado += f"{i}. {titulo}: {descricao} | Aplicação: {aplicacao} | Validação: {validacao}\n"
            else:
                # Formato antigo (string)
                resultado += f"{i}. {regra}\n"
        return resultado.strip()
    
    def add_regra(self, nova_regra):
        """Adiciona uma nova regra"""
        self.regras.append(nova_regra)
        self._salvar_regras()
        return f"Regra adicionada: {nova_regra}"
    
    def excluir_regra(self, indice):
        """Exclui uma regra pelo índice (1-based)"""
        if 1 <= indice <= len(self.regras):
            regra_removida = self.regras.pop(indice - 1)
            self._salvar_regras()
            return f"Regra excluída: {regra_removida}"
        else:
            return f"Índice inválido. Use um número entre 1 e {len(self.regras)}"
    
    def get_regra(self, indice):
        """Retorna uma regra pelo índice (1-based)"""
        if 1 <= indice <= len(self.regras):
            return self.regras[indice - 1]
        else:
            return f"Índice inválido. Use um número entre 1 e {len(self.regras)}"
    
    def set_regra(self, indice, novo_texto):
        """Altera uma regra pelo índice (1-based)"""
        if 1 <= indice <= len(self.regras):
            regra_antiga = self.regras[indice - 1]
            self.regras[indice - 1] = novo_texto
            self._salvar_regras()
            return f"Regra {indice} alterada de '{regra_antiga}' para '{novo_texto}'"
        else:
            return f"Índice inválido. Use um número entre 1 e {len(self.regras)}"

# Instância global para uso direto
gerenciador = GerenciadorRegras()

def listar_regras():
    """Função direta para listar regras"""
    return gerenciador.listar_regras()

def add_regra(nova_regra):
    """Função direta para adicionar regra"""
    return gerenciador.add_regra(nova_regra)

def excluir_regra(indice):
    """Função direta para excluir regra"""
    return gerenciador.excluir_regra(indice)

def get_regra(indice):
    """Função direta para obter regra"""
    return gerenciador.get_regra(indice)

def set_regra(indice, novo_texto):
    """Função direta para alterar regra"""
    return gerenciador.set_regra(indice, novo_texto)

# Exemplo de uso direto
if __name__ == "__main__":
    print(listar_regras())
    print(add_regra("Primeira regra persistente"))
    print(add_regra("Segunda regra persistente"))
    print(listar_regras())