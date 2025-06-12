import os
import subprocess
import shutil
from logger import logging

def clone_repo_from_url(repo_url, target_dir="repo"):
    """
    Clone the GitHub repository from the given URL to the target directory.
    If the target directory already exists, do nothing.
    """
    logging.info("Started cloning the repository from the provided URL...")

    if os.path.exists(target_dir):
        logging.info(f"Target directory '{target_dir}' already exists. Skipping clone.")
        return  

    try:
        subprocess.run(["git", "clone", repo_url, target_dir], check=True)
        logging.info(f"Repository cloned successfully into '{target_dir}'.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error occurred while cloning the repository: {e}")
        raise
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        raise

    logging.info("Finished cloning the repository.")


# if __name__ == "__main__":
#     repo_url = "https://github.com/devmahmud/Django-Poll-App"
#     try:
#         clone_repo_from_url(repo_url)
#     except Exception as e:
#         print(f"Failed to clone repository: {e}")