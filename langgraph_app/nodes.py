import os
import sys

# Add the parent directory to the Python path to allow importing from 'core'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import all necessary functions from your core modules
from core.clone_repo import clone_repo_from_url
from core.docker_runner import build_and_run_docker_container
from core.web_scraper import fetch_source_from_localhost, get_functional_spec_from_html, save_spec_to_markdown
from core.spec_extractor import extract_routes_from_markdown, fetch_html_from_url, get_selenium_test_from_html, save_test_script
from core.report_generator import generate_llm_report 
from core.testcase_runner import run_test_case
from logger import logging
from langgraph_app.state import RepoState 

from prompt.functional_spec import SPEC_EXTRACTOR
from prompt.generate_reports import GENERATE_REPORTS
from prompt.generate_test_cases import TEST_CASES

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

api_key = os.environ['OPENAI_API_KEY']
llm = ChatOpenAI(model = 'gpt-4o-mini', api_key = api_key)
parser = StrOutputParser()

# --- Node 1: Clone Repository ---
def clone_repo_node(state: RepoState) -> dict:
    logging.info("Langraph Node: Executing 'clone_repo_node'")
    repo_url = state["repo_url"]
    target_dir = state["target_dir"]
    try:
        clone_repo_from_url(repo_url, target_dir)
        return {"clone_success": True, "clone_error": None}
    except Exception as e:
        error_msg = f"Clone failed: {e}"
        logging.error(error_msg)
        return {"clone_success": False, "clone_error": error_msg, "error_message": error_msg}

# --- Node 2: Build and Run Docker ---
def docker_runner_node(state: RepoState) -> dict:
    logging.info("Langraph Node: Executing 'docker_runner_node'")
    target_dir = state["target_dir"]
    image_name = state["docker_image_name"]
    try:
        build_and_run_docker_container(target_dir, image_name)
        return {"docker_run_success": True, "docker_error": None}
    except Exception as e:
        error_msg = f"Docker build/run failed: {e}"
        logging.error(error_msg)
        return {"docker_run_success": False, "docker_error": error_msg, "error_message": error_msg}

# --- Node 3: Extract Base Functional Spec ---
def extract_base_spec_node(state: RepoState) -> dict:
    logging.info("Langraph Node: Executing 'extract_base_spec_node'")
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) 
    output_spec_path = os.path.join(base_dir, "outputs", "functional_specifications.md")

    try:
        html = fetch_source_from_localhost()
        if not html:
            raise ValueError("Failed to fetch HTML source from localhost.")
        spec_content = get_functional_spec_from_html(html, SPEC_EXTRACTOR, llm, parser)
        if "Error from OpenAI" in spec_content: # Basic check for OpenAI errors
            raise ValueError(f"OpenAI error during spec generation: {spec_content}")

        save_spec_to_markdown(spec_content, output_spec_path)

        return {
            "base_spec_extraction_success": True,
            "base_spec_error": None
            # "initial_html_source": html,
            # "functional_spec_content": spec_content
        }
    except Exception as e:
        error_msg = f"Base spec extraction failed: {e}"
        logging.error(error_msg)
        return {"base_spec_extraction_success": False, "base_spec_error": error_msg, "error_message": error_msg}

# --- Node 4: Generate Selenium Tests for Each Route ---
def generate_selenium_tests_node(state: RepoState) -> dict:
    logging.info("Langraph Node: Executing 'generate_selenium_tests_node'")
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) # fst_generator root
    input_spec_path = os.path.join(base_dir, "outputs", "functional_specifications.md")
    tests_output_dir = os.path.join(base_dir, "tests", "selenium")

    generated_scripts = []
    error_occurred = False
    error_messages = []

    try:
        routes = extract_routes_from_markdown(input_spec_path)
        print("\n\n routes: ", routes)
        if not routes:
            logging.warning("No routes extracted from functional specification.")
            return {"selenium_test_generation_success": True, "selenium_gen_error": None, "extracted_routes": [], "generated_test_scripts_paths": []}

        for name, path in routes:
            logging.info(f"Generating test for page: {name} ({path})")
            html = fetch_html_from_url(path)
            if not html:
                error_occurred = True
                error_messages.append(f"Could not fetch HTML for {path}")
                continue

            test_code = get_selenium_test_from_html(html, name, path,TEST_CASES, llm, parser)
            if not test_code:
                error_occurred = True
                error_messages.append(f"Could not generate test code for {name} ({path})")
                continue

            script_filename = os.path.join(tests_output_dir, f"test_{name}.py")
            save_test_script(test_code, script_filename)
            run_test_case(script_filename)
            generated_scripts.append(script_filename)

        if error_occurred:
            combined_error_msg = "Some Selenium tests failed to generate: " + "; ".join(error_messages)
            logging.error(combined_error_msg)
            return {
                "selenium_test_generation_success": False,
                "selenium_gen_error": combined_error_msg,
                "error_message": combined_error_msg,
                "extracted_routes": routes,
                "generated_test_scripts_paths": generated_scripts
            }
        else:
            return {
                "selenium_test_generation_success": True,
                "selenium_gen_error": None,
                "extracted_routes": routes,
                "generated_test_scripts_paths": generated_scripts
            }
    except Exception as e:
        error_msg = f"Selenium test generation failed: {e}"
        logging.error(error_msg)
        return {"selenium_test_generation_success": False, "selenium_gen_error": error_msg, "error_message": error_msg}


# --- Node 5: Generate Final LLM Report ---
def generate_report_node(state: RepoState) -> dict:
    logging.info("Langraph Node: Executing 'generate_report_node'")
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) # fst_generator root
    extracted_routes = state.get("extracted_routes", [])
    final_report_paths = []
    error_occurred = False
    error_messages = []

    if not extracted_routes:
        logging.warning("No routes extracted, skipping report generation.")
        return {"report_generation_success": True, "report_gen_error": None, "final_report_paths": []}

    try:
        for page_name, _ in extracted_routes:
            logging.info(f"Generating LLM report for page: {page_name}")
            try:
                generate_llm_report(page_name, GENERATE_REPORTS, llm, parser)
                report_path = os.path.join(base_dir, "reports", f"final_report_{page_name}.md")
                final_report_paths.append(report_path)
            except Exception as e:
                error_occurred = True
                error_messages.append(f"Report generation failed for {page_name}: {e}")
                logging.error(f"Report generation failed for {page_name}: {e}")
                continue 

        if error_occurred:
            combined_error_msg = "Some LLM reports failed to generate: " + "; ".join(error_messages)
            logging.error(combined_error_msg)
            return {
                "report_generation_success": False,
                "report_gen_error": combined_error_msg,
                "error_message": combined_error_msg,
                "final_report_paths": final_report_paths
            }
        else:
            return {
                "report_generation_success": True,
                "report_gen_error": None,
                "final_report_paths": final_report_paths
            }
    except Exception as e:
        error_msg = f"Overall report generation node failed: {e}"
        logging.error(error_msg)
        return {"report_generation_success": False, "report_gen_error": error_msg, "error_message": error_msg}