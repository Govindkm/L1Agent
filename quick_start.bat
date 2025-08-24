@echo off
echo Multi-Agent Email System - Quick Start
echo =====================================

echo.
echo Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo.
echo Installing dependencies...
pip install python-dotenv click rich

echo.
echo Setting up environment...
if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env"
        echo Created .env file from template
    ) else (
        echo Created basic .env file
        echo # Model Provider Configuration > .env
        echo MODEL_PROVIDER=ollama >> .env
        echo OLLAMA_BASE_URL=http://localhost:11434 >> .env
        echo OLLAMA_MODEL=llama3.2:latest >> .env
        echo # Email Configuration >> .env
        echo EMAIL_USER=your_email@gmail.com >> .env
        echo EMAIL_PASSWORD=your_app_password >> .env
        echo # Logging >> .env
        echo LOG_LEVEL=INFO >> .env
        echo LOG_FILE=agent_logs.log >> .env
    )
) else (
    echo .env file already exists
)

echo.
echo Testing system components...
python test_system.py

echo.
echo Setup complete! 
echo.
echo Next steps:
echo 1. Edit .env file with your configuration
echo 2. If using Ollama, start it: ollama serve
echo 3. Test the system: python main.py demo
echo 4. Start interactive mode: python main.py interactive
echo.

pause
