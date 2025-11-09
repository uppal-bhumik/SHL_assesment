# SHL GenAI Assessment Recommendation System

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red?logo=streamlit)
![LangChain](https://img.shields.io/badge/LangChain-0.1+-orange?logo=langchain)
![OpenAI](https://img.shields.io/badge/OpenAI-gpt--3.5--turbo-blue?logo=openai)

---

### 🔴 LIVE APPLICATION LINKS 🔴


>
> * **Frontend Web App:** `https://shl-bhumik.streamlit.app/`
> * **Backend API Docs:** `https://shl-api-p9xh.onrender.com`

---

## Project Overview

This is a full-stack, AI-powered web application built for the **SHL Research Intern Hiring Assessment**. It functions as an intelligent assistant for recruiters, taking a natural-language query (like a job description) and recommending the most relevant SHL assessments.

The core of this project is a **RAG (Retrieval-Augmented Generation)** pipeline that uses a "golden dataset" to provide smart, balanced recommendations.

## Core Features

* **Full-Stack Application:** A complete, decoupled system with a FastAPI backend and a Streamlit frontend.
* **RAG Pipeline:** Uses LangChain to power a "smart" AI "brain."
* **Vector Search:** Employs ChromaDB and OpenAI Embeddings to find the most relevant assessments.
* **"Balance Requirement" Solved:** The AI (`gpt-3.5-turbo`) is specifically prompted to provide a *balanced mix* of technical (e.g., "Java") and behavioral (e.g., "Collaboration") tests.
* **Strategic Data Pipeline:** Includes a professional data pipeline that involved:
    1.  A robust Selenium scraper (`scripts/scraper.py`) to bypass anti-bot measures and prove data extraction was possible.
    2.  A **strategic pivot** to a 27-item "golden dataset" (`data/Book1.xlsx - Sheet1.csv`) to ensure a high-quality, reliable demo that could be completed on time.

## Tech Stack

* **Backend:** FastAPI, Uvicorn
* **Frontend:** Streamlit
* **AI (RAG):** LangChain, OpenAI (`gpt-3.5-turbo`)
* **Vector Database:** ChromaDB
* **Data Handling:** Pandas, Openpyxl
* **Configuration:** `python-dotenv`

## 🚀 How to Run This Project Locally

### 1. Clone the Repository
```bash
git clone https://github.com/uppal-bhumik/SHL_assesment
cd SHL

2. Set Up a Virtual Environment (Recommended)

# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate

3. Install All Dependencies
pip install -r requirements.txt

4. Create Your .env File
Create a file named .env in the root of the project (SHL/.env) and add your OpenAI API key:

OPENAI_API_KEY="sk-..."

5. Run the Backend (Terminal 1)
In your first terminal, start the FastAPI server:

python -m uvicorn app.main:app --reload

Server will be running at http://127.0.0.1:8000

6. Run the Frontend (Terminal 2)
In a new, separate terminal, run the Streamlit app:

streamlit run frontend/app.py

Your browser will automatically open to http://localhost:8501

Project Structure
SHL/
├── app/
│   ├── core/
│   │   └── logic.py         # The RAG "Brain"
│   └── main.py              # The FastAPI API
├── data/
│   ├── Book1.xlsx - Sheet1.csv  # The 27-item "Golden Dataset"
│   └── test_set.csv           # 9 queries for final submission
├── deliverables/
│   └── final_submission.csv   # Deliverable #5
├── frontend/
│   └── app.py               # The Streamlit Web App
├── scripts/
│   ├── run_tests.py         # Script to generate final_submission.csv
│   └── scraper.py           # The (unused) Selenium scraper PoC
├── .env                     # (Local file for API key)
├── .gitignore
├── README.md                # You are here!
└── requirements.txt         # All Python libraries

---
