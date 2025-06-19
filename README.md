# 🧪 AI Tester for Django Apps (PoC_Team_A_LangGraph)

> 🚀 A Proof-of-Concept that automates functional spec and test case generation using LLMs for Django projects.

![Python](https://img.shields.io/badge/python-3.8%2B-blue) 
![License](https://img.shields.io/badge/license-MIT-green)
![LangGraph](https://img.shields.io/badge/powered%20by-LangGraph-purple)

---

## 🧠 Approach

This PoC takes a **Django project GitHub URL** as input and automates:

1. **Containerizing** the Django project and serving it on `http://localhost:8000`.
2. Using a **Python script** to fetch the **HTML source code** of each rendered page.
3. Passing that source code to a **Large Language Model (LLM)** to:
   - Generate a `functional_specs.md` file.
   - Map the **actual user interaction flow** (based on real URL paths, not hallucinated ones).
4. Iterating through each discovered URL:
   - Extracting the page source.
   - Feeding it to the LLM to **generate precise test cases**.
5. Executing the generated test cases and generating a **dedicated test report** for each page.

💡 *By using actual source code, we eliminate reliance on LLM assumptions and ensure accuracy in test coverage.*

---

## ⚙️ Getting Started

### 🔁 Clone the Repository

```bash
git clone https://github.com/amartyadebdas/AI-Tester-Django
cd AI-Tester-Django
```

### 🐍 Create and Activate a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 📦 Install Dependencies

```bash
pip install -r requirements_dev.txt
```

### 🚀 Run the App

> *For demonstration, this uses a Django ToDo Application as a sample project.*

```bash
python3 -m langgraph_app.langgraph_app
```

✅ That’s it — you’ll get the results automatically!

---

## 💬 Contact

If you'd like to connect, suggest improvements, or collaborate:

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Amartya%20Debdas-blue?logo=linkedin)](https://www.linkedin.com/in/amartya-debdas-87669721a/)

---
