# Core-Backend

FastAPI backend service for healthcare data management system, integrating with Supabase for data storage and authentication.

## Project Overview

This backend system manages hospital staff (doctors, nurses), patients, medical records, and accident records through a RESTful API.

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Supabase account with project URL and API key

## Project Structure

```
Core-Backend/
│
├── app/                      # Main application package
│   ├── main.py               # FastAPI app entrypoint
│   ├── db.py                 # Supabase connection setup
│   ├── models/               # Pydantic models
│   │   ├── user.py
│   │   ├── patient.py
│   │   ├── hospital.py
│   │   ├── hospital_staff.py
│   │   ├── medical.py
│   │   └── accident.py
│   ├── routes/               # API endpoints
│   │   ├── auth_routes.py    # Login, register, token endpoints
│   │   ├── hospital_routes.py
│   │   ├── nurse_routes.py
│   │   ├── doctor_routes.py
│   │   ├── patient_routes.py
│   │   ├── accident_routes.py
│   │   └── medical_routes.py
│   ├── services/             # Business logic
│   │   ├── auth_service.py
│   │   ├── hospital_service.py
│   │   ├── hospital_staff_service.py
│   │   ├── nurse_service.py
│   │   ├── doctor_service.py
│   │   ├── patient_service.py
│   │   ├── accident_service.py
│   │   └── medical_service.py
│   ├── auth/                 # Authentication dependencies
│   │   ├── dependencies.py
│   │   └── hospital_dependency.py
│   └── utils/                # Utility functions
│       ├── auth.py
│       └── serializers.py
├── requirements.txt          # Project dependencies
├── README.md
├── venv                      # Virtual environment
├── .gitignore
└── .env                      # Environment variables (not tracked in git)

```

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/DSE-project-Group-24/Core-Backend.git
cd Core-Backend
```

### 2. Create and Activate Virtual Environment

#### Windows

```powershell
# Create virtual environment
python -m venv venv
```

```powershell

# Activate virtual environment
.\venv\Scripts\activate
```

#### macOS/Linux

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory with the following variables:

```
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_api_key

# JWT Settings
SECRET_KEY=your_jwt_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 5. Run the Application

```bash
# Start the FastAPI server
uvicorn app.main:app --reload
```

The API will be available at http://127.0.0.1:8000

### 6. Access API Documentation

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## API Endpoints

The API provides the following endpoints:

- `/auth` - User authentication and registration
- `/hospital` - Hospital management
- `/nurse` - Nurse management
- `/doctor` - Doctor management
- `/patients` - Patient management
- `/accidents` - Accident records management
- `/medical` - Medical records management

## Development

### Running Tests

```bash
# Run tests (if test suite is available)
pytest
```

### Linting and Formatting

```bash
# Install development dependencies
pip install flake8 black

# Run linting
flake8 app

# Run formatting
black app
```

## Troubleshooting

### Common Issues

#### Environment Activation Problems

If you have issues activating the virtual environment:

**Windows**:

- Make sure you're using the correct PowerShell permissions: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- Try running as administrator

**All Platforms**:

- If the virtual environment doesn't activate, try creating it again with `python -m venv venv --clear`

#### Database Connection Issues

- Check that your Supabase URL and key are correctly set in the `.env` file
- Make sure your Supabase project is active and the database is online
- Verify that your IP address is allowed in Supabase's security settings

#### Module Import Errors

If you encounter module import errors, make sure:

- You've installed all dependencies with `pip install -r requirements.txt`
- You're running the application from the project root directory

## License

[Include your license information here]

## Contributors

```


| Method | Endpoint                  | Role(s) Allowed      | Description                               |
| ------ | ------------------------- | -------------------- | ----------------------------------------- |
| POST   | `/auth/register`          | Admin                | Create doctor/nurse accounts for hospital |
| POST   | `/auth/login`             | All                  | Login, returns JWT token                  |
| POST   | `/auth/refresh`           | All                  | Refresh JWT token                         |
| GET    | `/auth/me`                | All                  | Get current user profile                  |
| GET    | `/nurse/patients`         | Nurse                | List patients in nurse's hospital         |
| POST   | `/nurse/patients/pending` | Nurse                | Add minimal patient data                  |
| PATCH  | `/nurse/patients/{id}`    | Nurse                | Update patient details                    |
| GET    | `/patients/{id}`          | Nurse, Admin, Doctor | View patient details                      |
| GET    | `/admin/users`            | Admin                | List hospital users                       |
| POST   | `/admin/users`            | Admin                | Create user (doctor/nurse)                |
| PATCH  | `/admin/users/{id}`       | Admin                | Update user info                          |
| DELETE | `/admin/users/{id}`       | Admin                | Delete user                               |



```
