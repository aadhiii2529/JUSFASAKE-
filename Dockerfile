FROM python:3.9-slim

# Install system dependencies for OpenCV and Shapely
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libgeos-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose port for the web dashboard
EXPOSE 5000

# Command to run the application
CMD ["python", "main.py"]
