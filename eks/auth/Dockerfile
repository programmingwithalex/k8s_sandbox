FROM python:3.12-slim

WORKDIR /app

RUN pip install uv
COPY pyproject.toml .
RUN uv pip install --no-cache-dir -r pyproject.toml --system

# must match directory structure in eks/auth to allow relative imports
COPY . /app/auth

CMD ["uvicorn", "auth.main:app", "--host", "0.0.0.0", "--port", "80"]
