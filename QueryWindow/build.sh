#!/bin/bash

read -p 'Enter version: ' versionIn

python3 -m PyInstaller -d all --onedir --collect-all mssql_python --add-data ddbc_bindings.cp314-amd64.pyd:mssql_python --add-data ddbc_bindings.cp314-universal2.so:mssql_python --add-data Window.py:. --add-data Pages.py:. --add-data Sanic.icns:. --icon=sanic.icns --name Sanic-alpha-mac-${versionIn} --clean QueryWindow.py
