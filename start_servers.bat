@echo off
REM Start both Backend and Frontend servers
REM Windows PowerShell Script

echo.
echo ================================================================
echo   Starting AI-Based Drone Surveillance System
echo ================================================================
echo.

echo Starting Backend Server (Flask)...
start "Drone Surveillance - Backend" cmd /k "cd backend && python app.py"
timeout /t 3 /nobreak >nul

echo Starting Frontend Server (React)...
start "Drone Surveillance - Frontend" cmd /k "cd drone-surveillance-frontend && npm run dev"

echo.
echo ================================================================
echo   System Started!
echo ================================================================
echo.
echo Backend:  http://localhost:5000
echo Frontend: http://localhost:3000
echo.
echo Press any key to stop all servers...
pause >nul

echo.
echo Stopping servers...
taskkill /FI "WindowTitle eq Drone Surveillance - Backend*" /T /F >nul 2>&1
taskkill /FI "WindowTitle eq Drone Surveillance - Frontend*" /T /F >nul 2>&1

echo All servers stopped.
pause
