# ===== Build Stage =====
FROM python:3.11-slim AS builder

WORKDIR /app

# 빌드 도구 설치
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

# 의존성 파일 복사
COPY parser/requirements/ /app/parser-requirements/
COPY api/requirements.txt api-requirements.txt

# 패키지 빌드 (--user로 /root/.local에 설치)
RUN pip install --no-cache-dir --user -r /app/parser-requirements/prod.txt && \
    pip install --no-cache-dir --user -r api-requirements.txt

# ===== Production Stage =====
FROM python:3.11-slim

WORKDIR /app

# curl만 설치 (healthcheck용)
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# 빌드된 패키지만 복사 (gcc 제외)
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# 소스 코드 복사
COPY parser /app/parser
COPY api /app/api

WORKDIR /app/api

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
