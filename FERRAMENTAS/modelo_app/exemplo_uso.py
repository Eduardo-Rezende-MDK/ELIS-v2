from modelo_app import ModeloApp

def main():
    print("=== EXEMPLO 1: Interface StudyAI Padrão ===")
    # Criar instância do app StudyAI
    app = ModeloApp("StudyAI", "Administrador")
    
    # Exibir interface padrão StudyAI
    app.exibir()
    
    print("\n" + "="*60)
    print("=== EXEMPLO 2: Interface Personalizada ===")
    
    # Criar app personalizado
    app_custom = ModeloApp("MeuSistema", "Usuário")
    
    # Conteúdo personalizado
    conteudo_custom = """
Bem-vindo ao sistema personalizado!

Opções disponíveis:
1. Cadastrar dados
2. Consultar informações
3. Gerar relatórios
4. Configurações

Escolha uma opção:
"""
    
    # Exibir app personalizado
    app_custom.exibir(conteudo_custom)
    
    print("\n" + "="*60)
    print("=== EXEMPLO 3: Menu Interativo (descomentado para testar) ===")
    print("# Para testar o menu interativo, descomente a linha abaixo:")
    print("# app.menu_interativo()")
    
    # Descomente a linha abaixo para testar o menu interativo
    # app.menu_interativo()

def exemplo_menu_interativo():
    """Função separada para testar o menu interativo"""
    app = ModeloApp("StudyAI", "Estudante")
    app.menu_interativo()

if __name__ == "__main__":
    main()
    
    # Para testar o menu interativo, execute:
    # exemplo_menu_interativo()