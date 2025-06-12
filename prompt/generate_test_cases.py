TEST_CASES = '''You are a senior QA automation engineer.

Write a standalone Python script using Selenium (not pytest) to test the `{page_name}` page of a Django web application.

Requirements:
- Use `webdriver.Chrome(options=options)` to set headless mode using `Options()` (not `chrome_options`)
- Use modern Selenium 4 syntax: `driver.find_element(By.XPATH, '...')`
- Load the page from: http://localhost:8000{path}
- Take a screenshot before interacting with the form and save it as: screenshots/before_{page_name}.png
- Fill in the form fields with test data
- Submit the form using the correct button
- Wait for 3 seconds after submission
- Take a screenshot after submission and save it as: screenshots/after_{page_name}.png
- Print the screenshot file paths and the first 300 characters of the final HTML
- Use a try-finally block to ensure `driver.quit()` is always called
- Include all necessary imports
- Wrap execution logic under: `if __name__ == "__main__"`
- Output only valid Python code, no markdown or explanations
- This is the page HTML content:
{html_content}'''