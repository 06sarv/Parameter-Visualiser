#!/bin/bash

echo "Starting Chemical Equipment Visualizer Setup..."

# Backend setup
echo "Setting up Backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
echo "Backend setup complete!"

# Web frontend setup
echo "Setting up Web Frontend..."
cd ../web-frontend
npm install
echo "Web Frontend setup complete!"

# Desktop app setup
echo "Setting up Desktop App..."
cd ../desktop-app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
echo "Desktop App setup complete!"

cd ..
echo "
Setup Complete!

To start the application:

1. Backend (Terminal 1):
   cd backend
   source venv/bin/activate
   python manage.py runserver

2. Web Frontend (Terminal 2):
   cd web-frontend
   npm start

3. Desktop App (Terminal 3):
   cd desktop-app
   source venv/bin/activate
   python main.py

Happy coding!
"
