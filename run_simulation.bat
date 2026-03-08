@echo off
echo ============================================================
echo INDIAN TRAFFIC SIMULATION - COMMAND CENTER
echo ============================================================
echo.
echo Choose your Simulation Strategy:
echo 1. Macro-Level (Mumbai City Digital Twin)
echo    - Entire city network, real-time routing, road blockades.
echo 2. Micro-Level (High-Fidelity Satellite Intersection)
echo    - Top-down asphalt textures, lane markings, detailed sprites.
echo 3. Interactive Web Map (Basic)
echo    - Live zoomable satellite tiles with real GPS coordinates.
echo 4. TraffiSim AI Digital Twin (Full Scale - SIH Edition)
echo    - Advanced Agents, Mixed Traffic, Next.js Dashboard, OSM Data.
echo.
set /p choice="Enter your choice (1, 2, 3, or 4): "

echo.
echo Launching...

if "%choice%"=="4" (
    echo Launching TraffiSim AI Platform...
    echo Starting Backend on http://localhost:8000
    start "TraffiSim Backend" cmd /c "py -3.12 -m uvicorn backend.main:app --port 8000"
    echo Starting Frontend on http://localhost:3000
    cd frontend && start "TraffiSim Frontend" cmd /c "npm run dev"
    timeout /t 5
    start http://localhost:3000
) else if "%choice%"=="3" (
    echo Starting Web Server at http://localhost:8000
    start http://localhost:8000
    py -3.12 web_server.py 2>NUL
    if %ERRORLEVEL% neq 0 (
        py -3.13 web_server.py 2>NUL
        if %ERRORLEVEL% neq 0 python web_server.py
    )
) else if "%choice%"=="2" (
    py -3.12 high_fidelity_intersection.py 2>NUL
    if %ERRORLEVEL% neq 0 (
        py -3.13 high_fidelity_intersection.py 2>NUL
        if %ERRORLEVEL% neq 0 python high_fidelity_intersection.py
    )
) else (
    py -3.12 main.py 2>NUL
    if %ERRORLEVEL% neq 0 (
        py -3.13 main.py 2>NUL
        if %ERRORLEVEL% neq 0 python main.py
    )
)

echo.
echo Simulation closed.
pause
