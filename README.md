# Chemical Equipment Parameter Visualizer

🚀 **Live Demo**: [https://parameter-visualiser.vercel.app](https://parameter-visualiser.vercel.app)

## Project Overview

A hybrid application that runs both as a **Web Application** (React) and a **Desktop Application** (PyQt5), designed for data visualization and analytics of chemical equipment parameters. The application features a shared Django REST API backend that handles CSV file uploads, data analysis, and report generation.

### Key Features

- **CSV Upload**: Upload CSV files containing equipment data through both web and desktop interfaces
- **Data Analysis**: Automatic calculation of summary statistics (averages, counts, distributions)
- **Interactive Visualizations**: 
  - Web: Chart.js powered colorful charts (Bar, Line, Pie)
  - Desktop: Matplotlib charts embedded in PyQt5
- **Data Tables**: View detailed equipment information in tabular format
- **History Management**: Store and access the last 5 uploaded datasets
- **PDF Reports**: Generate comprehensive PDF reports with equipment statistics
- **Cloud Deployment**: Fully deployed with backend on Render and frontend on Vercel
- **SQLite Database**: Persistent storage for all uploaded datasets

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend (Web)** | React.js + Chart.js | Interactive web interface with visualizations |
| **Frontend (Desktop)** | PyQt5 + Matplotlib | Native desktop application with charts |
| **Backend** | Django + Django REST Framework | RESTful API for data processing |
| **Data Processing** | Pandas | CSV parsing and statistical analysis |
| **Database** | SQLite | Store uploaded datasets |
| **PDF Generation** | ReportLab | Create detailed PDF reports |
| **Deployment** | Vercel + Render | Cloud hosting for web and API |
| **Version Control** | Git & GitHub | Code management |

## Live Deployment

- **Web App**: [https://parameter-visualiser.vercel.app](https://parameter-visualiser.vercel.app)
- **Backend API**: [https://parameter-visualiser-backend.onrender.com/api](https://parameter-visualiser-backend.onrender.com/api)

## Project Structure

```
chemical-equipment-visualizer/
├── backend/                    # Django REST API
│   ├── config/                # Django project settings
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── equipment/             # Main app
│   │   ├── models.py         # Database models
│   │   ├── serializers.py    # DRF serializers
│   │   ├── views.py          # API views
│   │   ├── urls.py           # URL routing
│   │   └── admin.py          # Admin interface
│   ├── manage.py
│   └── requirements.txt
│
├── web-frontend/              # React web application
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── App.js            # Main React component
│   │   ├── App.css           # Styles
│   │   └── index.js          # Entry point
│   └── package.json
│
├── desktop-app/               # PyQt5 desktop application
│   ├── main.py               # Main application file
│   └── requirements.txt
│
├── sample_equipment_data.csv  # Sample data for testing
└── README.md                  # This file
```

## Setup Instructions

### Prerequisites

- Python 3.8+ (for backend and desktop app)
- Node.js 16+ and npm (for web frontend)
- pip (Python package manager)

### 1. Backend Setup (Django)

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations to create database
python manage.py makemigrations
python manage.py migrate

# Create superuser for admin access (optional)
python manage.py createsuperuser

# Run the development server
python manage.py runserver
```

The backend API will be available at: `http://localhost:8000`

**API Endpoints:**
- `GET /api/health/` - Health check
- `POST /api/datasets/upload_csv/` - Upload CSV file
- `GET /api/datasets/` - List all datasets
- `GET /api/datasets/{id}/` - Get specific dataset with details
- `GET /api/datasets/{id}/summary/` - Get dataset summary
- `GET /api/datasets/{id}/generate_pdf/` - Download PDF report
- `GET /api/history/` - Get last 5 datasets summary

### 2. Web Frontend Setup (React)

```bash
# Navigate to web frontend directory
cd web-frontend

# Install dependencies
npm install

# Start development server
npm start
```

The web application will open automatically at: `http://localhost:3000`

### 3. Desktop App Setup (PyQt5)

```bash
# Navigate to desktop app directory
cd desktop-app

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the desktop application
python main.py
```

**Note:** Make sure the Django backend is running before starting the desktop app.

## Sample Data

A sample CSV file (`sample_equipment_data.csv`) is provided in the root directory for testing. The CSV should have the following structure:

```csv
Equipment Name,Type,Flowrate,Pressure,Temperature
Reactor-A1,Reactor,150.5,25.3,350.2
Heat Exchanger-B2,Heat Exchanger,200.0,15.8,280.5
...
```

**Required Columns:**
- Equipment Name (string)
- Type (string)
- Flowrate (float)
- Pressure (float)
- Temperature (float)

## Usage Guide

### Web Application

1. **Upload CSV File**
   - Click "Choose File" to select a CSV file
   - Click "Upload & Analyze" to process the file
   - View automatic analysis and visualizations

2. **View Data**
   - Summary statistics displayed at the top
   - Interactive charts show distributions and comparisons
   - Data table shows all equipment details

3. **Download PDF Report**
   - Click "Download PDF Report" button
   - PDF includes statistics, charts, and equipment details

4. **View History**
   - Scroll to bottom to see recent uploads
   - Click on any history item to reload that dataset

### Desktop Application

1. **Upload CSV File**
   - Click "Choose File" button
   - Select your CSV file
   - Click "Upload & Analyze"

2. **Navigate Tabs**
   - **Summary & Statistics**: View key metrics and equipment types
   - **Visualizations**: See interactive matplotlib charts
   - **Data Table**: Browse all equipment in table format
   - **History**: Access previously uploaded datasets

3. **Generate PDF**
   - Go to Summary tab
   - Click "Download PDF Report"
   - Choose save location

## Authentication

The backend supports basic authentication. To enable it in production:

1. Edit `backend/config/settings.py`
2. Change the permission class from `AllowAny` to `IsAuthenticated` in views
3. Use Django's authentication system or create custom authentication

**Example API call with authentication:**
```python
import requests
from requests.auth import HTTPBasicAuth

response = requests.post(
    'http://localhost:8000/api/datasets/upload_csv/',
    files={'file': open('data.csv', 'rb')},
    auth=HTTPBasicAuth('username', 'password')
)
```

## Database Schema

### EquipmentDataset Model
- `id`: Primary key
- `name`: Dataset filename
- `uploaded_at`: Upload timestamp
- `uploaded_by`: Foreign key to User (optional)
- `file`: File upload field
- `total_count`: Total equipment count
- `avg_flowrate`: Average flowrate
- `avg_pressure`: Average pressure
- `avg_temperature`: Average temperature
- `equipment_types`: JSON field with type distribution

### Equipment Model
- `id`: Primary key
- `dataset`: Foreign key to EquipmentDataset
- `equipment_name`: Equipment name
- `type`: Equipment type
- `flowrate`: Flowrate value
- `pressure`: Pressure value
- `temperature`: Temperature value

## Testing

### Test Backend API
```bash
cd backend
python manage.py test
```

### Test with Sample Data
1. Use the provided `sample_equipment_data.csv`
2. Upload through either web or desktop interface
3. Verify statistics calculation
4. Check visualizations
5. Generate and download PDF report

## Building for Production

### Backend (Django)
```bash
# Update settings for production
# - Set DEBUG = False
# - Configure ALLOWED_HOSTS
# - Use PostgreSQL instead of SQLite
# - Set up proper SECRET_KEY

# Collect static files
python manage.py collectstatic

# Use a production server like Gunicorn
pip install gunicorn
gunicorn config.wsgi:application
```

### Web Frontend
```bash
cd web-frontend
npm run build
# Serve the build folder with a web server
```

### Desktop App
```bash
# Package with PyInstaller
pip install pyinstaller
pyinstaller --onefile --windowed main.py
```

## Deployment

This project is fully deployed and accessible online:

### Current Deployment
- **Frontend**: Deployed on Vercel at [https://parameter-visualiser.vercel.app](https://parameter-visualiser.vercel.app)
- **Backend**: Deployed on Render at [https://parameter-visualiser-backend.onrender.com](https://parameter-visualiser-backend.onrender.com)

### Deployment Configuration

**Backend (Render)**:
- Build Command: `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput`
- Start Command: `gunicorn config.wsgi:application`
- Auto-deploys from GitHub on push

**Frontend (Vercel)**:
- Framework: React
- Root Directory: `web-frontend`
- Environment Variable: `REACT_APP_API_URL` = `https://parameter-visualiser-backend.onrender.com/api`
- Auto-deploys from GitHub on push

### Alternative Deployment Options
- **Backend**: Railway, Fly.io, PythonAnywhere, AWS, Azure
- **Frontend**: Netlify, GitHub Pages, Cloudflare Pages
- **Desktop**: Distribute as packaged executable (.exe, .app, or binary)

## Troubleshooting

**Issue: Backend not connecting**
- Ensure Django server is running on port 8000
- Check CORS settings in `settings.py`

**Issue: CSV upload fails**
- Verify CSV has required columns
- Check file encoding (UTF-8 recommended)
- Ensure file size is reasonable

**Issue: Desktop app doesn't show charts**
- Verify matplotlib and PyQt5 are installed
- Check that backend API is accessible

**Issue: PDF generation fails**
- Ensure ReportLab is installed
- Check file permissions for media directory

## API Documentation

Detailed API documentation can be accessed at:
- Django REST Framework browsable API: `http://localhost:8000/api/`
- Admin interface: `http://localhost:8000/admin/`

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

**Built for FOSSEE Intern Screening Task**
