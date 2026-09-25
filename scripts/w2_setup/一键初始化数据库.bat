@echo off
rem W2 MySQL one-click init. Double-click to run.
rem Password: typed at prompt, or set MYSQL_PASSWORD env var beforehand.
set VENV_PY=D:\projects\OpenManus\.venv\Scripts\python.exe
if not exist "%VENV_PY%" set VENV_PY=python

"%VENV_PY%" "%~dp0one_click_init.py"
pause
