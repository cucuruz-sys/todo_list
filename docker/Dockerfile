FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends git ca-certificates && \
    rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/cucuruz-sys/todo_list.git   . && \
    rm -rf .git

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8084

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8084"]