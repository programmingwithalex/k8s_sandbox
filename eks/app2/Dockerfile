FROM python:3.12-slim

WORKDIR /app

RUN pip install uv
COPY pyproject.toml .
RUN uv pip install --no-cache-dir -r pyproject.toml --system

# must match directory structure in eks/app2 to allow relative imports
COPY . /app/app2

CMD ["uvicorn", "app2.main:app", "--host", "0.0.0.0", "--port", "80"]
