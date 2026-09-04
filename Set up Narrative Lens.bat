@echo off
setlocal enabledelayedexpansion

rem ===================================================================
rem  Narrative Lens - ONE-TIME SETUP. Double-click this file once, on a
rem  new computer, before the first time you start the app.
rem
rem  It installs the software Narrative Lens needs and builds its pages.
rem  It needs the internet while it runs. After it has finished, the app
rem  never needs the internet again except when you click Analyse.
rem
rem  When it is done, double-click "Start Narrative Lens.bat".
rem ===================================================================

cd /d "%~dp0"

echo.
echo   Setting up Narrative Lens. This takes a few minutes the first time.
echo   You can leave it running.
echo.

rem --- Find a Python ----------------------------------------------------
rem  "py -3" is the Windows launcher and is the reliable one. Plain "python"
rem  can be a Microsoft Store placeholder that does nothing, so it is only
rem  tried second, and it is checked by asking it its version rather than by
rem  assuming it works.
set "PYTHON="
py -3 --version >nul 2>&1
if not errorlevel 1 set "PYTHON=py -3"

if not defined PYTHON (
  python --version >nul 2>&1
  if not errorlevel 1 set "PYTHON=python"
)

if not defined PYTHON (
  echo.
  echo   Narrative Lens cannot be set up yet.
  echo.
  echo   What went wrong: Python is not installed on this computer.
  echo   What to do: install Python from python.org, tick the box that
  echo   says "Add Python to PATH" while installing, then double-click
  echo   this file again.
  echo.
  pause
  exit /b 1
)

echo   Step 1 of 4: making a private space for the app's software...
%PYTHON% -m venv ".venv"
if errorlevel 1 (
  echo.
  echo   Narrative Lens cannot be set up.
  echo.
  echo   What went wrong: the private space for the app's software could
  echo   not be made.
  echo   What to do: send the messages above to whoever set this up.
  echo.
  pause
  exit /b 1
)

set "VENV_PY=.venv\Scripts\python.exe"
if not exist "%VENV_PY%" (
  echo.
  echo   Narrative Lens cannot be set up.
  echo.
  echo   What went wrong: the private space was made but is not usable.
  echo   What to do: delete the folder called ".venv" next to this file,
  echo   then double-click this file again.
  echo.
  pause
  exit /b 1
)

echo   Step 2 of 4: installing the software the app needs...
echo   (this is the slow one - a few minutes is normal)
"%VENV_PY%" -m pip install --upgrade pip
"%VENV_PY%" -m pip install -e .
if errorlevel 1 (
  echo.
  echo   Narrative Lens cannot be set up.
  echo.
  echo   What went wrong: the software the app needs could not be
  echo   downloaded. This is almost always the internet connection.
  echo   What to do: check you are online, then double-click this file
  echo   again. If it keeps failing, send the messages above to whoever
  echo   set this up.
  echo.
  pause
  exit /b 1
)

rem --- The app's own pages ----------------------------------------------
rem  npm is a .cmd file on Windows. Calling it without "call" ends this
rem  script instead of returning to it, which would leave setup half-done
rem  and silent about it.
echo   Step 3 of 4: checking for Node...
call npm --version >nul 2>&1
if errorlevel 1 (
  echo.
  echo   Narrative Lens cannot be set up yet.
  echo.
  echo   What went wrong: Node is not installed on this computer. The
  echo   app's pages are built with it.
  echo   What to do: install Node from nodejs.org, take the version it
  echo   offers you, then double-click this file again.
  echo.
  pause
  exit /b 1
)

echo   Step 4 of 4: building the app's pages...
pushd "frontend"
call npm install
if errorlevel 1 (
  popd
  echo.
  echo   Narrative Lens cannot be set up.
  echo.
  echo   What went wrong: the pieces the app's pages are built from could
  echo   not be downloaded. This is almost always the internet connection.
  echo   What to do: check you are online, then double-click this file
  echo   again.
  echo.
  pause
  exit /b 1
)

call npm run build
if errorlevel 1 (
  popd
  echo.
  echo   Narrative Lens cannot be set up.
  echo.
  echo   What went wrong: the app's pages could not be built.
  echo   What to do: send the messages above to whoever set this up.
  echo.
  pause
  exit /b 1
)
popd

if not exist "frontend\dist\index.html" (
  echo.
  echo   Narrative Lens cannot be set up.
  echo.
  echo   What went wrong: the app's pages were built but did not appear
  echo   where the app looks for them.
  echo   What to do: send this message to whoever set this up.
  echo.
  pause
  exit /b 1
)

echo.
echo   ===============================================================
echo     Narrative Lens is ready.
echo.
echo     Now double-click "Start Narrative Lens.bat" to open the app.
echo     You only ever have to do this setup once on this computer.
echo   ===============================================================
echo.
pause

endlocal
