# ===== Build Stage =====
FROM python:3.11-slim AS builder

WORKDIR /app

# 빌드 도구 설치
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

# 의존성 파일 복사
COPY requirements/ requirements/

# 패키지 빌드 (--user로 /root/.local에 설치)
RUN pip install --no-cache-dir --user -r requirements/prod.txt

# ===== Production Stage =====
FROM python:3.11-slim

WORKDIR /app

# 빌드된 패키지만 복사 (gcc 제외)
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# 소스 코드 복사
COPY . .

ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Seoul

CMD ["python", "scheduler.py"]
