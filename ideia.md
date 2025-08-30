essa tag indica que ja foi executado a ideia ------------ ok
------------ ok


crie um arquivo de rules e contexto pro IA
crie um arquivo de configuração para o TRAE-IDE
inicialçmente quero apenas essas informações 
liguagem: python
------------ ok 
crie uma ferramenta EXEMPLO, que me mostre apenas isso SOU A FERRAMENTA EXEMPLO
------------ ok
quero organizar o projeto , vou darum exemplo
C:\Users\MARDUKA\Desktop\ELIS\ELIS-v2\ai_rules_context.md
C:\Users\MARDUKA\Desktop\ELIS\ELIS-v2\trae_config.json
esses arquivos são relativos ao IA, vamos criar um DIR IA/ 
eles devem estar lah
consegue usar a mesma logica para  C:\Users\MARDUKA\Desktop\ELIS\ELIS-v2\ferramenta_exemplo.py
------------ ok
esse erro esta travando tudo 
PS C:\Users\MARDUKA\Desktop\ELIS\ELIS-v2> Remove-Variable -Name '__VSCodeOriginalPrompt' -ErrorAct; function prompt { $lastSuccess = $?; "(TraeAI-6cation) [$( if ($lastSuccess -eq $true) { 0 } else { 1 } ):$LASTEXITCODE] $ " }; $env:GIT_PAGER=""; $env:PAGER=""
[0:] $ ^C
(TraeAI-6) C:\Users\MARDUKA\Desktop\ELIS\ELIS-v2 
[0:] $
[0:] $
(TraeAI-6) C:\Users\MARDUKA\Desktop\ELIS\ELIS-v2 
[0:] $ ^C
[0:] $
(TraeAI-6) C:\Users\MARDUKA\Desktop\ELIS\ELIS-v2 
[0:] $
(TraeAI-6) C:\Users\MARDUKA\Desktop\ELIS\ELIS-v2 
[0:] > if ($env:TERM_PROGRAM -eq "vscode") { $GloIntegration.ps1" } catch{} }; Write-Output "[Trae] Shell integration is not enabled, try to fix it now."
ix it now.
[0:] $ ^C
(TraeAI-6) C:\Users\MARDUKA\Desktop\ELIS\ELIS-v2 
[0:] $
(TraeAI-6) C:\Users\MARDUKA\Desktop\ELIS\ELIS-v2 
[0:] $ cd c:\Users\MARDUKA\Desktop\ELIS\ELIS-v2 ; mkdir ferramentas


    Diretório:


Mode                 LastWriteTime        Length 
----                 -------------        ------ 
d-----        30/08/2025     17:18


(TraeAI-6) C:\Users\MARDUKA\Desktop\ELIS\ELIS-v2 
[0:] $
(TraeAI-6) C:\Users\MARDUKA\Desktop\ELIS\ELIS-v2 
[0:] $
isso é o que vejo no terminal, crie uma forma de resolver isso e add essa solução nas rules, para nao acontecer novamente
------------ ok
esse é um dos problemas fundamentais que encontro no processo de desenvolvimento, a solução de terminal que vc acabou de criar , usar , ela funciona. A dor esta que nos meus proximos prompts, a resposta da IA , nao usa ela,  ela retorna comandos de terminais errados, como passar a solução para evitar isso?
------------ ok
o meu desenvolvimento com IA esta com uma produtividade extremamente baixa, consegui identificar que os meus prompts sao mal construidos e nao transferrem o contexto correto.Pensei em um forma de resolver isso, vou tentar explicar de forma humana
user: insere o prompt
assistant IA1:recebe o prompt , analiza o contexto que o projeto tem , e gera um prompt2 e envia pro assistant IA2
assistant IA1 recebe a resposta, analiza se ela esta correta aplicando as regras e conxtexto do projeto
Minha pergunta é, esse fluxo é viavel? vc pode dizer que não, eu nao sei se estou certo
--------- ok
vamos validar o IA1 e IA2
prompt de exemplo "crie um arquivo de texto, res_IA.txt, com o conteudo: feito. add na linha de baixo o comando usado para fazer o arquivo"
execute o prompt com a IA1 e com a IA2, vamos ver o comportamento

