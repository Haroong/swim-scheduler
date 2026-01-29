FROM python:3.11-slim

WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    gcc curl \
    && rm -rf /var/lib/apt/lists/*

# Parser 의존성 복사 (디렉토리 전체 - base.txt 참조 때문)
COPY parser/requirements/ /app/parser-requirements/
COPY api/requirements.txt api-requirements.txt

# 의존성 설치
RUN pip install --no-cache-dir -r /app/parser-requirements/prod.txt && \
    pip install --no-cache-dir -r api-requirements.txt

# Parser 소스 코드 복사 (database 모듈 공유)
COPY parser /app/parser

# API 소스 코드 복사
COPY api /app/api

WORKDIR /app/api

# 환경 변수
ENV PYTHONUNBUFFERED=1

# 포트 노출
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
