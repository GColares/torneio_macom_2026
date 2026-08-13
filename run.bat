@echo off
echo ===========================================
echo   Iniciando Servidor Django - Macom 2026
echo ===========================================

echo Ativando ambiente virtual...
call venv\Scripts\activate

echo Atualizando banco de dados com o CSV mais recente...
python manage.py import_csv

echo Abrindo o navegador...
start http://localhost:8081

echo Iniciando servidor Django (Nao feche esta janela!)...
python manage.py runserver 8081
