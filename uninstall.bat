@echo off
setlocal enabledelayedexpansion
title jshortcuts — Windows Uninstaller

echo ========================================================
echo   jshortcuts -- Uninstaller (Windows)
echo ========================================================
echo.

set INSTALL_DIR=%LOCALAPPDATA%\jshortcuts
set DESKTOP_SHORTCUT=%USERPROFILE%\Desktop\jshortcuts.lnk
set DATA_FILE=%USERPROFILE%\.jshortcuts.json
set SYNC_DIR=%USERPROFILE%\.jshortcuts-sync

echo [1/3] Removing core installation directory...
if exist "%INSTALL_DIR%" (
    rmdir /S /Q "%INSTALL_DIR%"
    echo   - Deleted %INSTALL_DIR%
) else (
    echo   - Installation directory not found.
)

echo.
echo [2/3] Removing Desktop Shortcut...
if exist "%DESKTOP_SHORTCUT%" (
    del /Q "%DESKTOP_SHORTCUT%"
    echo   - Removed %DESKTOP_SHORTCUT%
) else (
    echo   - Desktop shortcut not found.
)

echo.
echo [3/3] Managing local Sync and Data...
if exist "%SYNC_DIR%" (
    echo   [WARNING] Found a GitHub Sync Repository at: %SYNC_DIR%
    set /p "DEL_SYNC=Delete your local GitHub sync clone completely? (y/N): "
    if /i "!DEL_SYNC!"=="y" (
        rmdir /S /Q "%SYNC_DIR%"
        echo   - Deleted %SYNC_DIR%
    ) else (
        echo   - Kept %SYNC_DIR%
    )
) else (
    echo   - Sync repository not found.
)

echo.
if exist "%DATA_FILE%" (
    echo   [INFO] Found local shortcuts data file at: %DATA_FILE%
    set /p "DEL_DATA=Delete your local shortcuts data file too? (y/N): "
    if /i "!DEL_DATA!"=="y" (
        del /Q "%DATA_FILE%"
        echo   - Deleted %DATA_FILE%
    ) else (
        echo   - Kept %DATA_FILE% (backup preserved)
    )
) else (
    echo   - Shortcuts data file not found.
)

echo.
set MY_DIR=%~dp0
if exist "%MY_DIR%jshortcuts" if exist "%MY_DIR%install.bat" (
    echo [INFO] Found the downloaded repository installer folder:
    echo        %MY_DIR%
    set /p "DEL_REPO=Delete this entire installation folder to finish cleanup? (y/N): "
    if /i "!DEL_REPO!"=="y" (
        echo   - Will delete installer folder upon exit.
        (
            echo @echo off
            echo timeout /t 2 /nobreak ^>nul
            echo rmdir /s /q "%MY_DIR%"
            echo del "%%~f0"
        ) > "%TEMP%\delete_jshortcuts_installer.bat"
        start /b "" "%TEMP%\delete_jshortcuts_installer.bat"
    )
)

echo.
echo ========================================================
echo   jshortcuts has been completely uninstalled.
echo ========================================================
echo.
echo NOTE: Since the Windows PATH variable cannot be easily manipulated
echo to strictly remove one entry without corrupting environments, 
echo please manually remove "%INSTALL_DIR%" from your PATH
echo by searching "Environment Variables" in your Windows Start Menu.
echo.
pause
