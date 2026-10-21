@echo off
REM =======================================================================================
REM Real Time Zone (RTZ) - One-Time Hourly Weather Hook Installer
REM =======================================================================================
cd /d "%~dp0"

set "GAMMA="
if exist "..\..\ModOrganizer.ini" (
    for %%G in ("%~dp0..\..") do set "GAMMA=%%~fG"
) else if exist "ModOrganizer.ini" (
    set "GAMMA=%~dp0"
)

if not defined GAMMA (
    echo.
    echo  ** Could not find ModOrganizer.ini two levels up.
    echo     Install this zip via Mod Organizer 2 first, then right-click
    echo     "Seasons of the Zone - Real Time Zone (RTZ)" in MO2, choose
    echo     "Open in Explorer", and run setup_rtz.bat from there.
    echo.
    pause
    exit /b 1
)

set "PY=python"
where py >nul 2>&1 && set "PY=py -3"

echo.
echo  Setting up Real Time Zone (RTZ) hourly weather fetcher...
echo.
%PY% "_tools\fetch_rtz_hourly.py" --install
echo.
echo  Setup complete! Start the game with play.bat as usual.
echo.
if not "%~1"=="--nopause" pause
