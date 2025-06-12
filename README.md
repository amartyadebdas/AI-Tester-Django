# PoC_Team_A_LangGraph

## APPROACH:
I followed simple approach , get the django github Url from user . Containerize it to access the app at localhost port 8000 . Now Created a python script that will fetch the source code the page . Then give this source code to LLM to generate functional spects.md . The good thing about this md file is we will get User Interaction flow with their URL. The Reason of doing this is sometImes the Llm generates random url so we use source code to access the actual path. Now In the next step- The python script will get each url one by one from readme , access it’s source code and give this source code to LLM to generate test_cases , at the end we will execute test cases , and generate sepearte report for each page . 

## Get Started

1. Clone the repo:
```bash
git clone git@github.com:amartyadebdas/AI-Tester-Django.git

```

3. Create virtual Environment (UBUNTU):
```bash
python3 -m venv venv
```

4. Activate virtual Environment(UBUNTU):
```bash
source venv/bin/activate
```
5. Install the dependencies:
```bash

pip install -r requirements_dev.txt

```

6. Run the application:
```bash
python3 -m langgraph_app.langgraph_app
```
---

### NOTE: 
Please connect with me if you encounter any errors while running the application. Also, inform me if you face any package-related issues after installing the `requirements.txt`.