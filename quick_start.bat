@echo off
REM Quick Start Script for AI-Based Drone Surveillance System
REM Windows PowerShell Script

echo.
echo ================================================================
echo   AI-Based Drone Surveillance System - Quick Start
echo   HAL Defense AI Division 2025
echo ================================================================
echo.

echo [1/3] Installing Backend Dependencies...
cd backend
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install backend dependencies
    pause
    exit /b 1
)
echo Backend dependencies installed successfully!
echo.

echo [2/3] Installing Frontend Dependencies...
cd ..\drone-surveillance-frontend
call npm install
if errorlevel 1 (
    echo ERROR: Failed to install frontend dependencies
    pause
    exit /b 1
)
echo Frontend dependencies installed successfully!
echo.

echo ================================================================
echo   Installation Complete!
echo ================================================================
echo.
echo Next Steps:
echo.
echo 1. Setup Kaggle API (for dataset download):
echo    - Go to https://www.kaggle.com/settings
echo    - Create API token
echo    - Place kaggle.json in C:\Users\%USERNAME%\.kaggle\
echo.
echo 2. Train the model:
echo    cd backend
echo    python setup_and_train.py
echo.
echo 3. OR use pre-trained model and start servers:
echo    - Backend:  cd backend ^&^& python app.py
echo    - Frontend: cd drone-surveillance-frontend ^&^& npm run dev
echo.
echo 4. Open http://localhost:3000 in your browser
echo.
echo ================================================================

pause
