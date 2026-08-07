@echo off
setlocal enabledelayedexpansion

cd ..\docs
call conda activate vm
mkdocs build
timeout /t 4 /nobreak >nul
mkdocs gh-deploy --clean
timeout /t 4 /nobreak >nul
start https://saudzahirr.github.io/vonMises/

endlocal
