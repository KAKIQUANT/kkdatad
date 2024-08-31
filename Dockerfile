# Use Ubuntu as a parent image
FROM ubuntu:22.04

# Set the working directory in the container
WORKDIR /app

# Update the package list and install necessary packages
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy the entire project into the container's /app directory
COPY . .

# Install any dependencies specified in requirements.txt
RUN pip3 install --no-cache-dir .

# Expose the port FastAPI will run on
EXPOSE 8000

# Set environment variables for production
ENV PYTHONUNBUFFERED=1

# Command to run the FastAPI application using uvicorn
CMD ["uvicorn", "kkdatad.app:app", "--host", "0.0.0.0", "--port", "8000"]
