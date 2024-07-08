# Use the latest official Python runtime as a parent image
FROM python:latest

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install any needed packages specified in requirements_docker.txt
RUN pip install --no-cache-dir -r requirements_docker.txt

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run api.py when the container launches with auto-reload enabled
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
