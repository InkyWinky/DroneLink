@echo off
rem start cmd.exe /c "cd <Paste complete path to Mission Management folder> && npm run serve"
start cmd.exe /c "cd C:\Users\winky\Documents\MUAS\Mission-Management && npm run serve"
rem start cmd.exe /c "python <Paste complete path to the DronelinkServer.py file>"
start cmd.exe /c "python C:\Users\winky\Documents\MUAS\Mission-Management\Backend\DronelinkServer.py"

set ip_address_string="IPv4 Address"
rem Edit "Chrome" below to your browser if you do not have Chrome

for /f "usebackq tokens=2 delims=:" %%f in (`ipconfig ^| findstr /c:%ip_address_string%`) do start chrome %%f:8080