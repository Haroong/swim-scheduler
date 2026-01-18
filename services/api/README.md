# Swim Scheduler API

성남시 수영장 자유수영 스케줄 데이터를 제공하는 FastAPI 기반 REST API

## 개요

이 API는 성남시 내 수영장의 자유수영 스케줄 정보를 제공합니다. 크롤러가 수집한 데이터를 JSON 파일과 MariaDB에서 조회하여 RESTful API로 제공합니다.

## 기능

### DB 기반 엔드포인트
- 시설 목록 조회
- 스케줄 조회 (시설명, 월별 필터링)
- 달력 형식 스케줄 조회

### JSON 파일 기반 엔드포인트 (NEW!)
- 공지사항 목록 조회 (조직, 시설, 첨부파일 여부로 필터링)
- 공지사항 요약 정보
- LLM으로 파싱된 첨부파일 데이터 조회
- 시설 기본 스케줄 조회 (공식 이용안내 페이지 기반)

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

### 기본 엔드포인트

#### `GET /`
API 정보 반환

**응답:**
```json
{
  "message": "Swim Scheduler API",
  "docs": "/docs",
  "version": "1.0.0"
}
```

#### `GET /health`
헬스 체크

**응답:**
```json
{
  "status": "healthy"
}
```

---

### 스케줄 관련 엔드포인트 (DB 기반)

#### `GET /api/facilities`
시설 목록 조회

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

#### `GET /api/schedules`
스케줄 조회

**쿼리 파라미터:**
- `facility` (선택): 시설명
- `month` (선택): 월 (형식: `2026-01` 또는 `2026년 1월`)

**예시:**
```bash
curl "http://localhost:8000/api/schedules?facility=야탑유스센터&month=2026-01"
```

**응답 예시:**
```json
[
  {
    "id": 1,
    "facility_name": "야탑유스센터",
    "valid_month": "2026년 1월",
    "schedules": [...],
    "fees": [...],
    "notes": ["수영모 착용 필수"],
    "source_url": "https://...",
    "created_at": "2026-01-17T12:00:00"
  }
]
```

#### `GET /api/schedules/calendar`
달력용 스케줄 조회

**쿼리 파라미터:**
- `year` (필수): 년도
- `month` (필수): 월 (1-12)

**예시:**
```bash
curl "http://localhost:8000/api/schedules/calendar?year=2026&month=1"
```

---

### 데이터 관련 엔드포인트 (JSON 파일 기반)

#### `GET /api/notices/summary`
공지사항 요약 정보

**예시:**
```bash
curl http://localhost:8000/api/notices/summary
```

**응답:**
```json
{
  "total_count": 60,
  "by_organization": {
    "snyouth": 40,
    "snhdc": 20
  },
  "by_facility": {
    "판교유스센터": 10,
    "탄천종합운동장": 5
  }
}
```

#### `GET /api/notices`
공지사항 목록 조회

**쿼리 파라미터:**
- `organization` (선택): 조직 ("snyouth" 또는 "snhdc")
- `facility` (선택): 시설명
- `has_attachment` (선택): 첨부파일 여부 (true/false)
- `limit` (선택): 최대 반환 개수 (1-100)

**예시:**
```bash
# 최근 3개 공지사항
curl "http://localhost:8000/api/notices?limit=3"

# SNHDC 공지사항 중 첨부파일 있는 것만
curl "http://localhost:8000/api/notices?organization=snhdc&has_attachment=true"
```

**응답 예시:**
```json
[
  {
    "facility_name": "판교스포츠센터",
    "title": "수영장 운영 안내",
    "date": "2026-01-15 17:17:11",
    "detail_url": "https://...",
    "notice_id": "0002119",
    "has_attachment": true,
    "file_hwp": "파일명.hwp",
    "file_pdf": "파일명.pdf",
    "file_etc": null,
    "organization": "snhdc"
  }
]
```

#### `GET /api/parsed-attachments`
LLM으로 파싱된 첨부파일 조회

**쿼리 파라미터:**
- `facility` (선택): 시설명
- `month` (선택): 월 (예: "2026년 2월")

**예시:**
```bash
curl http://localhost:8000/api/parsed-attachments
```

**응답 예시:**
```json
{
  "meta": {
    "last_updated": "2026-01-18 15:21:36",
    "source": "SNHDC attachments (HWP/PDF)",
    "parsed_count": 2
  },
  "parsed_schedules": [
    {
      "facility_name": "평생학습관스포츠센터",
      "valid_month": "2026년 2월",
      "schedules": [...],
      "fees": [...],
      "notes": ["매월 2, 4주 일요일 및 공휴일 휴장"],
      "source_url": "https://spo.isdc.co.kr",
      "source_file": "파일명.hwp",
      "source_notice_title": "2월 운영프로그램 안내",
      "source_notice_date": "2026-01-15 09:31:30"
    }
  ]
}
```

#### `GET /api/base-schedules`
시설 기본 스케줄 조회 (공식 이용안내 페이지 기반)

**쿼리 파라미터:**
- `organization` (선택): 조직 ("snyouth" 또는 "snhdc")
- `facility` (선택): 시설명

**예시:**
```bash
curl "http://localhost:8000/api/base-schedules?organization=snyouth"
```

**응답 예시:**
```json
{
  "meta": {
    "last_updated": "2026-01-18 15:21:03",
    "version": "2.0",
    "total_facility_count": 7
  },
  "snyouth": [
    {
      "facility_name": "판교유스센터",
      "facility_url": "https://www.snyouth.or.kr/fmcs/133",
      "weekday_schedule": [...],
      "weekend_schedule": {...},
      "fees": {...},
      "notes": [...],
      "last_updated": "2026-01-18"
    }
  ]
}
```

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
│   │   ├── schedules.py        # 스케줄 API (DB 기반)
│   │   └── data.py             # 데이터 API (JSON 기반)
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── schedule.py         # Pydantic 스키마
│   └── services/
│       ├── __init__.py
│       ├── schedule_service.py # DB 기반 서비스
│       └── data_service.py     # JSON 기반 서비스
├── .venv/                      # 가상환경
├── requirements.txt
└── README.md
```

### 데이터 소스

API는 두 가지 데이터 소스를 사용합니다:

#### 1. JSON 파일 (../parser/storage/)
- `swim_programs.json`: 공지사항 목록 (60개)
- `snhdc_parsed_attachments.json`: LLM으로 파싱된 첨부파일 (2개)
- `facility_base_schedules.json`: 시설 기본 스케줄 (7개 시설)

#### 2. MariaDB
- `parsed_swim_schedules` 테이블: 파싱된 스케줄 데이터

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
