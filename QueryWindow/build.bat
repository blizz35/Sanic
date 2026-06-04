@echo off
set /p "name=Enter version: "

py -m PyInstaller -w --onedir --collect-all mssql_python --add-data ddbc_bindings.cp314-amd64.pyd:mssql_python --add-data *.py:. --add-data *.ico:. --onefile --splash hahayes.png --icon=vincueblack.ico --name "Sanic %name%" QueryWindow.py 