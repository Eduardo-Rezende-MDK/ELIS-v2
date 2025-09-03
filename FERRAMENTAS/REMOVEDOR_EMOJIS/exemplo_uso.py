#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exemplo de Uso - Removedor de Emojis
Demonstra como usar a ferramenta para aplicar a Regra 2
"""

from removedor_emojis import RemovedorEmojis
import os

def demonstrar_deteccao_emojis():
    """Demonstra detecção de diferentes tipos de emojis"""
    removedor = RemovedorEmojis()
    
    print("=== DETECÇÃO DE EMOJIS ===")
    
    textos_com_emojis = [
        "Olá! 😊 Como você está?",
        "Projeto concluído! 🎉🚀",
        "Erro no código 💥 precisa corrigir 🔧",
        "Amo programar! ❤️ Python é incrível! 🐍",
        "Festa hoje! 🎊🍰🎈 Vamos comemorar! 🥳"
    ]
    
    for texto in textos_com_emojis:
        print(f"\nTexto: {texto}")
        emojis = removedor.detectar_emojis(texto)
        print(f"Emojis encontrados: {len(emojis)}")
        
        for emoji_info in emojis:
            print(f"  - {emoji_info['emoji']} ({emoji_info['nome']}) na posição {emoji_info['posicao']}")

def demonstrar_remocao_emojis():
    """Demonstra remoção de emojis de textos"""
    removedor = RemovedorEmojis()
    
    print("\n=== REMOÇÃO DE EMOJIS ===")
    
    textos_teste = [
        "Código funcionando! 👍 Sem bugs! 🐛❌",
        "function hello() { console.log('Oi! 👋'); }",
        "# Comentário com emoji 📝 no código Python 🐍",
        "SELECT * FROM users WHERE active = 1; -- Query OK ✅",
        "git commit -m 'Feature implementada 🚀 pronta para produção 🎯'"
    ]
    
    for texto in textos_teste:
        texto_limpo = removedor.remover_emojis(texto)
        print(f"\nOriginal: {texto}")
        print(f"Limpo:    {texto_limpo}")
        
        # Verificar conformidade
        validacao = removedor.validar_conformidade_regra2(texto_limpo)
        print(f"Status:   {validacao['status']}")

def demonstrar_analise_completa():
    """Demonstra análise completa de texto"""
    removedor = RemovedorEmojis()
    
    print("\n=== ANÁLISE COMPLETA ===")
    
    texto_exemplo = """
    # Sistema de Login 🔐
    
    def login(usuario, senha):
        if validar_credenciais(usuario, senha):
            print("Login realizado com sucesso! ✅")
            return True
        else:
            print("Credenciais inválidas! ❌")
            return False
    
    # Teste da função 🧪
    resultado = login("admin", "123456")
    if resultado:
        print("Usuário logado! 🎉")
    """
    
    resultado = removedor.analisar_texto(texto_exemplo)
    
    print(f"Tamanho original: {resultado['tamanho_original']} caracteres")
    print(f"Tamanho limpo: {resultado['tamanho_limpo']} caracteres")
    print(f"Redução: {resultado['reducao_caracteres']} caracteres")
    print(f"Total de emojis: {resultado['total_emojis']}")
    print(f"Conforme Regra 2: {resultado['conforme_regra2']}")
    
    print("\nEmojis encontrados:")
    for emoji_info in resultado['emojis_encontrados']:
        print(f"  - {emoji_info['emoji']} ({emoji_info['unicode']}) - {emoji_info['nome']}")
    
    print("\nCódigo limpo (conforme Regra 2):")
    print(resultado['texto_limpo'])

def demonstrar_processamento_arquivo():
    """Demonstra processamento de arquivo com emojis"""
    removedor = RemovedorEmojis()
    
    print("\n=== PROCESSAMENTO DE ARQUIVO ===")
    
    # Criar arquivo de teste com emojis
    conteudo_teste = """
# Documentação do Projeto 📚

## Funcionalidades ⚡

- Login de usuários 👤
- Dashboard principal 📊
- Relatórios 📈
- Configurações ⚙️

## Status do Projeto 🚀

✅ Backend implementado
✅ Frontend em desenvolvimento
❌ Testes pendentes
🔄 Deploy em andamento

## Próximos Passos 📋

1. Finalizar testes 🧪
2. Fazer deploy 🚀
3. Monitorar performance 📊
4. Celebrar! 🎉
"""
    
    # Salvar arquivo de teste
    arquivo_teste = "documento_com_emojis.md"
    with open(arquivo_teste, 'w', encoding='utf-8') as f:
        f.write(conteudo_teste)
    
    print(f"Arquivo criado: {arquivo_teste}")
    
    # Processar arquivo
    resultado = removedor.processar_arquivo(arquivo_teste)
    
    print(f"\nResultado do processamento:")
    print(f"Arquivo original: {resultado['arquivo_original']}")
    print(f"Total de emojis: {resultado['total_emojis']}")
    print(f"Conforme Regra 2: {resultado['conforme_regra2']}")
    
    if 'arquivo_limpo' in resultado:
        print(f"Arquivo limpo salvo: {resultado['arquivo_limpo']}")
        
        # Mostrar diferença
        print("\nConteúdo limpo:")
        with open(resultado['arquivo_limpo'], 'r', encoding='utf-8') as f:
            print(f.read()[:200] + "...")
    
    # Limpar arquivos de teste
    if os.path.exists(arquivo_teste):
        os.remove(arquivo_teste)
    if 'arquivo_limpo' in resultado and os.path.exists(resultado['arquivo_limpo']):
        os.remove(resultado['arquivo_limpo'])
    
    print("\nArquivos de teste removidos.")

def demonstrar_validacao_conformidade():
    """Demonstra validação de conformidade com Regra 2"""
    removedor = RemovedorEmojis()
    
    print("\n=== VALIDAÇÃO DE CONFORMIDADE ===")
    
    casos_teste = [
        {
            'nome': 'Código Python limpo',
            'texto': 'def calcular_media(numeros): return sum(numeros) / len(numeros)'
        },
        {
            'nome': 'Comentário com emoji',
            'texto': '# Esta função está funcionando perfeitamente! 👍'
        },
        {
            'nome': 'Log de sistema',
            'texto': '[INFO] Sistema iniciado com sucesso'
        },
        {
            'nome': 'Mensagem de erro com emoji',
            'texto': 'ERRO: Falha na conexão com banco de dados 💥'
        },
        {
            'nome': 'Documentação técnica',
            'texto': 'A função retorna True se a operação for bem-sucedida, False caso contrário.'
        }
    ]
    
    for caso in casos_teste:
        validacao = removedor.validar_conformidade_regra2(caso['texto'])
        
        print(f"\nCaso: {caso['nome']}")
        print(f"Texto: {caso['texto'][:50]}{'...' if len(caso['texto']) > 50 else ''}")
        print(f"Status: {validacao['status']}")
        print(f"Violações: {validacao['violacoes']}")
        
        if validacao['emojis_encontrados']:
            print(f"Emojis: {', '.join(validacao['emojis_encontrados'])}")
        
        print(f"Ação: {validacao['acao_requerida']}")

def simular_pipeline_validacao():
    """Simula pipeline de validação automática"""
    removedor = RemovedorEmojis()
    
    print("\n=== SIMULAÇÃO DE PIPELINE DE VALIDAÇÃO ===")
    
    # Simular arquivos sendo processados
    arquivos_simulados = [
        {'nome': 'config.py', 'conteudo': 'DEBUG = True\nDATABASE_URL = "sqlite:///app.db"'},
        {'nome': 'utils.js', 'conteudo': 'function success() { alert("Sucesso! ✅"); }'},
        {'nome': 'README.md', 'conteudo': '# Projeto\n\nEste projeto é incrível! 🚀'},
        {'nome': 'test.py', 'conteudo': 'def test_login(): assert login("user", "pass") == True'}
    ]
    
    print("Processando arquivos no pipeline...\n")
    
    aprovados = 0
    rejeitados = 0
    
    for arquivo in arquivos_simulados:
        validacao = removedor.validar_conformidade_regra2(arquivo['conteudo'])
        
        if validacao['conforme']:
            print(f"✅ {arquivo['nome']}: APROVADO")
            aprovados += 1
        else:
            print(f"❌ {arquivo['nome']}: REJEITADO - {validacao['violacoes']} emoji(s)")
            print(f"   Emojis: {', '.join(validacao['emojis_encontrados'])}")
            
            # Mostrar versão corrigida
            texto_corrigido = removedor.remover_emojis(arquivo['conteudo'])
            print(f"   Corrigido: {texto_corrigido[:50]}{'...' if len(texto_corrigido) > 50 else ''}")
            rejeitados += 1
    
    print(f"\nResumo do Pipeline:")
    print(f"Aprovados: {aprovados}")
    print(f"Rejeitados: {rejeitados}")
    print(f"Taxa de conformidade: {(aprovados/(aprovados+rejeitados)*100):.1f}%")

if __name__ == "__main__":
    print("REMOVEDOR DE EMOJIS - ELIS v2")
    print("Ferramenta para aplicação da Regra 2: Proibição Absoluta de Emojis")
    print("=" * 70)
    
    demonstrar_deteccao_emojis()
    demonstrar_remocao_emojis()
    demonstrar_analise_completa()
    demonstrar_processamento_arquivo()
    demonstrar_validacao_conformidade()
    simular_pipeline_validacao()
    
    print("\n" + "=" * 70)
    print("Demonstração concluída!")
    print("A ferramenta está pronta para aplicar a Regra 2 em todo o sistema.")