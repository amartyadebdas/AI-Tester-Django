import os
import re
import requests
import openai
from dotenv import load_dotenv
from pathlib import Path 
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_SPEC = BASE_DIR / "outputs" / "functional_specifications.md"
TESTS_OUTPUT_DIR = BASE_DIR / "tests" / "selenium"
SCREENSHOTS_DIR = BASE_DIR / "screenshots"
BASE_URL = "http://localhost:8000"

os.makedirs(TESTS_OUTPUT_DIR, exist_ok=True)
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)


def extract_routes_from_markdown(md_path):
    routes = []
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = r"\*\*(.*?) \(`/([^`]+)`\)"
    matches = re.findall(pattern, content)
    for name, path in matches:
        routes.append((name.strip().lower().replace(" ", "_"), f"/{path.strip()}"))
    return routes


def fetch_html_from_url(path):
    url = f"{BASE_URL}{path}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        print(f"[✓] Fetched {url}")
        return response.text
    except requests.RequestException as e:
        print(f"[✗] Failed to fetch {url}: {e}")
        return None


def get_selenium_test_from_html(html_content, page_name, path, prompt, llm, parser):
    screenshot_before_path = str(SCREENSHOTS_DIR / f"before_{page_name}.png").replace('\\', '/')
    screenshot_after_path = str(SCREENSHOTS_DIR / f"after_{page_name}.png").replace('\\', '/')

    try:
        final_prompt = ChatPromptTemplate.from_messages([
            ('system', prompt),
            ('human','{input}')
        ])

        chain = final_prompt | llm | parser

        response = chain.invoke({
            "page_name":page_name,
            "html_content":html_content,
            "path":path,
            "input":"Generate syntactically and semantically accurate selenium testcases for the given page."
        }
        )

        return response
    except Exception as e:
        print(f"[✗] OpenAI error for {path}: {e}")
        return None

def clean_gpt_generated_code(raw_code: str) -> str:
    raw_code = raw_code.strip()

    fenced_pattern = r"(?i)```(?:python)?\s*(.*?)```"
    match = re.search(fenced_pattern, raw_code, re.DOTALL)
    if match:
        return match.group(1).strip()

    if raw_code.lower().startswith("python\n"):
        return raw_code.split("\n", 1)[1].strip()

    return raw_code



def save_test_script(code, filename):
    cleaned_code = clean_gpt_generated_code(code)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(cleaned_code)
    print(f"[✓] Cleaned & saved script to {filename}")



# if __name__ == "__main__":
#     routes = extract_routes_from_markdown(INPUT_SPEC)

#     for name, path in routes:
#         html = fetch_html_from_url(path)
#         if not html:
#             continue

#         test_code = get_selenium_test_from_html(html, name, path)
#         if not test_code:
#             continue

#         save_test_script(test_code, os.path.join(TESTS_OUTPUT_DIR, f"test_{name}.py"))
