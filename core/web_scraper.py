import os
import requests
import openai
import logging
from dotenv import load_dotenv
from logger import logging
from pathlib import Path

from langchain_core.prompts import ChatPromptTemplate


# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
BASE_DIR = Path(__file__).resolve().parent.parent


def fetch_source_from_localhost(url="http://localhost:8000"):
    try:
        response = requests.get(url)
        response.raise_for_status()
        logging.info(f"Fetched source from {url}")
        return response.text
    except requests.RequestException as e:
        logging.error(f"Failed to fetch {url}: {e}")
        return ""


def get_functional_spec_from_html(html_source, prompt, llm, parser):
    if not html_source:
        logging.warning("No HTML source to analyze.")
        return "No HTML source to analyze."

    try:
        final_prompt = ChatPromptTemplate.from_messages([
            ('system', prompt),
            ('human','{input}')
        ])

        chain = final_prompt | llm | parser

        response = chain.invoke({
            "html_source":html_source,
            "input":"Get the functional specifications from the given html code."
        }
        )

        return response
    except Exception as e:
        return f" Error from OpenAI: {e}"


def save_spec_to_markdown(spec_text, output_file=None):
    if output_file is None:
        output_file = BASE_DIR / "outputs" / "functional_specifications.md"
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(spec_text)
    
    logging.info(f"Functional spec saved to {output_file}")

# if __name__ == "__main__":
#     html = fetch_source_from_localhost()
#     spec = get_functional_spec_from_html(html)
#     save_spec_to_markdown(spec)
