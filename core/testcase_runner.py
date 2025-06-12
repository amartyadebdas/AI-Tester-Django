import subprocess
from pathlib import Path

def run_test_case(file: str):
    """
    Runs a Python test file and saves its full output to:
    output_testcase/output_<filename>.txt

    Args:
        file (str): Path to the Python file to run.

    Creates:
        output_testcase/output_<filename>.txt containing stdout and stderr.
    """
    output_dir = Path("testcase_output")
    output_dir.mkdir(exist_ok=True)

    output_filename = f"output_{Path(file).stem}.txt"
    output_path = output_dir / output_filename

    try:
        result = subprocess.run(
            ["python", file],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # combine stdout and stderr
            text=True
        )

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result.stdout)

    except Exception as e:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"[ERROR] Failed to run test case: {e}\n")