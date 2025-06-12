# langgraph_app/routers.py (or keep them in langgraph_app.py if small)
from langgraph_app.state import RepoState
from logger import logging
from langgraph.graph import END

def decide_after_clone(state: RepoState) -> str:
    if state["clone_success"]:
        logging.info("Router: Clone successful. Proceeding to Docker.")
        return "docker_runner"
    else:
        logging.error("Router: Clone failed. Ending workflow.")
        return "end_with_error"

def decide_after_docker_run(state: RepoState) -> str:
    if state["docker_run_success"]:
        logging.info("Router: Docker run successful. Proceeding to extract base spec.")
        return "extract_base_spec"
    else:
        logging.error("Router: Docker run failed. Ending workflow.")
        return "end_with_error"

def decide_after_base_spec_extraction(state: RepoState) -> str:
    if state["base_spec_extraction_success"]:
        logging.info("Router: Base spec extraction successful. Proceeding to generate selenium tests.")
        return "generate_selenium_tests"
    else:
        logging.error("Router: Base spec extraction failed. Ending workflow.")
        return "end_with_error"

def decide_after_selenium_gen(state: RepoState) -> str:
    # We might still want to try report generation even if some selenium tests failed
    # or if no routes were extracted, depending on desired behavior.
    if state["selenium_test_generation_success"]:
        logging.info("Router: Selenium test generation successful (or partially). Proceeding to generate reports.")
        return "generate_reports"
    elif state["selenium_gen_error"]: # If there were issues, but not a hard crash
        logging.warning(f"Router: Selenium test generation had issues: {state['selenium_gen_error']}. Attempting report generation anyway.")
        return "generate_reports"
    else: # A critical error in the node itself
        logging.error("Router: Critical error in Selenium test generation. Ending workflow.")
        return "end_with_error"

def decide_after_report_gen(state: RepoState) -> str:
    if state["report_generation_success"]:
        logging.info("Router: Report generation successful. Workflow complete.")
        return "end_success"
    else:
        logging.error("Router: Report generation failed. Workflow complete with errors.")
        return "end_with_error"

# A final router for handling the end states
def final_decision_router(state: RepoState) -> str:
    if state.get("error_message") or \
       not all([state.get("clone_success", False),
                state.get("docker_run_success", False),
                state.get("base_spec_extraction_success", False),
                state.get("selenium_test_generation_success", False),
                state.get("report_generation_success", False)]):
        return "end_with_error"
    else:
        return "end_success"