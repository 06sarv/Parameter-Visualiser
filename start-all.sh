#!/bin/bash

# Start Django backend
echo "Starting Django Backend..."
cd backend
source venv/bin/activate
python manage.py runserver &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start React frontend
echo "Starting React Frontend..."
cd ../web-frontend
npm start &
FRONTEND_PID=$!

echo "
Application started!

Backend: http://localhost:8000
Frontend: http://localhost:3000

Press Ctrl+C to stop all services
"

# Trap Ctrl+C to kill all processes
trap "echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT

# Wait for user to press Ctrl+C
wait
