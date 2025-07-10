FROM python:3.12

RUN mkdir /candy_store

WORKDIR /candy_store

RUN pip install poetry

COPY pyproject.toml poetry.lock* README.md ./

RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-root

COPY . .

RUN apt-get update && apt-get install -y dos2unix && \
    dos2unix /candy_store/docker/*.sh && \
    chmod a+x /candy_store/docker/*.sh

CMD ["poetry", "run", "gunicorn", "app.main:app", "--workers", "1", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind=0.0.0.0:8000"]