@echo off
REM Script para configuração do ambiente virtual ELIS
REM Autor: Sistema ELIS
REM Data: 2025

echo ========================================
echo ELIS - Configuracao do Ambiente Virtual
echo ========================================

REM Verificar se Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Python nao encontrado no sistema!
    echo Por favor, instale o Python 3.8+ antes de continuar.
    pause
    exit /b 1
)

echo Python encontrado. Versao:
python --version

REM Criar ambiente virtual se não existir
if not exist "venv" (
    echo Criando ambiente virtual...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ERRO: Falha ao criar ambiente virtual!
        pause
        exit /b 1
    )
    echo Ambiente virtual criado com sucesso!
) else (
    echo Ambiente virtual ja existe.
)

REM Ativar ambiente virtual
echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

REM Atualizar pip
echo Atualizando pip...
python -m pip install --upgrade pip

REM Instalar dependências (se houver dependências externas no futuro)
if exist "requirements.txt" (
    echo Instalando dependencias...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo AVISO: Algumas dependencias podem nao ter sido instaladas.
    )
) else (
    echo Arquivo requirements.txt nao encontrado.
)

echo ========================================
echo Configuracao concluida!
echo Para ativar o ambiente virtual manualmente:
echo   venv\Scripts\activate.bat
echo Para desativar:
echo   deactivate
echo ========================================

REM Manter janela aberta
echo Pressione qualquer tecla para continuar...
pause >nul