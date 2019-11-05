FROM python:3.7-slim

RUN pip install black autoflake isort httpx fastapi typing_extensions
ADD scripts/util/postprocess-docker.sh /
ENTRYPOINT ["/postprocess-docker.sh"]
