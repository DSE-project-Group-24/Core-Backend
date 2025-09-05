# Core-Backend


```
core_backend/
│
├── app/
│   ├── main.py               # FastAPI app entrypoint
│   ├── config.py             # DB, JWT secrets, Supabase config
│   ├── database.py           # Supabase/Postgres connection setup
│   ├── models/               # Pydantic and ORM models
│   │   ├── user.py
│   │   ├── patient.py
│   │   └── accident.py
│   ├── routers/
│   │   ├── auth.py           # Login, register, token refresh
│   │   ├── nurse.py          # Nurse-specific endpoints
│   │   ├── patients.py       # CRUD patients (Nurse + Admin)
│   │   ├── admin.py          # Hospital admin user mgmt
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── nurse_service.py
│   │   └── patient_service.py
│   ├── utils/
│   │   ├── security.py       # JWT helpers (validate tokens etc.)
│   │   ├── role_check.py     # Role verification dependencies
│   │   └── logging.py
│   └── __init__.py
│
└── requirements.txt
└── .gitignore
└── .env
└── README.md
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



