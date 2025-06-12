from langgraph.graph import StateGraph, END
from langgraph_app.state import RepoState
from langgraph_app.nodes import (
    clone_repo_node,
    docker_runner_node,
    extract_base_spec_node,
    generate_selenium_tests_node,
    generate_report_node
)
from langgraph_app.routers import (
    decide_after_clone,
    decide_after_docker_run,
    decide_after_base_spec_extraction,
    decide_after_selenium_gen,
    decide_after_report_gen
)
from logger import logging
import os
import json 

def build_qa_automation_graph():
    workflow = StateGraph(RepoState)

    # 1. Add Nodes
    workflow.add_node("clone_repo", clone_repo_node)
    workflow.add_node("docker_runner", docker_runner_node)
    workflow.add_node("extract_base_spec", extract_base_spec_node)
    workflow.add_node("generate_selenium_tests", generate_selenium_tests_node)
    workflow.add_node("generate_reports", generate_report_node)

    # 2. Set Entry Point
    workflow.set_entry_point("clone_repo")

    # 3. Add Edges (Transitions)
    workflow.add_conditional_edges(
        "clone_repo",
        decide_after_clone,
        {
            "docker_runner": "docker_runner",
            "end_with_error": END
        }
    )

    workflow.add_conditional_edges(
        "docker_runner",
        decide_after_docker_run,
        {
            "extract_base_spec": "extract_base_spec",
            "end_with_error": END
        }
    )

    workflow.add_conditional_edges(
        "extract_base_spec",
        decide_after_base_spec_extraction,
        {
            "generate_selenium_tests": "generate_selenium_tests",
            "end_with_error": END
        }
    )

    workflow.add_conditional_edges(
        "generate_selenium_tests",
        decide_after_selenium_gen,
        {
            "generate_reports": "generate_reports",
            "end_with_error": END
        }
    )

    # After reports, the workflow is essentially done, we can have a final decision or just end.
    workflow.add_conditional_edges(
        "generate_reports",
        decide_after_report_gen, # This router can still check overall success for final logging
        {
            "end_success": END,
            "end_with_error": END 
        }
    )

    # Compile the graph
    app = workflow.compile()
    return app

if __name__ == "__main__":
    base_proj_dir = os.path.dirname(os.path.abspath(__file__))

    output_dir = os.path.join(base_proj_dir, "outputs")
    os.makedirs(output_dir, exist_ok=True)

    app = build_qa_automation_graph()

    initial_state = RepoState(
        repo_url="https://github.com/devmahmud/Django-Poll-App",
        target_dir=os.path.join(base_proj_dir, "repo"),
        docker_image_name="fst_sandbox_app",
        clone_success=None,
        docker_run_success=None,
        base_spec_extraction_success=None,
        selenium_test_generation_success=None,
        report_generation_success=None,
        error_message=None,
        clone_error=None,
        docker_error=None,
        base_spec_error=None,
        selenium_gen_error=None,
        report_gen_error=None,
        extracted_routes=None,
        generated_test_scripts_paths=None,
        final_report_paths=None
    )

    logging.info("Starting Langraph QA Automation workflow...")
    final_state = {}

    try:
        final_state = app.invoke(initial_state)
        logging.info("\n--- Langraph Workflow Finished ---")

        output_filename = os.path.join(output_dir, "final_state.json")
        try:
            with open(output_filename, 'w') as f:
                json.dump(final_state, f, indent=4)
            logging.info(f"Final state saved to: {output_filename}")
        except Exception as e:
            logging.error(f"Failed to save final state to file: {e}")

        if final_state.get("report_generation_success") and final_state.get("selenium_test_generation_success") and final_state.get("base_spec_extraction_success") and final_state.get("docker_run_success") and final_state.get("clone_success"):
            print("\n All workflow steps completed successfully!")
            for path in final_state.get("final_report_paths", []):
                print(f"   Report: {path}")
        else:
            print("\n Workflow completed with errors or partial success. Check logs for details.")
            if final_state.get("error_message"):
                print(f"   Overall Error: {final_state['error_message']}")
            if not final_state.get("clone_success"):
                print(f"   Clone Error: {final_state.get('clone_error', 'N/A')}")
            if not final_state.get("docker_run_success"):
                print(f"   Docker Error: {final_state.get('docker_error', 'N/A')}")
            if not final_state.get("base_spec_extraction_success"):
                print(f"   Base Spec Error: {final_state.get('base_spec_error', 'N/A')}")
            if not final_state.get("selenium_test_generation_success"):
                print(f"   Selenium Gen Error: {final_state.get('selenium_gen_error', 'N/A')}")
            if not final_state.get("report_generation_success"):
                print(f"   Report Gen Error: {final_state.get('report_gen_error', 'N/A')}")

    except Exception as e:
        logging.critical(f"An unhandled exception occurred during Langraph execution: {e}")
        print(f"\n Langraph execution crashed: {e}")
