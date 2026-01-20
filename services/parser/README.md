# Swim Scheduler Parser

성남시 수영장 자유수영 정보 자동 수집 시스템

## 개요

성남시청소년청년재단(SNYOUTH) 및 성남도시개발공사(SNHDC) 수영장의 자유수영 정보를 자동으로 크롤링하고, LLM을 사용하여 파싱한 후 DB에 저장하는 파이프라인입니다.

**파이프라인**: 크롤링 → LLM 파싱 → DB 저장

## 주요 기능

- ✅ 다중 기관 지원 (SNYOUTH, SNHDC)
- ✅ 게시판 자동 크롤링 (키워드 검색)
- ✅ 첨부파일 다운로드 (HWP, PDF)
- ✅ LLM 기반 자동 파싱 (Claude API)
- ✅ 구조화된 데이터 저장 (MariaDB)
- ✅ 환경별 설정 관리 (dev/staging/prod)
- ✅ 중앙 집중식 로깅

## 프로젝트 구조

```
services/parser/
├── config/                      # 설정 관리
│   ├── __init__.py
│   ├── settings.py              # Pydantic Settings
│   └── logging_config.py        # 로깅 설정
├── crawler/                     # 크롤러
│   ├── base/                    # 베이스 크롤러
│   ├── snhdc/                   # 성남도시개발공사
│   ├── snyouth/                 # 성남시청소년청년재단
│   └── factory.py               # Crawler Factory
├── llm/                         # LLM 파서
│   ├── llm_parser.py
│   └── prompts.py
├── database/                    # DB 관리
│   ├── connection.py
│   └── repository.py
├── services/                    # 비즈니스 로직
│   ├── crawling_service.py
│   ├── parsing_service.py
│   └── swim_crawler_service.py
├── dto/                         # Data Transfer Objects
├── domain/                      # Domain Entities
├── extractors/                  # 파일 추출기 (HWP, PDF)
├── utils/                       # 유틸리티
├── requirements/                # 의존성 관리
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt
├── main.py                      # 메인 실행 파일
└── README.md
```

## 설치 및 설정

### 1. 의존성 설치

**개발 환경**:
```bash
pip install -r requirements/dev.txt
```

**프로덕션 환경**:
```bash
pip install -r requirements/prod.txt
```

### 2. 환경 설정

환경별 `.env` 파일 생성:

**개발 환경** (`.env.dev`):
```bash
cp .env.dev.example .env.dev
# 또는
cp .env.dev.example .env
```

**프로덕션 환경** (`.env.prod`):
```bash
cp .env.prod.example .env.prod
# 또는
cp .env.prod.example .env
```

### 3. 필수 환경변수 설정

`.env` 파일에서 다음 값을 설정:

```bash
# LLM API Key (필수)
ANTHROPIC_API_KEY=sk-ant-xxxxx

# Database 설정 (필수)
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=swim_scheduler_dev

# 환경 선택 (선택, 기본: dev)
ENV=dev
```

## 실행 방법

### 전체 파이프라인 실행

```bash
python main.py
```

### 단계별 실행

**1. 크롤링만 실행**:
```bash
python main.py --crawl --keyword "수영" --max-pages 5
```

**2. 파싱만 실행**:
```bash
python main.py --parse --max-files 10
```

**3. DB 저장만 실행**:
```bash
python main.py --save
```

### 기본 스케줄 DB 저장

```bash
python save_base_schedules_to_db.py
```

## 설정 시스템

### 환경별 설정

프로젝트는 3가지 환경을 지원합니다:

- `dev`: 개발 환경 (기본값)
- `staging`: 스테이징 환경
- `prod`: 프로덕션 환경

환경 변수 `ENV`로 제어:
```bash
ENV=prod python main.py
```

### 주요 설정 항목

| 설정 | 기본값 | 설명 |
|------|--------|------|
| `ENV` | dev | 환경 (dev/staging/prod) |
| `DEBUG` | true | 디버그 모드 |
| `LOG_LEVEL` | INFO | 로그 레벨 |
| `LOG_FORMAT` | json | 로그 포맷 (json/text) |
| `CRAWL_MAX_PAGES` | 5 | 최대 크롤링 페이지 수 |
| `CRAWL_MAX_FILES` | 10 | 최대 파싱 파일 수 |
| `HTTP_MAX_RETRIES` | 3 | HTTP 재시도 횟수 |

전체 설정 목록: `config/settings.py` 참조

## 로깅

### 로그 레벨

- `DEBUG`: 상세 디버그 정보
- `INFO`: 일반 정보 메시지
- `WARNING`: 경고 메시지
- `ERROR`: 에러 메시지
- `CRITICAL`: 치명적 오류

### 로그 출력 형식

**개발 환경** (text):
```
[INFO    ] 2026-01-20 20:00:00 crawler.snhdc       크롤링 완료: 10개
```

**프로덕션 환경** (json):
```json
{"timestamp":"2026-01-20T20:00:00","level":"INFO","logger":"crawler.snhdc","message":"크롤링 완료: 10개"}
```

### 로그 파일

로그 파일은 `logs/` 디렉토리에 저장됩니다:
- 파일명: `swim-scheduler-parser.log`
- 로테이션: 10MB마다 백업 (최대 5개 보관)

## 데이터베이스

### 스키마

주요 테이블:
- `facility`: 시설 정보
- `notice`: 공지사항
- `swim_schedule`: 수영 스케줄
- `swim_session`: 세션 정보
- `fee`: 이용료

### 마이그레이션

```bash
# JSON 데이터를 DB로 마이그레이션
python -c "from database.repository import SwimRepository; SwimRepository().migrate_from_json()"
```

## 지원 기관

### 성남시청소년청년재단 (SNYOUTH)
- 중원유스센터
- 판교청소년수련관
- 야탑청소년수련관

### 성남도시개발공사 (SNHDC)
- 단대체육관
- 수정체육관
- 중원체육관
- 판교체육관
- 분당체육관

## 트러블슈팅

### 1. DB 연결 실패
```bash
# DB 설정 확인
cat .env | grep DB_

# MariaDB 연결 테스트
mysql -h localhost -u root -p swim_scheduler_dev
```

### 2. LLM API 키 오류
```bash
# API 키 확인
cat .env | grep ANTHROPIC_API_KEY

# API 키 유효성 테스트
python -c "from config import settings; print(settings.ANTHROPIC_API_KEY[:10])"
```

### 3. 로그 확인
```bash
# 최근 로그 확인
tail -f logs/swim-scheduler-parser.log

# 에러 로그만 확인
grep ERROR logs/swim-scheduler-parser.log
```

## 개발 가이드

### 새로운 기관 추가

1. `crawler/{org_key}/` 디렉토리 생성
2. `list_crawler.py`, `detail_crawler.py`, `facility_info_crawler.py` 구현
3. `crawler/factory.py`에 등록:
   ```python
   CrawlerFactory.register("new_org", NewListCrawler, NewDetailCrawler, NewFacilityCrawler)
   ```

### 코드 스타일

```bash
# 포매팅
black .
isort .

# 린트
flake8 .

# 타입 체크
mypy .
```

## 라이선스

MIT License

## 문의

프로젝트 관련 문의: GitHub Issues
