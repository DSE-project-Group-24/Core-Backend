# Core-Backend

A concise, human-friendly FastAPI backend for managing hospital staff, patients, accident and medical records. The service integrates with Supabase for data storage and authentication and includes prediction features (CatBoost & SARIMA) and a government rules engine.

This README highlights the current functionality and explains how to run and test the project.

---

## Quick links (open these files to inspect implementation)

## Project structure

Core-Backend/
│
├── app/ # Main application package
│ ├── main.py # FastAPI app entrypoint
│ ├── db.py # Supabase connection setup
│ ├── models/ # Pydantic models
│ │ ├── user.py
│ │ ├── patient.py
│ │ ├── hospital.py
│ │ ├── hospital_staff.py
│ │ ├── medical.py
│ │ └── accident.py
│ ├── routes/ # API endpoints
│ │ ├── auth_routes.py # Login, register, token endpoints
│ │ ├── hospital_routes.py
│ │ ├── nurse_routes.py
│ │ ├── doctor_routes.py
│ │ ├── patient_routes.py
│ │ ├── accident_routes.py
│ │ └── medical_routes.py
│ ├── services/ # Business logic
│ │ ├── auth_service.py
│ │ ├── hospital_service.py
│ │ ├── hospital_staff_service.py
│ │ ├── nurse_service.py
│ │ ├── doctor_service.py
│ │ ├── patient_service.py
│ │ ├── accident_service.py
│ │ └── medical_service.py
│ ├── auth/ # Authentication dependencies
│ │ ├── dependencies.py
│ │ └── hospital_dependency.py
│ └── utils/ # Utility functions
│ ├── auth.py
│ └── serializers.py
├── requirements.txt # Project dependencies
├── README.md
├── venv # Virtual environment
├── .gitignore
└── .env # Environment variables (not tracked in git)

---

## Important features

- Discharge outcome predictions via a CatBoost classifier with endpoints and model health/info endpoints (see [`DischargeOutcomePredictor`](app/services/discharge_outcome_service.py)).
- Hospital stay length prediction endpoint using CatBoost (see [`predict_records`](app/services/hospital_stay_service.py)).
- SARIMA-based forecasting endpoints for monthly/daily forecasts (see [`get_forecast_service`](app/services/prediction_service.py)).
- Government rules engine to bootstrap and run association-rule searches on the dataset (`GovRulesEngine` in [app/services/gov_rules_service.py]).
- Transfer request workflows (create/approve/reject) and dedicated routes ([app/routes/transfer_routes.py]).
- Functional test runners to exercise groups of tests without pytest: [tests/simple_test_runner.py](tests/simple_test_runner.py) and [tests/run_functional_tests.py](tests/run_functional_tests.py).

---

## Requirements

- Python 3.10+
- pip
- Supabase project (URL and API key)
- Recommended: create and activate a venv

Install dependencies and create a virtual environment before running the project. Example commands are below.

Windows (PowerShell):

```powershell
# create a venv named .venv
python -m venv .venv

# activate the venv (PowerShell)
.\.venv\Scripts\Activate.ps1

# upgrade pip and install requirements
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Windows (cmd.exe):

```cmd
python -m venv .venv
.\.venv\Scripts\activate.bat
pip install -r requirements.txt
```

macOS / Linux (bash / zsh):

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Once dependencies are installed the app can be started (see "Run locally").

---

## Configuration

Create a `.env` file in the project root with:

```
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_api_key

# JWT settings
SECRET_KEY=your_jwt_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

If environment variables are missing, the app raises at startup (see [app/db.py](app/db.py)).

---

## Run locally

Start the server:

```bash
uvicorn app.main:app --reload
```

The API will be available at http://127.0.0.1:8000. You can also run via the included Procfile on platforms that support it: [Procfile](Procfile).

API docs:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

---

## Main endpoints (summary)

- Authentication

  - POST /auth/register
  - POST /auth/login
  - POST /auth/refresh
  - GET /auth/me

- Core resources

  - /hospital, /nurse, /doctor, /patients, /accidents, /medical

- Predictions (prefix: /predictions)

  - POST /predictions/discharge-outcome — discharge outcome (CatBoost) ([route implementation](app/routes/discharge_outcome_routes.py))
  - GET /predictions/discharge-outcome/model-info — model metadata
  - POST /predictions/hospital-stay-predict — hospital stay predictions ([route implementation](app/routes/hospital_stay_service_route.py))
  - POST /predictions/forecast — monthly SARIMA forecasts ([route implementation](app/routes/prediction_routes.py))
  - POST /predictions/daily-forecast — daily SARIMA forecast

- Government rules

  - GET /gov/rules/bootstrap
  - POST /gov/rules/run (restricted to government personnel) — see [app/routes/gov_routes.py](app/routes/gov_routes.py)

- Transfers

  - /transfers endpoints for creating and approving transfer requests ([app/routes/transfer_routes.py](app/routes/transfer_routes.py))

---

## Models and files

Put model files under the `trained_models/` directory. The discharge outcome and hospital-stay services expect CatBoost model files; SARIMA models live under `trained_models/` as well. Notable files:

- trained_models/catboost_stay_classifier_v2_with_feature_15.cbm
- trained_models/catboost_top25_model.cbm

If model files are missing, the prediction services return a clear error or an empty response and log the problem — see model-loading patterns in [app/services/hospital_stay_service.py](app/services/hospital_stay_service.py) and [app/services/discharge_outcome_service.py](app/services/discharge_outcome_service.py).

---

## Troubleshooting

- "Missing SUPABASE_URL or SUPABASE_KEY" — verify `.env` and restart. (See [app/db.py](app/db.py).)
- Prediction endpoints failing — confirm required model files exist in `trained_models/` and check server logs.
- Auth failures — ensure Supabase is reachable and user accounts exist or register via the admin endpoints.

---
