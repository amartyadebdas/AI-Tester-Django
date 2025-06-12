GENERATE_REPORTS = """
        You are a QA lead. Using the following information, generate a clean, professional QA test report in Markdown format for the `{page_name}` page.
        
        ### Functional Specification:
        {spec_content}
        
        ### Selenium Test Code:
        {test_code}

        ### Result of the Code:
        {ouptut_test_code}        
        
        Screenshots:
        - Before: screenshots/before_{page_name}.png
        - After: screenshots/after_{page_name}.png
        
        Requirements:
        - Title: Final QA Report for {page_name} Page
        - Section for functional spec (briefly summarize)
        - Section for test strategy (based on the script)
        - Mention test inputs (e.g., username/password if used)
        - Screenshot references
        - Final summary/observations
        
        Output only valid Markdown.
"""