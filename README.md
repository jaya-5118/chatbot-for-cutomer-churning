# 🤖 Chatbot for Customer Service — Enterprise AI Support Suite

[![Live Demo](https://img.shields.io/badge/Live_Demo-GitHub_Pages-brightgreen?style=for-the-badge&logo=github)](https://jaya-5118.github.io/chatbot-for-cutomer-churning/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-82.25%25_Acc-F7931E.svg?style=flat&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)

An enterprise-ready, portfolio-grade **AI Customer Service & Support Intelligence Platform** built with **FastAPI**, **scikit-learn (Logistic Regression + TF-IDF)**, **Sentiment Analysis**, and a commercial **SaaS dashboard interface**.

---

## 🌐 Live Web Demo

**Anyone can open and test the application directly in their browser without installing anything:**

👉 **[https://jaya-5118.github.io/chatbot-for-cutomer-churning/](https://jaya-5118.github.io/chatbot-for-cutomer-churning/)**

---

## ✨ Features

- **💬 Live Customer Support Widget**: Autonomous resolution of order tracking (`#ORD-9842`), returns & refunds, shipping policies, cancellations, and store hours.
- **🎯 23 Intent Classes Trained**: Machine Learning model trained on 1,151 samples achieving **82.25% Accuracy** and **0.8200 F1-Score**.
- **😊 Frustration & Mood Detection**: Real-time customer polarity scoring, urgency classification (Low, Medium, High, Critical), and automatic escalation flags.
- **📚 Verified Policy Citations**: Indexes official shipping, return, payment, cancellation, and FAQ policies for instant cited answers.
- **🚨 Human Agent Escalation Queue**: Automatic or 1-click handover to live agents with preserved conversation history.
- **📊 Executive Telemetry Hub**: Live KPI counters for Total Inquiries, AI Resolution Rate (~88%), Average Latency (~3.8ms), and Intent Distribution charts.

---

## 🛠️ How Anyone Can Run It Locally

### Option A: Open Live Web Link (No installation needed)
Simply click **[https://jaya-5118.github.io/chatbot-for-cutomer-churning/](https://jaya-5118.github.io/chatbot-for-cutomer-churning/)**.

### Option B: Run Locally with Python FastAPI Backend
```bash
# 1. Clone the repository
git clone https://github.com/jaya-5118/chatbot-for-cutomer-churning.git
cd chatbot-for-cutomer-churning

# 2. Install dependencies
cd backend
pip install -r requirements.txt

# 3. Start the FastAPI server
python -m uvicorn app.main:app --app-dir . --host 0.0.0.0 --port 8000 --reload
```
Open **`http://localhost:8000/`** in your browser!

---

## 📝 License

Distributed under the MIT License.
