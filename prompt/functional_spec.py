SPEC_EXTRACTOR = '''
You're a senior software architect.

        From the HTML source of a Django-based homepage provided below, generate a clear and concise **functional specification** in Markdown format.

        Your output must contain ONLY the following sections in this order:

        ## User Interaction Flows
        - Describe the user's journey in exactly 4-6 short steps.
        - Start from homepage → register → login → and so on.
        - Include the route (`/path/`) in backticks inside each step.

        ## URL Endpoints and their Purpose
        - List each endpoint in the order it appears in the user flow.
        - Use this exact format:
          **Name (`/url/`)** — one-line purpose of that endpoint.

        Be direct and simple. Avoid repeating "Navigation", "Interface", or "Page" unless necessary. Avoid generic headings like "Navigation Bar Access".

        HTML Source:
        {html_source}
'''