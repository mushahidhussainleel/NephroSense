# Use the official lightweight Python 3.11 image as the base image
FROM python:3.11-slim

# Set the working directory inside the Docker container
WORKDIR /app

# Copy the requirements file first to improve Docker layer caching
COPY requirements.txt .

# Install all Python dependencies listed in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the remaining application files into the container
COPY . .

# Expose port 8000 for the FastAPI application
EXPOSE 8000

# Start the FastAPI application using Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]