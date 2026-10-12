@echo off
rem W4: launch the Streamlit UI (dev server on http://localhost:8501)
set PY=D:\projects\OpenManus\.venv\Scripts\python.exe
if not exist "%PY%" (
  echo [ERROR] venv python not found: %PY%
  pause
  exit /b 1
)
"%PY%" -m streamlit run "D:\projects\ecommerce-data-agent\app\web\streamlit_app.py"
