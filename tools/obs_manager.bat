@echo off

call %APOLLO%\venv\scripts\activate.bat
python %APOLLO%\src\raptor_obs_manager.py %1

if %ERRORLEVEL% neq 0 (
  pause
)


