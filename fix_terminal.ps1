# Script de Correção do Terminal PowerShell - ELIS v2
# Este script resolve problemas comuns de integração do terminal no Trae IDE

Write-Host "[ELIS] Iniciando correção do terminal PowerShell..." -ForegroundColor Green

# 1. Limpar variáveis problemáticas
try {
    Remove-Variable -Name '__VSCodeOriginalPrompt' -ErrorAction SilentlyContinue
    Write-Host "[OK] Variável __VSCodeOriginalPrompt removida" -ForegroundColor Yellow
} catch {
    Write-Host "[INFO] Variável __VSCodeOriginalPrompt não encontrada" -ForegroundColor Gray
}

# 2. Resetar função prompt para padrão simples
function prompt {
    $currentPath = Get-Location
    "PS $currentPath> "
}

# 3. Configurar variáveis de ambiente
$env:GIT_PAGER = ""
$env:PAGER = ""
$env:TERM_PROGRAM = "trae-ide"

# 4. Limpar histórico de comandos problemáticos
Clear-History

# 5. Verificar e corrigir integração do shell
if ($env:TERM_PROGRAM -eq "trae-ide") {
    Write-Host "[OK] Integração Trae IDE detectada" -ForegroundColor Green
} else {
    Write-Host "[AVISO] Configurando integração Trae IDE" -ForegroundColor Yellow
    $env:TERM_PROGRAM = "trae-ide"
}

# 6. Resetar título do terminal
$Host.UI.RawUI.WindowTitle = "Trae IDE - ELIS v2"

Write-Host "[ELIS] Correção do terminal concluída com sucesso!" -ForegroundColor Green
Write-Host "[INFO] Terminal pronto para uso" -ForegroundColor Cyan

# Exibir informações do ambiente
Write-Host "`n=== INFORMAÇÕES DO AMBIENTE ===" -ForegroundColor Magenta
Write-Host "Diretório atual: $(Get-Location)" -ForegroundColor White
Write-Host "Versão PowerShell: $($PSVersionTable.PSVersion)" -ForegroundColor White
Write-Host "Terminal: $($env:TERM_PROGRAM)" -ForegroundColor White
Write-Host "================================`n" -ForegroundColor Magenta