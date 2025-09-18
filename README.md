### How to set enviroment

```sh
pip install uv

uv sync 

uv run fastapi dev ./src/main.py
```

### Using Docker 🐋
1. Build Docker image from `Dockerfile`
```sh
docker build -t canyouregmyex-api-image .
```

2. Run the image
```sh
docker run -d -p 8000:8000 --name <container-name> canyouregmyex-api-image
```

3. Verify that container is running
```sh
docker ps
```