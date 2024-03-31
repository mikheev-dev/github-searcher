FROM python:3.10.11
RUN pip install poetry
WORKDIR /app

COPY ./pyproject.toml /app/
RUN poetry install

COPY . /app
CMD ["poetry", "run", "uvicorn", "github_searcher.app:app", "--host", "0.0.0.0", "--port", "8000"]