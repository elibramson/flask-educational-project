#!/bin/bash

echo "Starting Flask Blog App Docker Deployment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Docker is not running. Please start Docker first."
    exit 1
fi

cleanup() {
    echo "🧹 Cleaning up..."
    docker-compose down
    docker stop flask-blog-alpine 2>/dev/null || true
    docker rm flask-blog-alpine 2>/dev/null || true
    docker system prune -f
}

build_and_run() {
    echo "🔨 Building Docker image..."
    
    # Try building with the main Dockerfile first
    if docker-compose build; then
        echo "Build successful!"
        echo "Starting containers..."
        if docker-compose up -d; then
            echo "Application started successfully!"
            echo "Your app is running at: http://localhost:8080"
            echo "To view logs: docker-compose logs -f"
            echo "To stop: docker-compose down"
        else
            echo "Failed to start containers"
            exit 1
        fi
    else
        echo "Main build failed. Trying Alpine alternative..."
        
        # Stop and remove existing Alpine container if it exists
        echo "Stopping existing Alpine container..."
        docker stop flask-blog-alpine 2>/dev/null || true
        docker rm flask-blog-alpine 2>/dev/null || true
        
        # Try building with Alpine Dockerfile
        if docker build -f Dockerfile.alpine -t flask-blog-alpine .; then
            echo "Alpine build successful!"
            echo "Starting Alpine container..."
            if docker run -d --name flask-blog-alpine -p 8080:5000 flask-blog-alpine; then
                echo "Alpine application started successfully!"
                echo "Your app is running at: http://localhost:8080"
                echo "To view logs: docker logs -f flask-blog-alpine"
                echo "To stop: docker stop flask-blog-alpine"
            else
                echo "Failed to start Alpine container"
                exit 1
            fi
        else
            echo "Both builds failed!"
            echo "Try these solutions:"
            echo "   1. Run: docker system prune -a"
            echo "   2. Restart Docker Desktop"
            echo "   3. Check your internet connection"
            exit 1
        fi
    fi
}

case "$1" in
    "build")
        echo "🔨 Building only..."
        docker-compose build
        ;;
    "build-alpine")
        echo "🔨 Building Alpine version..."
        docker stop flask-blog-alpine 2>/dev/null || true
        docker rm flask-blog-alpine 2>/dev/null || true
        docker build -f Dockerfile.alpine -t flask-blog-alpine .
        ;;
    "run")
        echo "Running existing image..."
        docker-compose up -d
        ;;
    "stop")
        echo "Stopping containers..."
        docker-compose down
        docker stop flask-blog-alpine 2>/dev/null || true
        docker rm flask-blog-alpine 2>/dev/null || true
        ;;
    "clean")
        cleanup
        ;;
    "logs")
        echo "Showing logs..."
        if docker ps | grep -q flask-blog-alpine; then
            docker logs -f flask-blog-alpine
        else
            docker-compose logs -f
        fi
        ;;
    "restart")
        echo "Restarting containers..."
        docker-compose restart
        docker restart flask-blog-alpine 2>/dev/null || true
        ;;
    *)
        build_and_run
        ;;
esac 