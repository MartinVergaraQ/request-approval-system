# Request Approval System

Sistema web para gestionar solicitudes con flujo de aprobación (Draft → Submitted → Approved/Rejected) y auditoría (historial de acciones).

## Tech Stack
- Backend: Django + DRF + SimpleJWT
- DB: PostgreSQL (Docker)
- API client: Bruno collections

## Features
- Autenticación JWT (login/refresh)
- CRUD de solicitudes (solo creador / aprobador)
- Acciones: submit / approve / reject con reglas de negocio
- Historial (audit trail) por solicitud
- Filtros: por estado (`?status=...`)
- Paginación (PageNumberPagination)

## Getting Started

### 1) Backend (Django)
cd Backend
python -m venv entorno
# activar entorno según tu OS
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

### 2) Variables de entorno (Backend/.env)
DB_NAME=request_approval
DB_USER=app
DB_PASSWORD=app
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=dev-secret-key
DEBUG=1
