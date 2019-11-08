FROM python:3.7-slim

RUN apt-get update && apt-get install -y build-essential
RUN pip install black autoflake isort httpx fastapi typing_extensions
ADD scripts/util/postprocess-docker.sh /
ENTRYPOINT ["/postprocess-docker.sh"]
