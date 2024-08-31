# Variables
IMAGE_NAME = kkdatad
CONTAINER_NAME = kkdatad_container
PORT = 8000
DOCKER_DIR = docker

# Build the Docker image
build:
	docker build -t $(IMAGE_NAME) .

# Run the Docker container
run:
	docker run -d -p $(PORT):8000 --name $(CONTAINER_NAME) $(IMAGE_NAME)

# Stop the Docker container
stop:
	docker stop $(CONTAINER_NAME)

# Remove the Docker container
remove:
	docker rm $(CONTAINER_NAME)

# Clean up: Stop and remove the container
clean: stop remove

# Rebuild the image and run the container
rebuild: clean build run

# Tail logs from the container
logs:
	docker logs -f $(CONTAINER_NAME)
