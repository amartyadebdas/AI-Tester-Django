import os
import subprocess
import socket
import time
from logger import logging
from utils import clean_requirements_txt

def is_port_in_use(port):
    """
    Check if a given port is in use on localhost.
    Returns True if in use, False otherwise.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def free_port_8000():
    """
    Finds and removes any Docker containers using port 8000.
    This directly resolves port conflicts during docker run.
    """
    try:
        result = subprocess.run(
            ["sudo", "docker", "ps", "--format", "{{.ID}} {{.Ports}}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )

        containers = result.stdout.strip().splitlines()
        removed = False

        for line in containers:
            if "0.0.0.0:8000" in line or "[::]:8000" in line:
                container_id = line.split()[0]
                logging.info(f"Port 8000 in use by container {container_id}. Removing...")
                subprocess.run(["sudo", "docker", "rm", "-f", container_id], check=True)
                removed = True

        if removed:
            logging.info("Freed port 8000 by killing conflicting Docker containers.")
            time.sleep(2)
        else:
            logging.info("No Docker container found using port 8000.")

    except subprocess.CalledProcessError as e:
        logging.error(f"Error freeing port 8000: {e.stderr}")
        raise


def build_and_run_docker_container(target_dir="repo", image_name="fst_sandbox_app"):
    """
    Builds a Docker image from the specified directory, performs migrations, and runs the container.
    Automatically frees port 8000 if it's already in use by another Docker container.
    """
    logging.info("Preparing to build and run Docker container...")

    # Ensure port 8000 is free
    if is_port_in_use(8000):
        logging.info("Port 8000 is in use. Attempting to free it...")
        free_port_8000()
        time.sleep(3)
    else:
        logging.info("Port 8000 is free. Proceeding.")

    # Prepare absolute paths
    abs_target_dir = os.path.abspath(target_dir)
    db_path = os.path.join(target_dir, "db.sqlite3")
    abs_db_path = os.path.abspath(db_path)

    # Dockerfile content for building the image
    dockerfile_content = """
    FROM python:3.11-slim

    WORKDIR /app

    COPY . .

    RUN pip install --no-cache-dir -r requirements.txt

    EXPOSE 8000

    CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
    """

    dockerfile_path = os.path.join(target_dir, "Dockerfile")

    try:
        # Ensure database file exists
        if not os.path.exists(db_path):
            with open(db_path, "w"):
                pass
            logging.info(f"Created empty DB at {db_path}")

        # Write Dockerfile
        with open(dockerfile_path, "w") as f:
            f.write(dockerfile_content.strip())
        logging.info(f"Dockerfile written to {dockerfile_path}")

        # Clean requirements file
        requirements_path = os.path.join(target_dir, "requirements.txt")
        clean_requirements_txt(requirements_path)

        # Build the Docker image
        logging.info("Building Docker image...")
        subprocess.run(["sudo", "docker", "build", "--no-cache", "-t", image_name, target_dir], check=True)

        # Run Django migrations
        logging.info("Running Django migrations inside Docker...")
        subprocess.run([
            "sudo", "docker", "run", "--rm",
            "-v", f"{abs_target_dir}:/app",
            "-v", f"{abs_db_path}:/app/db.sqlite3",
            image_name,
            "python", "manage.py", "makemigrations"
        ], check=True)

        subprocess.run([
            "sudo", "docker", "run", "--rm",
            "-v", f"{abs_target_dir}:/app",
            "-v", f"{abs_db_path}:/app/db.sqlite3",
            image_name,
            "python", "manage.py", "migrate"
        ], check=True)

        # Run the actual container
        logging.info("Running Docker container...")
        subprocess.run([
            "sudo", "docker", "run", "-d",
            "-p", "8000:8000",
            "-v", f"{abs_target_dir}:/app",
            "-v", f"{abs_db_path}:/app/db.sqlite3",
            image_name
        ], check=True)

        # Optional: give it a moment to start up
        logging.info("Waiting briefly to let app start...")
        time.sleep(10)

        logging.info("Docker container started successfully.")

    except subprocess.CalledProcessError as e:
        logging.error(f"Docker command failed: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error during Docker build/run: {e}")
        raise





# if __name__ == "__main__":
#     target_dir = "repo"
#     image_name = "fst_sandbox_app"
#     try:
#         build_and_run_docker_container(target_dir, image_name)
#     except Exception as e:
#         print(f"Failed to build or run Docker container: {e}")