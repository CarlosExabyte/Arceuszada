@echo off
chcp 65001 >nul
title ZA Recomp - Seletor Multi-Jogo
cd /d "%~dp0"

echo ========================================================
echo   ZA RECOMP - AMBIENTE UNIFICADO MULTI-JOGO
echo ========================================================
echo   [1] Pokémon Legends: Z-A
echo   [2] Pokémon Legends: Arceus
echo   [3] Abrir Menu Principal (Launcher)
echo ========================================================
set /p OPT="Escolha uma opção [1, 2 ou 3]: "

if "%OPT%"=="1" (
    set LARECOMP_GAME=za
    echo Iniciando Pokémon Legends: Z-A...
    start "" "lasrecomp.exe" %*
) else if "%OPT%"=="2" (
    set LARECOMP_GAME=arceus
    echo Iniciando Pokémon Legends: Arceus...
    start "" "lasrecomp.exe" %*
) else (
    echo Iniciando ZA Recomp Launcher...
    start "" "lasrecomp.exe" %*
)
