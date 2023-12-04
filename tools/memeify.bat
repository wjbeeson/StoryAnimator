@echo off

call %APOLLO%\venv\scripts\activate.bat
python %APOLLO%\src\cmd_memeify.py %1

if %ERRORLEVEL% neq 0 (
  pause
)


