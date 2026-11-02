@echo off
chcp 65001 >nul
title Pokémon Legends: Arceus - ZA Recomp
cd /d "%~dp0"

if not exist "extracted\lasgame.dll" (
    echo ========================================================
    echo [AVISO] O jogo ainda não foi recompilado!
    echo Execute primeiro 'recompilar_arceus.bat' para compilar o código nativo.
    echo ========================================================
    pause
    exit /b 1
)

set LARECOMP_GAME=arceus
echo Iniciando Pokémon Legends: Arceus via ZA Recomp Runtime...
start "" "lasrecomp.exe" %*
