#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerenciador de Regras ELIS v2
Ferramenta para inserir, editar e excluir regras do sistema MCP
"""

import os
import sys
import json
import datetime
from pathlib import Path

class GerenciadorRegras:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.mcp_dir = self.project_root / "MCP"
        self.rules_file = self.mcp_dir / "mcp_rules.py"
        self.backup_dir = self.project_root / "FERRAMENTAS" / "backups"
        self.backup_dir.mkdir(exist_ok=True)
    
    def criar_backup(self):
        """Cria backup do arquivo de regras atual"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"mcp_rules_backup_{timestamp}.py"
        
        if self.rules_file.exists():
            import shutil
            shutil.copy2(self.rules_file, backup_file)
            print(f"Backup criado: {backup_file.name}")
            return backup_file
        return None
    
    def listar_regras(self):
        """Lista todas as regras disponíveis"""
        print("\n=== REGRAS ATUAIS ===")
        
        if not self.rules_file.exists():
            print("Arquivo de regras não encontrado!")
            return
        
        with open(self.rules_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extrai a função iarules atual
        lines = content.split('\n')
        in_iarules = False
        regra_atual = []
        
        for line in lines:
            if 'def iarules():' in line and 'bkp' not in line:
                in_iarules = True
                continue
            elif in_iarules and line.strip().startswith('def '):
                break
            elif in_iarules and 'return' in line:
                regra_atual.append(line.strip())
        
        if regra_atual:
            print("Regra ativa:")
            for linha in regra_atual:
                print(f"  {linha}")
        else:
            print("Nenhuma regra encontrada")
    
    def inserir_regra(self, nova_regra):
        """Insere uma nova regra"""
        print(f"\nInserindo nova regra: {nova_regra}")
        
        # Cria backup antes de modificar
        self.criar_backup()
        
        # Lê o arquivo atual
        with open(self.rules_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Substitui o return da função iarules
        lines = content.split('\n')
        new_lines = []
        in_iarules = False
        
        for line in lines:
            if 'def iarules():' in line and 'bkp' not in line:
                in_iarules = True
                new_lines.append(line)
            elif in_iarules and line.strip().startswith('return'):
                new_lines.append(f'    return "{nova_regra}"')
                in_iarules = False
            elif in_iarules and line.strip().startswith('def '):
                new_lines.append(f'    return "{nova_regra}"')
                new_lines.append(line)
                in_iarules = False
            else:
                new_lines.append(line)
        
        # Salva o arquivo modificado
        with open(self.rules_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        
        print("Regra inserida com sucesso!")
        print("ATENÇÃO: Aplique refresh manual nas configurações do Trae AI para ativar a regra.")
    
    def editar_regra(self, nova_regra):
        """Edita a regra atual"""
        print(f"\nEditando regra para: {nova_regra}")
        self.inserir_regra(nova_regra)  # Mesmo processo de inserção
    
    def excluir_regra(self):
        """Remove a regra atual (volta para padrão)"""
        print("\nExcluindo regra atual...")
        
        regra_padrao = "Sistema ELIS v2 - Regras padrão"
        self.inserir_regra(regra_padrao)
    
    def restaurar_backup(self, backup_file):
        """Restaura um backup específico"""
        backup_path = self.backup_dir / backup_file
        
        if not backup_path.exists():
            print(f"Backup {backup_file} não encontrado!")
            return
        
        import shutil
        shutil.copy2(backup_path, self.rules_file)
        print("Backup {backup_file} restaurado com sucesso!")
        print("ATENÇÃO: Aplique refresh manual nas configurações do Trae AI para ativar as alterações.")
    
    def listar_backups(self):
        """Lista todos os backups disponíveis"""
        print("\n=== BACKUPS DISPONÍVEIS ===")
        
        backups = list(self.backup_dir.glob("mcp_rules_backup_*.py"))
        
        if not backups:
            print("Nenhum backup encontrado")
            return
        
        for i, backup in enumerate(sorted(backups), 1):
            timestamp = backup.stem.replace('mcp_rules_backup_', '')
            data_formatada = datetime.datetime.strptime(timestamp, '%Y%m%d_%H%M%S')
            print(f"{i}. {backup.name} - {data_formatada.strftime('%d/%m/%Y %H:%M:%S')}")
    
    def aplicar_refresh(self):
        """Informa sobre refresh manual"""
        print("\n=== REFRESH MANUAL NECESSÁRIO ===")
        print("Para aplicar as alterações:")
        print("1. Abra as configurações do Trae AI")
        print("2. Vá para a seção MCP")
        print("3. Clique em 'Refresh' ou 'Reload'")
        print("4. As novas regras serão carregadas")
        print("=================================")
    
    def menu_principal(self):
        """Menu principal da ferramenta"""
        while True:
            print("\n" + "="*50)
            print("    GERENCIADOR DE REGRAS ELIS v2")
            print("="*50)
            print("1. Listar regras atuais")
            print("2. Inserir nova regra")
            print("3. Editar regra atual")
            print("4. Excluir regra atual")
            print("5. Listar backups")
            print("6. Restaurar backup")
            print("7. Instruções de refresh manual")
            print("0. Sair")
            print("="*50)
            
            opcao = input("Escolha uma opção: ").strip()
            
            if opcao == "1":
                self.listar_regras()
            
            elif opcao == "2":
                nova_regra = input("\nDigite a nova regra: ").strip()
                if nova_regra:
                    self.inserir_regra(nova_regra)
                else:
                    print("Regra não pode estar vazia!")
            
            elif opcao == "3":
                self.listar_regras()
                nova_regra = input("\nDigite a regra editada: ").strip()
                if nova_regra:
                    self.editar_regra(nova_regra)
                else:
                    print("Regra não pode estar vazia!")
            
            elif opcao == "4":
                confirma = input("\nTem certeza que deseja excluir a regra atual? (s/N): ")
                if confirma.lower() == 's':
                    self.excluir_regra()
            
            elif opcao == "5":
                self.listar_backups()
            
            elif opcao == "6":
                self.listar_backups()
                backup_nome = input("\nDigite o nome do backup para restaurar: ").strip()
                if backup_nome:
                    self.restaurar_backup(backup_nome)
            
            elif opcao == "7":
                self.aplicar_refresh()
            
            elif opcao == "0":
                print("\nSaindo do gerenciador de regras...")
                break
            
            else:
                print("\nOpção inválida! Tente novamente.")

def main():
    """Função principal"""
    gerenciador = GerenciadorRegras()
    gerenciador.menu_principal()

if __name__ == "__main__":
    main()