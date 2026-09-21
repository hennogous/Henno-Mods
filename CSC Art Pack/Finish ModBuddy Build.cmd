@echo off
setlocal
set "BUILT_MOD=%USERPROFILE%\Documents\My Games\Sid Meier's Civilization VI\Mods\CSC Art Pack"
if not "%~1"=="" set "BUILT_MOD=%~1"

echo Finishing the CSC Art Pack build in:
echo %BUILT_MOD%
echo.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Finish ModBuddy Build.ps1" -BuiltModPath "%BUILT_MOD%"
if errorlevel 1 (
    echo.
    echo The fix did not run. Check the message above, then rebuild in ModBuddy if needed.
    pause
    exit /b 1
)
echo.
echo Done. Press any key to close this window.
pause >nul
