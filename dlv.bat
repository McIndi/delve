@echo off
setlocal

SET DELVE_HOME=%~dp0

cd /d %DELVE_HOME%
call set-env.bat

%DELVE_HOME%\python\%PYTHON_VERSION%\python manage.py %*
endlocal
