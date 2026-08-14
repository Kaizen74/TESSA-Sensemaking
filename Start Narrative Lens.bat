@echo off
setlocal

rem ===================================================================
rem  Narrative Lens - double-click this file to start the app.
rem
rem  It brings the local database up to date, starts the server, and
rem  opens your browser. Close the small "Narrative Lens server" window
rem  to stop the app.
rem ===================================================================

cd /d "%~dp0"

set "NL_PORT=8756"
set "NL_HOST=127.0.0.1"
set "NL_URL=http://%NL_HOST%:%NL_PORT%/api/health"

rem Prefer the project's own Python if one has been set up; otherwise use
rem the Python that was installed on this computer.
set "PYTHON=python"
if exist ".venv\Scripts\python.exe" set "PYTHON=.venv\Scripts\python.exe"

rem --- Check Python is present and has what it needs --------------------
"%PYTHON%" -c "import fastapi, sqlalchemy, alembic, uvicorn" >nul 2>&1
if errorlevel 1 (
  echo.
  echo   Narrative Lens cannot start.
  echo.
  echo   What went wrong: the software it needs is not installed yet.
  echo   What to do: run the one-time setup you were given, then
  echo   double-click this file again.
  echo.
  pause
  exit /b 1
)

rem --- Bring the database up to date ------------------------------------
echo Preparing your data file...
"%PYTHON%" -m alembic upgrade head
if errorlevel 1 (
  echo.
  echo   Narrative Lens cannot start.
  echo.
  echo   What went wrong: the data file could not be prepared.
  echo   What to do: send the messages above to whoever set this up.
  echo.
  pause
  exit /b 1
)

rem --- Start the server, then open the browser --------------------------
echo Starting Narrative Lens...
start "Narrative Lens server" /min "%PYTHON%" -m uvicorn backend.main:app --host %NL_HOST% --port %NL_PORT%

rem Give the server a moment before the browser knocks on the door.
timeout /t 3 /nobreak >nul

start "" "%NL_URL%"

endlocal
