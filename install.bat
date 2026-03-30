@echo off
setlocal enabledelayedexpansion
title jshortcuts — Windows Installer

echo.
echo ========================================================
echo   jshortcuts -- Windows Installer
echo ========================================================
echo.

:: Check for Python
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python was not found on your system!
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check the box "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

:: Define Paths
set INSTALL_DIR=%LOCALAPPDATA%\jshortcuts
set DESKTOP_SHORTCUT=%USERPROFILE%\Desktop\jshortcuts.lnk

echo [1/4] Preparing installation directory...
if not exist "%INSTALL_DIR%" (
    mkdir "%INSTALL_DIR%"
)

echo [2/4] Copying core files...
copy /Y "jshortcuts" "%INSTALL_DIR%\jshortcuts.py" >nul
copy /Y "jshortcuts-gui.py" "%INSTALL_DIR%\jshortcuts-gui.py" >nul
if exist "jshortcuts_default.json" (
    copy /Y "jshortcuts_default.json" "%INSTALL_DIR%\jshortcuts_default.json" >nul
)

echo [3/4] Creating CLI wrappers...
(
    echo @echo off
    echo python "%INSTALL_DIR%\jshortcuts.py" %%*
) > "%INSTALL_DIR%\jshortcuts.bat"

:: Add to user PATH if not already present
echo [4/4] Configuring system path...
set "FOUND_IN_PATH=0"
for %%I in ("%INSTALL_DIR%") do echo %PATH% | find /i "%%~I" >nul && set "FOUND_IN_PATH=1"

if "%FOUND_IN_PATH%"=="0" (
    setx PATH "%PATH%;%INSTALL_DIR%" >nul 2>&1
    if !ERRORLEVEL! neq 0 (
        echo [WARNING] Could not automatically add jshortcuts to your PATH.
        echo Please manually add: "%INSTALL_DIR%" to your environment variables.
    ) else (
        echo   - Added %INSTALL_DIR% to your terminal PATH!
    )
) else (
    echo   - Path already configured.
)

:: Create Desktop Shortcut using a temporary VBS script
echo.
echo Creating GUI Desktop Shortcut...
set VBS_SCRIPT="%TEMP%\create_shortcut.vbs"
(
    echo Set oWS = WScript.CreateObject^("WScript.Shell"^)
    echo sLinkFile = "%DESKTOP_SHORTCUT%"
    echo Set oLink = oWS.CreateShortcut^(sLinkFile^)
    echo oLink.TargetPath = "python"
    echo oLink.Arguments = """%INSTALL_DIR%\jshortcuts-gui.py"""
    echo oLink.WindowStyle = 1
    echo oLink.Save
) > %VBS_SCRIPT%
cscript //nologo %VBS_SCRIPT%
del %VBS_SCRIPT%

echo.
echo ========================================================
echo   jshortcuts successfully installed on Windows!
echo ========================================================
echo.
echo What's Next?
echo  1. Restart your Command Prompt or PowerShell.
echo  2. Type "jshortcuts" everywhere to manage your hotkeys.
echo  3. Double-click the "jshortcuts" icon on your Desktop to open the App.
echo.
pause
