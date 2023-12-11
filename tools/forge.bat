rem @echo off
cd %APOLLO%\tools
call %APOLLO%\venv\scripts\activate.bat
rem call  "C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\Tools\vsdevcmd.bat"

python %APOLLO%\src\cmd_forge.py %1 %2

if %ERRORLEVEL% neq 0 (
  pause
)


