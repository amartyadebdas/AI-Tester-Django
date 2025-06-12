import os
from pathlib import Path
import openai

from langchain_core.prompts import ChatPromptTemplate

def generate_llm_report(page_name, prompt, llm, parser):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print(" OPENAI_API_KEY environment variable not set.")
        return

    base_dir = Path(__file__).resolve().parent.parent

    spec_path = base_dir / "outputs" / "functional_specifications.md"
    screenshot_before = base_dir / "screenshots" / f"before_{page_name}.png"
    screenshot_after = base_dir / "screenshots" / f"after_{page_name}.png"
    test_file = base_dir / "tests" / "selenium" / f"test_{page_name}.py"
    output = base_dir/"testcase_output"/f"output_{test_file}.txt"

    report_output = base_dir / "reports" / f"final_report_{page_name}.md"
    report_output.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(spec_path, "r") as f:
            spec_content = f.read()

        with open(test_file, "r") as f:
            test_code = f.read()

    except FileNotFoundError as e:
        print(f"Missing file: {e}")
        return

    try:
    
        final_prompt = ChatPromptTemplate.from_messages([
            ('system', prompt),
            ('human','{input}')
        ])

        chain = final_prompt | llm | parser

        response = chain.invoke({
            "spec_content":spec_content,
            "test_code":test_code,
            "ouptut_test_code": output,
            "page_name":page_name,

            "input":"Generate concise report based on the information provided information."
        }
        )

        report_md = response

        with open(report_output, "w") as f:
            f.write(report_md)

        print(f" Final LLM-generated report saved to: {report_output}")

    except Exception as e:
        print(f" OpenAI Error: {e}")


# if __name__ == "__main__":
#     generate_llm_report("register")
#     generate_llm_report("login")
#     generate_llm_report("polls_list")
