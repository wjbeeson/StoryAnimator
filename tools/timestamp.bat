@echo off
cd %APOLLO%\tools
call %APOLLO%\venv\scripts\activate.bat
python %APOLLO%\src\cmd_timestamp.py %1

if %ERRORLEVEL% neq 0 (
  pause
)


