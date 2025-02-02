@echo off
cd /d C:\AI\imgSort

REM Open the image sorter page in the default browser
start "" "http://127.0.0.1:5000/"

REM Launch the tray launcher without a console window
start "" pythonw tray_launcher.py
