@echo off
cd %APOLLO%\tools
call %APOLLO%\venv\scripts\activate.bat
python %APOLLO%\src\cmd_tts.py %1 -p

if %ERRORLEVEL% neq 0 (
  pause
)


