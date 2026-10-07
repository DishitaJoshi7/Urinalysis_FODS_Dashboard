@echo off
rem Launch from the project folder, even when double-clicked from Explorer.
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" goto install
rem Prefer Python 3.12; a clear error is shown if the Python launcher is missing.
py -3.12 -m venv .venv
if errorlevel 1 goto failed
:install
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto failed
".venv\Scripts\python.exe" -m streamlit run app.py
goto end
:failed
echo Setup failed. Install Python 3.12 and follow README.md for manual setup.
pause
:end
