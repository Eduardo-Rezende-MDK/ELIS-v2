class ModeloApp:
    def __init__(self, titulo="StudyAI", usuario="Administrador"):
        self.titulo = titulo
        self.usuario = usuario
        self.conteudo_corpo = ""
        
    def criar_header(self):
        header = f"""
========================================
    {self.titulo} - Olá, {self.usuario}!
========================================
"""
        return header
    
    def criar_corpo_studyai(self):
        corpo = """
Como posso te ajudar hoje?
Faça perguntas sobre seus estudos ou solicite trabalhos acadêmicos

[1] Ensaio          [2] Pesquisa
[3] Exercícios      [4] Estudos
[5] RAG

----------------------------------------
Preciso usar o sistema RAG

Não encontrei informações específicas sobre 'Preciso
usar o sistema RAG' na base de conhecimento. Você pode
tentar reformular sua pergunta ou adicionar mais contexto.

Digite abaixo o tema que você quer pesquisar...
"""
        return corpo
    
    def criar_corpo(self, conteudo=None):
        if conteudo is None:
            return self.criar_corpo_studyai()
        self.conteudo_corpo = conteudo
        corpo = f"""
{conteudo}
"""
        return corpo
    
    def criar_rodape(self):
        rodape = """
----------------------------------------
    © 2025 - ELIS v2 - StudyAI Interface
----------------------------------------
"""
        return rodape
    
    def renderizar_app(self, conteudo_corpo=None):
        if conteudo_corpo:
            self.conteudo_corpo = conteudo_corpo
            
        app_completo = (
            self.criar_header() +
            "\n" +
            self.criar_corpo(self.conteudo_corpo) +
            "\n" +
            self.criar_rodape()
        )
        
        return app_completo
    
    def exibir(self, conteudo_corpo=None):
        print(self.renderizar_app(conteudo_corpo))
    
    def menu_interativo(self):
        while True:
            self.exibir()
            opcao = input("\nEscolha uma opção (1-5) ou 'q' para sair: ")
            
            if opcao == 'q':
                print("Saindo...")
                break
            elif opcao == '1':
                print("\nMódulo Ensaio selecionado")
                tema = input("Digite o tema do ensaio: ")
                print(f"Gerando ensaio sobre: {tema}")
            elif opcao == '2':
                print("\nMódulo Pesquisa selecionado")
                tema = input("Digite o tema da pesquisa: ")
                print(f"Iniciando pesquisa sobre: {tema}")
            elif opcao == '3':
                print("\nMódulo Exercícios selecionado")
                materia = input("Digite a matéria: ")
                print(f"Gerando exercícios de: {materia}")
            elif opcao == '4':
                print("\nMódulo Estudos selecionado")
                assunto = input("Digite o assunto: ")
                print(f"Material de estudo para: {assunto}")
            elif opcao == '5':
                print("\nMódulo RAG selecionado")
                consulta = input("Digite sua consulta RAG: ")
                print(f"Processando consulta RAG: {consulta}")
            else:
                print("Opção inválida!")
            
            input("\nPressione Enter para continuar...")