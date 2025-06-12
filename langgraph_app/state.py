from typing import TypedDict, Optional, List, Tuple

class RepoState(TypedDict):
    """
    Represents the state of our repository operations and testing workflow.
    """
    repo_url: str
    target_dir: str 
    docker_image_name: str 
    
    # Status flags
    clone_success: Optional[bool]
    docker_run_success: Optional[bool]
    base_spec_extraction_success: Optional[bool]
    selenium_test_generation_success: Optional[bool]
    report_generation_success: Optional[bool]

    # Error messages for each stage
    error_message: Optional[str]
    clone_error: Optional[str]
    docker_error: Optional[str]
    base_spec_error: Optional[str]
    selenium_gen_error: Optional[str]
    report_gen_error: Optional[str]

    # Data generated at various stages
    extracted_routes: Optional[List[Tuple[str, str]]] # List of (page_name, path) tuples
    generated_test_scripts_paths: Optional[List[str]] # Paths to generated test scripts
    final_report_paths: Optional[List[str]] # Paths to final generated reports