# Swim Scheduler API

성남시 수영장 자유수영 스케줄 데이터를 제공하는 FastAPI 기반 REST API

## 기능

- 시설 목록 조회
- 스케줄 조회 (시설명, 월별 필터링)
- 달력 형식 스케줄 조회

## 기술 스택

- **FastAPI**: 고성능 비동기 웹 프레임워크
- **Pydantic**: 데이터 검증 및 스키마 정의
- **PyMySQL**: MariaDB 연결
- **Uvicorn**: ASGI 서버

## 설치 및 실행

### 1. 의존성 설치

```bash
cd services/api
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env.example`을 복사하여 `.env` 파일을 생성하고 실제 값으로 수정:

```bash
cp .env.example .env
```

### 3. API 서버 실행

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API 엔드포인트

### 시설 목록 조회

```http
GET /api/facilities
```

**응답 예시:**
```json
[
  {
    "facility_name": "야탑유스센터",
    "latest_month": "2026년 1월",
    "schedule_count": 15
  }
]
```

### 스케줄 조회

```http
GET /api/schedules?facility=야탑유스센터&month=2026-01
```

**쿼리 파라미터:**
- `facility` (선택): 시설명
- `month` (선택): 월 (형식: `2026-01` 또는 `2026년 1월`)

**응답 예시:**
```json
[
  {
    "id": 1,
    "facility_name": "야탑유스센터",
    "valid_month": "2026년 1월",
    "schedules": [
      {
        "day_type": "평일",
        "season": "동절기",
        "season_months": "11~2월",
        "sessions": [
          {
            "session_name": "자유수영",
            "start_time": "06:00",
            "end_time": "07:50",
            "capacity": 50,
            "lanes": 5
          }
        ]
      }
    ],
    "fees": [
      {
        "category": "성인",
        "price": 3000,
        "note": "1회 입장"
      }
    ],
    "notes": ["수영모 착용 필수"],
    "source_url": "https://...",
    "created_at": "2026-01-17T12:00:00"
  }
]
```

### 달력용 스케줄 조회

```http
GET /api/schedules/calendar?year=2026&month=1
```

**쿼리 파라미터:**
- `year` (필수): 년도
- `month` (필수): 월 (1-12)

## 개발

### 프로젝트 구조

```
services/api/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 앱 초기화
│   ├── database/
│   │   ├── __init__.py
│   │   └── connection.py       # DB 연결 (parser 모듈 재사용)
│   ├── routes/
│   │   ├── __init__.py
│   │   └── schedules.py        # 스케줄 API 엔드포인트
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── schedule.py         # Pydantic 스키마
│   └── services/
│       ├── __init__.py
│       └── schedule_service.py # 비즈니스 로직
├── .env.example
├── requirements.txt
└── README.md
```

### API 문서

서버 실행 후 다음 URL에서 자동 생성된 API 문서 확인 가능:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 헬스체크

```http
GET /health
```

## 데이터베이스 연결

이 API는 parser 서비스와 동일한 MariaDB를 사용합니다.
`app/database/connection.py`에서 parser의 DB 모듈을 재사용합니다.

## CORS 설정

기본적으로 다음 origins를 허용합니다:
- http://localhost:3000 (React 개발 서버)
- http://localhost:5173 (Vite 개발 서버)

추가 origins가 필요한 경우 `.env` 파일의 `CORS_ORIGINS`를 수정하세요.
