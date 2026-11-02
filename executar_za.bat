@echo off
chcp 65001 >nul
title Pokémon Legends: Z-A - ZA Recomp
cd /d "%~dp0"

set LARECOMP_GAME=za
echo Iniciando Pokémon Legends: Z-A via ZA Recomp Runtime...
start "" "lasrecomp.exe" %*
