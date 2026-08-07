@echo off
cd ..\docs
call conda activate vm
start mkdocs serve
timeout /t 4 /nobreak >nul
start http://127.0.0.1:8000/vonMises/
