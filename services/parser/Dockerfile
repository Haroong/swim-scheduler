FROM python:3.11-slim

WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements/ requirements/
RUN pip install --no-cache-dir -r requirements/prod.txt

# 소스 코드 복사
COPY . .

# 환경 변수
ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Seoul

# 스케줄러 실행 (매일 자정 자동 크롤링)
CMD ["python", "scheduler.py"]
