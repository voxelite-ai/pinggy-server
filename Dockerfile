FROM python:3.11.0

WORKDIR /app/

ENV VIRTUAL_ENV="/app/.venv"

RUN pip install uv

COPY requirements.txt .

RUN uv venv

RUN uv pip install --no-cache-dir -Ur requirements.txt --system
RUN uv pip install uvicorn --system

COPY . .

VOLUME ["/app/db"]

EXPOSE 8080

CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "4"]