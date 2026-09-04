@echo off
setlocal

rem ===================================================================
rem  Narrative Lens - double-click this file to start the app.
rem
rem  It brings the local database up to date, starts the server, and
rem  opens your browser. Close the small "Narrative Lens server" window
rem  to stop the app.
rem
rem  On a computer where the app has not been set up yet, this file
rem  offers to do the setup for you rather than sending you off to find
rem  another file. Constraint 7: the operator is not the one who should
rem  have to know the difference.
rem ===================================================================

cd /d "%~dp0"

set "NL_PORT=8756"
set "NL_HOST=127.0.0.1"
rem The page you land on is the app itself. The health address next to it is
rem only how this file knows the server has finished starting.
set "NL_URL=http://%NL_HOST%:%NL_PORT%/"
set "NL_HEALTH=http://%NL_HOST%:%NL_PORT%/api/health"

call :find_python
call :check_ready
if not errorlevel 1 goto ready

rem --- Not set up yet: offer to do it now -------------------------------
echo.
echo   Narrative Lens has not been set up on this computer yet.
echo.
echo   Setting up installs the software the app needs and builds its
echo   pages. It takes a few minutes and needs the internet. You only
echo   ever do this once on this computer.
echo.
choice /c YN /n /m "   Set it up now? Press Y for yes, or N to stop: "
if errorlevel 2 goto declined

echo.
echo   Starting the setup. This window will keep you posted.
echo.
call "Set up Narrative Lens.bat" from-launcher

rem The setup may have just created the .venv, so look for it again
rem before deciding whether it worked.
call :find_python
call :check_ready
if not errorlevel 1 goto ready
goto setup_failed

:declined
echo.
echo   Narrative Lens cannot start until it has been set up.
echo.
echo   When you are ready, double-click this file again and press Y.
echo.
pause
exit /b 1

:setup_failed
echo.
echo   Narrative Lens still cannot start.
echo.
echo   What went wrong: the setup did not finish, so the software the
echo   app needs is still missing.
echo   What to do: scroll up to the first message that says what went
echo   wrong, and send it to whoever set this up.
echo.
pause
exit /b 1

rem --- Bring the database up to date ------------------------------------
:ready
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

rem Wait for the server to answer before opening the browser, rather than
rem guessing at a number of seconds. Fifteen tries of one second is the
rem ceiling acceptance criterion 1 sets for starting up.
set "NL_READY="
for /l %%s in (1,1,15) do (
  if not defined NL_READY (
    curl --silent --fail --max-time 1 "%NL_HEALTH%" >nul 2>&1
    if not errorlevel 1 set "NL_READY=yes"
    if not defined NL_READY timeout /t 1 /nobreak >nul
  )
)

if not defined NL_READY (
  echo.
  echo   Narrative Lens is taking longer than usual to start.
  echo   Opening it anyway - if the page does not load, wait a moment
  echo   and refresh it.
  echo.
)

start "" "%NL_URL%"

endlocal
exit /b 0

rem ===================================================================
rem  Helpers
rem ===================================================================

rem Prefer the project's own Python if one has been set up; otherwise use
rem the Python that was installed on this computer.
:find_python
set "PYTHON=python"
if exist ".venv\Scripts\python.exe" set "PYTHON=.venv\Scripts\python.exe"
exit /b 0

rem Everything the app needs in order to run: its software, and its pages.
rem Returns 0 when the app can start and 1 when it cannot.
:check_ready
"%PYTHON%" -c "import fastapi, sqlalchemy, alembic, uvicorn" >nul 2>&1
if errorlevel 1 exit /b 1
if not exist "frontend\dist\index.html" exit /b 1
exit /b 0
