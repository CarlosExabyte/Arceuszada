@echo off
chcp 65001 >nul
title Pokémon Legends: Arceus - Compilador Nativo ZA Recomp
echo ========================================================
echo   POKÉMON LEGENDS: ARCEUS - RECOMPILAÇÃO NATIVA
echo   Ambiente ZA Recomp Multi-Game
echo ========================================================
echo.

cd /d "%~dp0"

echo [1/3] Verificando arquivos do jogo em extracted/...
python tools\verify_arceus.py --prepare
if %errorlevel% neq 0 (
    echo.
    echo [ERRO] Falha na verificação dos arquivos do jogo.
    echo Certifique-se de que os arquivos do jogo estão em:
    echo   - extracted\exefs\ (main, sdk, subsdk0, subsdk1, rtld, main.npdm)
    echo   - extracted\romfs\ (bin, system_resource)
    pause
    exit /b %errorlevel%
)

echo.
echo [2/3] Iniciando processo de recompilação estática...
echo Escolha o modo de recompilação:
echo [1] Recompilação Completa (recomendado, compila todos os 4 módulos: main, subsdk0, subsdk1, sdk)
echo [2] Teste Rápido de Verificação (compila amostra de 50 rotinas)
set /p MODO="Selecione [1 ou 2]: "

if "%MODO%"=="2" (
    echo Iniciando Teste Rápido...
    python tools\build_pla.py --test --limit 50
) else (
    echo Iniciando Recompilação Completa...
    python tools\build_pla.py
)

if %errorlevel% neq 0 (
    echo.
    echo [ERRO] Falha durante a recompilação.
    pause
    exit /b %errorlevel%
)

echo.
echo ========================================================
echo   RECOMPILAÇÃO CONCLUÍDA COM SUCESSO!
echo   Execute 'executar_arceus.bat' ou 'lasrecomp.exe'
echo ========================================================
pause
