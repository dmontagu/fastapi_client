FROM python:3.9-slim-bullseye

RUN apt-get update && apt-get install -y build-essential dos2unix
RUN pip install black autoflake isort httpx fastapi typing_extensions
ADD scripts/util/postprocess-docker.sh /

# Fix EOL in case the Docker build process runs on Windows
RUN dos2unix /postprocess-docker.sh

ENTRYPOINT ["/postprocess-docker.sh"]
