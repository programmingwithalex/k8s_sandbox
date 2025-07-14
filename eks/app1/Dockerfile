FROM python:3.12-slim

WORKDIR /app

RUN pip install uv
COPY pyproject.toml .
RUN uv pip install --no-cache-dir -r pyproject.toml --system

# must match directory structure in eks/app1 to allow relative imports
COPY . /app/app1

CMD ["uvicorn", "app1.main:app", "--host", "0.0.0.0", "--port", "80"]
