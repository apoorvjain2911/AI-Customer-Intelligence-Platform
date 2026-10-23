# AI Customer Intelligence Platform

A full-stack CRM and customer analytics platform that predicts customer churn with machine learning, explains each prediction with SHAP, and turns the results into customer segments, lifetime-value analysis and retention recommendations.

**Live demo:** [churn-prediction-roan.vercel.app](https://churn-prediction-roan.vercel.app) (frontend on Vercel, API on Render)
**Stack:** React · FastAPI · Scikit-learn · SHAP · SQLAlchemy

> The project began as a churn prediction dashboard and grew into a complete CRM with authentication, role-based access, analytics and an admin panel.

---

## Features

| Area | What it does |
|---|---|
| **Authentication & security** | JWT authentication, registration and login, bcrypt password hashing, protected routes, role-based access control (Admin and Sales Manager) |
| **Customer management** | Create, update, delete, search, filter and sort customers; customer detail view |
| **Churn prediction** | Random Forest model with a churn probability, Low / Medium / High risk classification, batch prediction and prediction history |
| **Explainable AI (SHAP)** | Global feature importance, per-customer explanations, churn drivers and retention recommendations |
| **Customer lifetime value** | CLV calculation, top valuable customers, customer value analysis |
| **Segmentation** | Create segments, assign customers, view segment statistics |
| **Reports** | Create, view, update and delete reports |
| **Admin panel** | User management, role changes, activate/deactivate users, model status, model retraining |
| **Analytics dashboard** | Customer overview, churn statistics, risk distribution, feature importance, prediction analytics |

## Tech Stack

| Layer | Technologies |
|---|---|
| Frontend | React 19, Vite, Tailwind CSS, Axios |
| Backend | Python, FastAPI, SQLAlchemy, Passlib (bcrypt), JWT |
| ML / data | Scikit-learn, SHAP, Pandas, NumPy, Joblib |
| Database | SQLite for development; PostgreSQL-compatible through SQLAlchemy |
| Deployment | Vercel (frontend), Render (backend) |

## Architecture

```
React (Vite)  ──HTTPS/JSON──►  FastAPI  ──►  Services  ──►  SQLAlchemy ──► Database
                                  │              │
                               Schemas        ML model (Joblib)
                             (validation)     + SHAP explainer
```

Requests are validated by Pydantic schemas, handled by routers in `api/`, passed to business logic in `services/`, and persisted through SQLAlchemy models. The trained model is stored with Joblib and loaded by the prediction and explainability services.

## Project Structure

```
backend/
├── api/          # route handlers
├── services/     # business logic, ML and SHAP
├── models/       # SQLAlchemy models
├── schemas/      # Pydantic request/response schemas
├── database/     # engine and session setup
├── core/         # config, security, JWT
└── main.py

frontend/
├── components/
├── pages/
├── context/
├── services/     # Axios API clients
└── App.jsx
```

## Getting Started

### Prerequisites
Python 3.10+ and Node.js 18+.

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

The API runs at `http://localhost:8000`, with interactive documentation at `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The app runs at `http://localhost:5173`.

### Environment variables

**Backend** (`backend/.env`)

```
DATABASE_URL=sqlite:///./app.db
FRONTEND_URL=http://localhost:5173
CORS_ORIGINS=http://localhost:5173
SECRET_KEY=change-me          # used to sign JWTs
```

**Frontend** (`frontend/.env`)

```
VITE_API_BASE_URL=http://localhost:8000
```

> TODO: confirm the JWT variable names (`SECRET_KEY`, algorithm, token expiry) match `core/` in your code, and add any others the backend reads.

## API Overview

Full interactive documentation is available at `/docs` (Swagger UI).

| Module | Endpoints |
|---|---|
| Authentication | `POST /auth/register`, `POST /auth/login`, `GET /auth/me` |
| Customers | `GET /customers`, `POST /customers`, `PUT /customers/{id}`, `DELETE /customers/{id}` |
| Dashboard | `GET /dashboard/summary` |
| Prediction | `POST /predict`, `POST /predict/batch` |
| Upload | `POST /upload` |
| Training | `POST /train` |
| Explainability | `GET /xai/customers/{id}` |
| Customer lifetime value | `GET /clv/summary`, `GET /clv/top`, `POST /clv/refresh/{id}` |
| Reports | CRUD endpoints |
| Segments | CRUD endpoints and customer assignment |
| Admin | Dashboard, user management, role management, status management, model retraining |

> TODO: replace the "CRUD endpoints" rows with the exact routes from `/docs` so the endpoint count in this README matches your resume's "35+ REST APIs".

## Machine Learning

- **Model:** Random Forest classifier trained on customer attributes, served through `POST /predict`.
- **Risk levels:** probability thresholds map each customer to Low, Medium or High risk.
- **Explainability:** SHAP values give both global feature importance and a per-customer breakdown of what pushed the prediction up or down.
- **Retraining:** admins can retrain the model through `POST /train`.

> TODO: add your real test-set results here, for example accuracy, precision, recall, F1 and ROC-AUC, along with the dataset name, its size and how it was split. Real figures are more convincing than any claim.

## Testing

> TODO: describe how to run your tests (for example `pytest`) and what they cover, or add a few tests for authentication, validation and prediction endpoints.

## Deployment

- **Frontend:** Vercel, with `VITE_API_BASE_URL` pointing at the deployed API.
- **Backend:** Render, with the environment variables above.
- **Note:** SQLite files are lost when a Render instance restarts. For persistent data, use a hosted PostgreSQL database and set `DATABASE_URL` accordingly.

## Current Limitations

- Development database is SQLite; PostgreSQL has not been used in production yet.
- No Docker or CI/CD setup yet.
- Model versioning is not implemented.

## Roadmap

- LLM-based AI copilot for customer insights
- PDF report generation
- Email automation and real-time notifications
- Customer activity timeline
- Docker support and a CI/CD pipeline
- PostgreSQL in production
- Model versioning
- Multi-tenant support

## Screenshots

> TODO: add images to a `docs/screenshots/` folder and link them here: dashboard, customer management, SHAP explanation, admin panel, reports, segments, login.

```markdown
![Dashboard](docs/screenshots/dashboard.png)
```

## Author

**Apoorv Jain**, B.Tech Mechanical Engineering, MANIT Bhopal
AI · Machine Learning · Full-Stack Development
[GitHub](https://github.com/apoorvjain2911) · [LinkedIn](https://linkedin.com/in/apoorv-jain)
