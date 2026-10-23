# AI Customer Intelligence Platform

A full-stack CRM and customer analytics platform that predicts customer churn with machine learning, explains each prediction with SHAP, and turns the results into customer segments, lifetime-value analysis and retention recommendations.

| | |
|---|---|
| **Frontend (live)** | https://churn-prediction-roan.vercel.app |
| **Backend API (live)** | https://churn-prediction-0v3d.onrender.com |
| **API docs (live)** | https://churn-prediction-0v3d.onrender.com/docs |
| **Stack** | React · FastAPI · Scikit-learn · SHAP · SQLAlchemy |

> The project began as a churn prediction dashboard and grew into a complete CRM with authentication, role-based access, analytics and an admin panel.

## Contents

1. [Features](#features)
2. [Tech stack](#tech-stack)
3. [Try the live app](#try-the-live-app)
4. [Run locally](#run-locally)
5. [Sample data](#sample-data)
6. [Verify everything works (step by step)](#verify-everything-works-step-by-step)
7. [Troubleshooting](#troubleshooting)
8. [Architecture and project structure](#architecture-and-project-structure)
9. [API overview](#api-overview)
10. [Machine learning](#machine-learning)
11. [Limitations and roadmap](#limitations-and-roadmap)

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

## Tech stack

| Layer | Technologies |
|---|---|
| Frontend | React 19, Vite, Tailwind CSS, Axios |
| Backend | Python, FastAPI, SQLAlchemy, Passlib (bcrypt), JWT |
| ML / data | Scikit-learn, SHAP, Pandas, NumPy, Joblib |
| Database | SQLite for development; PostgreSQL-compatible through SQLAlchemy |
| Deployment | Vercel (frontend), Render (backend) |

---

## Try the live app

Both the frontend and the backend are deployed, so you don't need to install anything.

1. **Wake the backend.** Open `<backend URL>/docs`. If the backend is on a free Render plan, the first request can take up to a minute while the service wakes up. Wait until the Swagger page loads.
2. **Open the app.** Go to https://churn-prediction-roan.vercel.app.
3. **Create an account.** Click *Register*, fill in the form and submit, then log in.
   `TODO: if you have a demo account, list its email and password here, and explain how to get an Admin role.`
4. **Explore.** Follow the checklist in [Verify everything works](#verify-everything-works-step-by-step) to test each feature, including model training with the sample data.

---

## Run locally

**Prerequisites:** Python 3.10+, Node.js 18+, Git.

### 1. Clone the repository

```bash
git clone https://github.com/apoorvjain2911/churn-prediction.git
cd churn-prediction
```

### 2. Start the backend

```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create `backend/.env`:

```
DATABASE_URL=sqlite:///./app.db
FRONTEND_URL=http://localhost:5173
CORS_ORIGINS=http://localhost:5173
SECRET_KEY=change-me
```

> `TODO: make sure the variable names above match what core/ reads, especially the JWT secret.`

Run the server:

```bash
uvicorn main:app --reload
```

The API is now at http://localhost:8000 and its documentation at http://localhost:8000/docs.

### 3. Start the frontend

In a second terminal:

```bash
cd frontend
npm install
```

Create `frontend/.env`:

```
VITE_API_BASE_URL=http://localhost:8000
```

Run the dev server:

```bash
npm run dev
```

The app is now at http://localhost:5173.

> To point a local frontend at the deployed backend instead, set `VITE_API_BASE_URL` to your Render URL. To test the deployed frontend, no setup is needed.

---

## Sample data

Two CSV files are included in the `data/` folder. Both use the same 21 columns.

| File | Rows | Use it for |
|---|---|---|
| `data/churn_sample_data.csv` | 20 | A quick check that file upload and validation work. Too small to train a meaningful model. |
| `data/churn_training_data.csv` | 1,000 | Training and retraining the model, and checking predictions and SHAP explanations. |

`churn_training_data.csv` is **synthetic**. It was generated to follow realistic patterns (month-to-month contracts, short tenure, fiber optic and electronic-check payments raise churn risk; longer contracts and tech support lower it) with about 27% churn. It is for testing the application only; it is not real customer data.

### Columns

| Column | Type | Values |
|---|---|---|
| `customerID` | integer | Unique ID |
| `gender` | text | Male, Female |
| `SeniorCitizen` | integer | 0 or 1 |
| `Partner`, `Dependents` | text | Yes, No |
| `tenure` | integer | Months with the company |
| `PhoneService` | text | Yes |
| `MultipleLines` | text | Yes, No |
| `InternetService` | text | DSL, Fiber optic |
| `OnlineSecurity`, `OnlineBackup`, `DeviceProtection`, `TechSupport`, `StreamingTV`, `StreamingMovies` | text | Yes, No |
| `Contract` | text | Month-to-month, One year, Two year |
| `PaperlessBilling` | text | Yes, No |
| `PaymentMethod` | text | Electronic check, Mailed check, Bank transfer (automatic), Credit card (automatic) |
| `MonthlyCharges` | number | Monthly bill |
| `TotalCharges` | number | Total billed to date |
| `Churn` | text | **Target:** Yes (churned) or No |

When using your own data, keep these column names and category values, and make sure there are no missing values.

---

## Verify everything works (step by step)

Follow these steps on either the live app or your local setup. Each step lists what you should see. If a step fails, see [Troubleshooting](#troubleshooting).

### A. Backend health

| # | Action | Expected result |
|---|---|---|
| A1 | Open `<backend URL>/docs` | The Swagger UI loads and lists the endpoint groups |
| A2 | In Swagger, run `POST /auth/register` with a test email and password | `200` or `201` response with the new user |
| A3 | Run `POST /auth/login` with the same credentials | A response containing an access token |
| A4 | Click **Authorize** in Swagger, paste the token, then run `GET /auth/me` | Your user details |

### B. Frontend and authentication

| # | Action | Expected result |
|---|---|---|
| B1 | Open the frontend and register a user | Registration succeeds |
| B2 | Log in | You land on the dashboard |
| B3 | Refresh the page | You stay logged in |
| B4 | Open a protected page in a private window without logging in | You are redirected to the login page |

### C. Customers

| # | Action | Expected result |
|---|---|---|
| C1 | Add a customer | The customer appears in the list |
| C2 | Search for them, then filter and sort | The list updates correctly |
| C3 | Edit the customer, then delete them | The changes are reflected in the list |

### D. Upload and train the model

You need an **Admin** account for training. `TODO: explain how a user becomes Admin in your app.`

| # | Action | Expected result |
|---|---|---|
| D1 | Upload `data/churn_sample_data.csv` first (*Upload* page, or `POST /upload`) | The upload succeeds and reports 20 rows. This confirms the upload path works. |
| D2 | Upload `data/churn_training_data.csv` | The upload succeeds and reports 1,000 rows |
| D3 | Trigger training (*Admin → Model Retraining*, or `POST /train`) | A success message, and the model status shows a trained model with an updated timestamp |
| D4 | Open *Admin → Model Status* | Shows the model as trained |

> Training on the 20-row file is expected to give poor or unstable results, so use the 1,000-row file for training.

### E. Predictions and explanations

| # | Action | Expected result |
|---|---|---|
| E1 | Predict churn for a single customer (*Prediction* page, or `POST /predict`) | A churn probability and a Low, Medium or High risk label |
| E2 | Try a high-risk profile: Month-to-month contract, tenure 2, Fiber optic, Electronic check, no TechSupport | A higher probability than a low-risk profile |
| E3 | Try a low-risk profile: Two year contract, tenure 60, TechSupport Yes | A lower probability |
| E4 | Run a batch prediction (`POST /predict/batch`) | One prediction per customer |
| E5 | Open a customer's SHAP explanation (`GET /xai/customers/{id}`) | Feature contributions and churn drivers |
| E6 | Check the prediction history | Your earlier predictions are listed |

If E2 gives a higher risk than E3, the model has learned the expected relationships.

### F. Analytics and the rest of the platform

| # | Action | Expected result |
|---|---|---|
| F1 | Open the dashboard | Customer counts, churn statistics and risk distribution reflect your data |
| F2 | Open *CLV* | Top valuable customers are listed |
| F3 | Create a segment and assign a customer to it | Segment statistics update |
| F4 | Create, edit and delete a report | Each action succeeds |
| F5 | As Admin, change a user's role and deactivate a user | The change is saved and takes effect |

---

## Troubleshooting

| Problem | Likely cause and fix |
|---|---|
| The live app loads but login or data calls fail | The backend may be asleep on a free Render plan. Open `<backend URL>/docs`, wait for it to load, then retry. |
| CORS error in the browser console | The backend `CORS_ORIGINS` must include the exact frontend URL. Locally it is `http://localhost:5173`. |
| Frontend calls the wrong server | Check `VITE_API_BASE_URL` and restart `npm run dev` after changing `.env`. |
| `401 Unauthorized` | Your token expired or is missing. Log in again. |
| `403 Forbidden` on training or admin pages | The account is not an Admin. |
| Upload rejected | Check the column names, the `Yes`/`No` spelling and that there are no empty cells. See [Columns](#columns). |
| Predictions fail before training | Train the model first (step D3). |
| Data disappears on the deployed backend | SQLite files are lost when a Render instance restarts. Use a hosted PostgreSQL database for persistence. |
| `ModuleNotFoundError` locally | Activate the virtual environment and re-run `pip install -r requirements.txt`. |

---

## Architecture and project structure

```
React (Vite)  ──HTTPS/JSON──►  FastAPI  ──►  Services  ──►  SQLAlchemy ──► Database
                                  │              │
                               Schemas        ML model (Joblib)
                             (validation)     + SHAP explainer
```

Requests are validated by Pydantic schemas, handled by routers in `api/`, passed to business logic in `services/`, and persisted through SQLAlchemy models. The trained model is stored with Joblib and loaded by the prediction and explainability services.

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

data/
├── churn_sample_data.csv      # 20 rows, upload smoke test
└── churn_training_data.csv    # 1,000 synthetic rows, training
```

## API overview

Interactive documentation is available at `/docs` (Swagger UI).

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

> `TODO: replace the "CRUD endpoints" rows with the exact routes from /docs.`

## Machine learning

- **Model:** Random Forest classifier trained on customer attributes, served through `POST /predict`.
- **Risk levels:** probability thresholds map each customer to Low, Medium or High risk.
- **Explainability:** SHAP values give global feature importance and a per-customer breakdown of what pushed the prediction up or down.
- **Retraining:** admins can retrain the model with `POST /train` after uploading new data.

> `TODO: add your real evaluation results (accuracy, precision, recall, F1, ROC-AUC), the dataset used and the train/test split.` Results on the synthetic file in `data/` describe the generator, not real customers, so don't quote them as real-world performance.

## Limitations and roadmap

**Current limitations**
- The development database is SQLite; PostgreSQL has not been used in production.
- No Docker or CI/CD setup.
- No automated test suite or model versioning yet.

**Roadmap**
- LLM-based AI copilot for customer insights
- PDF report generation
- Email automation and real-time notifications
- Customer activity timeline
- Docker support and a CI/CD pipeline
- PostgreSQL in production
- Model versioning
- Multi-tenant support

---

## Author

**Apoorv Jain**, MANIT Bhopal
AI · Machine Learning · Full-Stack Development
[GitHub](https://github.com/apoorvjain2911) · [LinkedIn](https://linkedin.com/in/apoorv-jain)
