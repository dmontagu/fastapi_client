FROM python:3.7

RUN pip install black isort autoflake httpx fastapi typing_extensions
ADD scripts/_postprocess-docker.sh /
ENTRYPOINT ["/_postprocess-docker.sh"]