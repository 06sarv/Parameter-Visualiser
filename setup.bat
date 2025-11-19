@echo off
echo Starting Chemical Equipment Visualizer Setup...

REM Backend setup
echo Setting up Backend...
cd backend
python -m venv venv
call venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
echo Backend setup complete!

REM Web frontend setup
echo Setting up Web Frontend...
cd ..\web-frontend
npm install
echo Web Frontend setup complete!

REM Desktop app setup
echo Setting up Desktop App...
cd ..\desktop-app
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
echo Desktop App setup complete!

cd ..
echo.
echo Setup Complete!
echo.
echo To start the application:
echo.
echo 1. Backend (Terminal 1):
echo    cd backend
echo    venv\Scripts\activate
echo    python manage.py runserver
echo.
echo 2. Web Frontend (Terminal 2):
echo    cd web-frontend
echo    npm start
echo.
echo 3. Desktop App (Terminal 3):
echo    cd desktop-app
echo    venv\Scripts\activate
echo    python main.py
echo.
pause
