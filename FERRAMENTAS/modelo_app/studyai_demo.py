from modelo_app import ModeloApp

def demo_studyai():
    """Demonstração da interface StudyAI baseada na imagem fornecida"""
    
    print("=== DEMONSTRAÇÃO STUDYAI - INTERFACE COMPLETA ===")
    
    # Criar app StudyAI
    app = ModeloApp("StudyAI", "Administrador")
    
    # Exibir interface padrão (sem conteúdo personalizado para usar o padrão StudyAI)
    app.exibir()
    
    print("\n" + "="*60)
    print("=== SIMULAÇÃO DE INTERAÇÃO ===")
    
    # Simular algumas interações
    print("\nUsuário selecionou: [5] RAG")
    print("Consulta: 'Preciso usar o sistema RAG'")
    print("\nResposta do sistema:")
    print("Não encontrei informações específicas sobre 'Preciso")
    print("usar o sistema RAG' na base de conhecimento.")
    print("Você pode tentar reformular sua pergunta ou adicionar mais contexto.")
    
    print("\n" + "-"*50)
    print("Campo de entrada: Digite abaixo o tema que você quer pesquisar...")
    
def demo_menu_completo():
    """Demonstração do menu interativo completo"""
    
    print("\n=== MENU INTERATIVO STUDYAI ===")
    print("Para testar o menu interativo completo, execute:")
    print("python -c \"from studyai_demo import *; menu_interativo_studyai()\"")
    
def menu_interativo_studyai():
    """Menu interativo StudyAI"""
    app = ModeloApp("StudyAI", "Administrador")
    
    print("Iniciando interface StudyAI interativa...")
    print("(Digite 'q' para sair a qualquer momento)\n")
    
    app.menu_interativo()

if __name__ == "__main__":
    demo_studyai()
    demo_menu_completo()