# AI Customer Intelligence Platform

A full-stack AI-powered Customer Intelligence Platform that helps businesses predict customer churn, manage customer relationships, analyze customer lifetime value, explain AI predictions, and generate actionable business insights.

## Live Demo

**Frontend:** https://churn-prediction-roan.vercel.app

---

# Overview

This project started as a Customer Churn Prediction Dashboard and has evolved into a complete AI-powered CRM & Customer Intelligence Platform.

The application enables organizations to:

- Manage customers
- Predict customer churn using Machine Learning
- Explain predictions using SHAP Explainable AI
- Analyze Customer Lifetime Value (CLV)
- Generate business reports
- Segment customers
- Manage users with Role-Based Access Control
- Monitor analytics through an interactive dashboard

Built using **React + FastAPI + Scikit-Learn**.

---

# Features

## Authentication & Security

- JWT Authentication
- Secure Login & Registration
- Password Hashing (bcrypt)
- Protected Routes
- Role-Based Access Control (RBAC)
- Admin & Sales Manager Roles

---

## Customer Management

- Add Customer
- Update Customer
- Delete Customer
- Customer Search
- Customer Details
- Customer Filtering
- Customer Sorting

---

## AI Churn Prediction

- Random Forest Churn Prediction
- Probability Score
- Risk Classification
  - Low
  - Medium
  - High
- Batch Prediction
- Prediction History

---

## Explainable AI (SHAP)

- SHAP Feature Importance
- Customer-specific AI Explanation
- Business Explanation
- Churn Drivers
- AI-powered Retention Recommendations

---

## Customer Lifetime Value (CLV)

- CLV Calculation
- Top Valuable Customers
- Customer Value Analysis

---

## Reports

- Report Management
- Create Reports
- Update Reports
- Delete Reports

---

## Customer Segmentation

- Customer Segments
- Segment Assignment
- Segment Statistics

---

## Admin Dashboard

- User Management
- Change User Roles
- Activate/Deactivate Users
- Model Status
- Model Retraining

---

## Analytics Dashboard

- Customer Overview
- Churn Statistics
- Risk Distribution
- Feature Importance
- Prediction Analytics

---

# Tech Stack

## Frontend

- React 19
- Vite
- Tailwind CSS
- Axios

---

## Backend

- FastAPI
- Python
- Scikit-Learn
- SHAP
- Pandas
- NumPy
- SQLAlchemy
- Joblib
- Passlib
- JWT Authentication

---

## Database

- SQLite (Development)
- PostgreSQL Compatible

---

## Deployment

- Vercel
- Render

---

# Project Structure

```
backend/
│
├── api/
├── services/
├── models/
├── schemas/
├── database/
├── core/
└── main.py

frontend/
│
├── components/
├── pages/
├── context/
├── services/
└── App.jsx
```

---

# Getting Started

## Backend

```bash
cd backend

pip install -r requirements.txt

uvicorn main:app --reload
```

---

## Frontend

```bash
cd frontend

npm install

npm run dev
```

---

# Environment Variables

## Backend

```env
DATABASE_URL=sqlite:///./app.db

FRONTEND_URL=http://localhost:5173

CORS_ORIGINS=http://localhost:5173
```

---

## Frontend

```env
VITE_API_BASE_URL=http://localhost:8000
```

---

# API Modules

### Authentication

- POST /auth/register
- POST /auth/login
- GET /auth/me

---

### Customers

- GET /customers
- POST /customers
- PUT /customers/{id}
- DELETE /customers/{id}

---

### Dashboard

- GET /dashboard/summary

---

### Prediction

- POST /predict
- POST /predict/batch

---

### Upload

- POST /upload

---

### Training

- POST /train

---

### SHAP Explainability

- GET /xai/customers/{id}

---

### Customer Lifetime Value

- GET /clv/summary
- GET /clv/top
- POST /clv/refresh/{id}

---

### Reports

- CRUD APIs

---

### Segments

- CRUD APIs
- Customer Assignment

---

### Admin

- Dashboard
- User Management
- Role Management
- Status Management
- Model Retraining

---

# Future Improvements

- AI Copilot (LLM Integration)
- PDF Report Generation
- Email Automation
- Real-time Notifications
- Customer Timeline
- Docker Support
- CI/CD Pipeline
- PostgreSQL Production Database
- Model Versioning
- Multi-Tenant Support

---

# Screenshots

Add screenshots of:

- Dashboard
- Customer Management
- SHAP Explanation
- Admin Panel
- Reports
- Segments
- Login Page

---

# Author

**Apoorv Jain**

Mechanical Engineering | MANIT Bhopal

AI • Machine Learning • Full Stack Development