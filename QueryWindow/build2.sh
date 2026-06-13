#!/bin/bash

read -p 'Enter version: ' versionIn

python3 -m PyInstaller -d all --onedir --collect-all mssql_python --add-data Window.py:. --add-data Pages.py:. --icon=sanic.icns --name Sanic-alpha-mac-${versionIn} --clean QueryWindow.py
