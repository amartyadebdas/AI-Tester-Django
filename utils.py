# from logger import logging
# import os 

# def clean_requirements_txt(path):
#     logging.info(f"Cleaning the {path} to remove invalid quotes.")
#     try:
#         with open(path, "r") as f:
#             lines = f.readlines()

#         cleaned = [line.replace('"', '').replace("'", '') for line in lines]

#         with open(path, "w") as f:
#             f.writelines(cleaned)

#         logging.info(f"Cleaned {path} to remove invalid quotes.")
#     except Exception as e:
#         logging.error(f"Failed to clean {path}: {e}")
#         raise


# utils.py
import re
import os
from logger import logging

def clean_requirements_txt(requirements_path: str):
    """
    Reads a requirements.txt file, removes version specifiers (like ==, >=, <, <=, !=, ~~)
    and invalid quotes, then writes the cleaned content back to the same file.

    Args:
        requirements_path (str): The full path to the requirements.txt file.
    """
    if not os.path.exists(requirements_path):
        logging.warning(f"requirements.txt not found at '{requirements_path}'. Skipping cleaning.")
        return

    logging.info(f"Cleaning requirements.txt at: {requirements_path} (removing versions and quotes).")
    cleaned_lines = []
    try:
        with open(requirements_path, 'r') as f:
            for line in f:
                original_line = line.strip()
                if not original_line or original_line.startswith('#'): # Skip empty lines and comments
                    cleaned_lines.append(original_line)
                    continue

                # Step 1: Remove version specifiers and anything that follows them
                # This regex captures the package name (and optional extras like [socks])
                # and discards everything else on the line if it starts with a non-alphanumeric character
                # (like =, >, <, !, ~, or a space)
                # It also handles potential spaces after the package name before the version.
                match = re.match(r'([a-zA-Z0-9._-]+(?:\[.*?\])?)\s*(?:[<=>!~].*|$)', original_line)
                if match:
                    # If a version specifier or anything after package name is found, take only the package name
                    version_stripped_line = match.group(1).strip()
                else:
                    # If no version specifier is found, it's just the package name (or malformed)
                    version_stripped_line = original_line.strip()


                # Step 2: Remove invalid quotes (your original logic)
                final_cleaned_line = version_stripped_line.replace('"', '').replace("'", '')

                cleaned_lines.append(final_cleaned_line) # Already stripped, no need for .strip() again here

        with open(requirements_path, 'w') as f:
            # Add a newline character back for each line when writing
            for line in cleaned_lines:
                f.write(line + '\n')

        logging.info(f"Successfully cleaned requirements.txt: {requirements_path}")
    except Exception as e:
        logging.error(f"Error cleaning requirements.txt '{requirements_path}': {e}")
        raise # Re-raise to ensure the docker_runner catches it if critical