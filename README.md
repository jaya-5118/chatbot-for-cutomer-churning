# 🤖 Chatbot for Customer Service — Enterprise AI Support Suite

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-82.25%25_Acc-F7931E.svg?style=flat&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

An enterprise-ready, portfolio-grade **AI Customer Service & Support Intelligence Platform** built with **FastAPI**, **scikit-learn (Logistic Regression + TF-IDF)**, **Sentiment Analysis**, and a commercial **Intercom/Linear-style SaaS dashboard interface**.

---

## ✨ Features

- **💬 Live Customer Support Widget**: Autonomous resolution of order tracking (`#ORD-9842`), returns & refunds, shipping policies, cancellations, and store hours.
- **🎯 23 Intent Classes Trained**: Machine Learning model trained on 1,151 samples achieving **82.25% Accuracy** and **0.8200 F1-Score**.
- **😊 Frustration & Mood Detection**: Real-time customer polarity scoring, urgency classification (Low, Medium, High, Critical), and automatic escalation flags.
- **📚 Verified Policy Citations**: Indexes official shipping, return, payment, cancellation, and FAQ policies for instant cited answers.
- **🚨 Human Agent Escalation Queue**: Automatic or 1-click handover to live agents with preserved conversation history.
- **📊 Executive Telemetry Hub**: Live KPI counters for Total Inquiries, AI Resolution Rate (~88%), Average Latency (~3.8ms), and Intent Distribution charts.

---

## 🛠️ Tech Stack

- **Backend:** FastAPI, Uvicorn, Python 3.10+
- **Machine Learning:** scikit-learn (Logistic Regression, TF-IDF Vectorizer), NumPy, Pandas, Joblib
- **Frontend:** Vanilla HTML5, Modern CSS3 (Glassmorphic Linear/Stripe design system), JavaScript (ES6+), Google Fonts (*Outfit*, *Inter*, *JetBrains Mono*)
- **Documentation:** Interactive OpenAPI / Swagger UI (`/docs`)

---

## 🚀 Quick Start Guide

### 1. Clone the Repository
```bash
git clone https://github.com/jaya-5118/chatbot-for-cutomer-churning.git
cd chatbot-for-cutomer-churning
```

### 2. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 3. (Optional) Train the Intent Model
```bash
python training/train.py
```

### 4. Run the Application Server
```bash
python -m uvicorn app.main:app --app-dir . --host 0.0.0.0 --port 8000 --reload
```

Open your browser at **`http://localhost:8000/`** to view the live dashboard!

---

## 📸 Screenshots & Architecture

- **Live Chat Widget:** `http://localhost:8000/`
- **Interactive Swagger Docs:** `http://localhost:8000/docs`
- **API Health Check:** `http://localhost:8000/api/v1/health`

---

## 📝 License

Distributed under the MIT License.
