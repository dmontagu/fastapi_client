FROM python:3.7-slim

RUN apt-get update && apt-get install -y build-essential dos2unix
RUN pip install black autoflake isort httpx fastapi typing_extensions python-multipart uvicorn[standard]
ADD scripts/util/postprocess-docker.sh /

# Fix EOL in case the Docker build process runs on Windows
RUN dos2unix /postprocess-docker.sh

ENTRYPOINT ["/postprocess-docker.sh"]
