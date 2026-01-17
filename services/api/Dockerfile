FROM python:3.11-slim

WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Parser 의존성도 함께 설치 (database 모듈 공유를 위해)
COPY ../parser/requirements.txt parser-requirements.txt
COPY requirements.txt api-requirements.txt

RUN pip install --no-cache-dir -r parser-requirements.txt && \
    pip install --no-cache-dir -r api-requirements.txt

# Parser 소스 코드 복사 (database 모듈 공유)
COPY ../parser /app/parser

# API 소스 코드 복사
COPY . /app/api

WORKDIR /app/api

# 환경 변수
ENV PYTHONUNBUFFERED=1

# 포트 노출
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
