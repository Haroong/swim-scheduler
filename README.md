# Swim Scheduler

성남시 수영장 자유수영 스케줄 통합 시스템

## 📋 목차

- [프로젝트 개요](#프로젝트-개요)
- [프로젝트 구조](#프로젝트-구조)
- [서비스 설명](#서비스-설명)
- [시작하기](#시작하기)
- [개발 가이드](#개발-가이드)
- [API 문서](#api-문서)
- [기술 스택](#기술-스택)

## 프로젝트 개요

성남시청소년재단 수영장의 자유수영 스케줄을 자동으로 크롤링하고, LLM을 활용하여 구조화된 데이터로 변환한 후, 웹에서 쉽게 조회할 수 있도록 제공하는 풀스택 시스템입니다.

**주요 기능:**
- 자동 크롤링 및 데이터 추출 (HWP/PDF 파일 지원)
- Claude AI를 활용한 지능형 데이터 파싱
- RESTful API 제공
- 사용자 친화적인 웹 인터페이스

## 프로젝트 구조

```
swim-scheduler/                    # 모노레포 루트
├── services/
│   ├── parser/                   # 크롤러 & 데이터 파서
│   │   ├── crawler/              # 웹 크롤러
│   │   ├── parser/               # LLM 기반 파서
│   │   ├── database/             # DB 연결
│   │   ├── utils/                # 유틸리티
│   │   ├── main.py               # 메인 실행 파일
│   │   ├── requirements.txt
│   │   ├── Dockerfile
│   │   └── README.md
│   │
│   ├── api/                      # FastAPI 백엔드
│   │   ├── app/
│   │   │   ├── routes/           # API 엔드포인트
│   │   │   ├── services/         # 비즈니스 로직
│   │   │   ├── schemas/          # Pydantic 스키마
│   │   │   ├── database/         # DB 연결
│   │   │   └── main.py           # FastAPI 앱
│   │   ├── requirements.txt
│   │   ├── Dockerfile
│   │   └── README.md
│   │
│   └── frontend/                 # React 프론트엔드
│       ├── src/
│       │   ├── components/       # 재사용 컴포넌트
│       │   ├── pages/            # 페이지 컴포넌트
│       │   ├── services/         # API 클라이언트
│       │   ├── types/            # TypeScript 타입
│       │   └── App.tsx
│       ├── package.json
│       ├── Dockerfile
│       └── README.md
│
├── docker-compose.yml            # Docker 오케스트레이션
├── Makefile                      # 개발 편의 명령어
├── .env.example                  # 환경 변수 예시
├── .gitignore
└── README.md

```

## 서비스 설명

### 🕷️ Parser (크롤러 & 파서)

**역할:**
- 성남시청소년재단 홈페이지 공지사항 크롤링
- HWP/PDF 첨부파일 다운로드 및 텍스트 추출
- Claude API를 통한 LLM 기반 스케줄 데이터 파싱
- 날짜 검증을 통한 데이터 품질 보장
- MariaDB에 구조화된 데이터 저장
- **매일 자정(00:00 KST) 자동 실행** - APScheduler를 통한 자동 크롤링

**기술:**
- Python 3.11
- BeautifulSoup4 (웹 크롤링)
- Anthropic Claude API (LLM 파싱)
- PyMySQL (데이터베이스)

**자세한 내용:** [services/parser/README.md](services/parser/README.md)

### ⚡ API (백엔드)

**역할:**
- REST API 제공
- 시설별/월별 스케줄 조회
- 달력용 데이터 변환
- CORS 설정으로 프론트엔드 연동

**기술:**
- FastAPI (비동기 웹 프레임워크)
- Pydantic (데이터 검증)
- PyMySQL (데이터베이스)

**엔드포인트:**
- `GET /api/facilities` - 시설 목록
- `GET /api/schedules` - 스케줄 조회 (필터링 지원)
- `GET /api/schedules/calendar` - 달력 데이터
- `GET /health` - 헬스체크

**자세한 내용:** [services/api/README.md](services/api/README.md)

### 🎨 Frontend (프론트엔드)

**역할:**
- 사용자 친화적인 웹 인터페이스
- 시설별/월별 필터링
- 스케줄 상세 정보 표시
- 반응형 디자인

**기술:**
- React 18
- TypeScript
- Vite (빌드 도구)
- Axios (HTTP 클라이언트)

**자세한 내용:** [services/frontend/README.md](services/frontend/README.md)

## 시작하기

### 사전 요구사항

- Docker & Docker Compose (권장)
- 또는 로컬 개발:
  - Python 3.11+
  - Node.js 20+
  - MariaDB 11.2+

### 1. 환경 설정

```bash
# 저장소 클론
git clone <repository-url>
cd swim-scheduler

# 환경 변수 파일 생성
make init
# 또는 수동으로:
cp .env.example .env
cp services/api/.env.example services/api/.env
cp services/frontend/.env.example services/frontend/.env

# .env 파일 수정 (API 키, DB 비밀번호 등)
vi .env
```

### 2. Docker로 전체 스택 실행

```bash
# 빌드 및 실행
make build
make up

# 또는 한 번에:
docker-compose up --build

# 로그 확인
make logs
```

**접속:**
- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### 3. 개별 서비스 로컬 실행

#### Parser 실행

```bash
cd services/parser
python3.11 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements/dev.txt

# .env 파일 설정 후
# 자동 스케줄러 실행 (매일 자정 자동 크롤링)
python scheduler.py

# 또는 수동 실행 (1회)
python main.py
```

#### API 실행

```bash
cd services/api
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 개발 모드 실행
make api-dev
# 또는
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend 실행

```bash
cd services/frontend
npm install

# 개발 서버 실행
make frontend-dev
# 또는
npm run dev
```

## 개발 가이드

### Makefile 명령어

```bash
make help           # 사용 가능한 명령어 목록
make build          # Docker 이미지 빌드
make up             # 모든 서비스 시작
make down           # 모든 서비스 중지
make logs           # 로그 확인
make parser-run     # Parser 수동 실행
make api-dev        # API 개발 모드
make frontend-dev   # Frontend 개발 모드
make db-shell       # 데이터베이스 쉘 접속
make clean          # 컨테이너 및 볼륨 정리
```

### 데이터베이스 스키마

```sql
CREATE TABLE parsed_swim_schedules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    facility_name VARCHAR(255) NOT NULL,
    valid_month VARCHAR(50) NOT NULL,
    schedules JSON,
    fees JSON,
    notes JSON,
    source_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 코드 구조 및 패턴

**Parser:**
- `crawler/`: 웹 크롤링 및 파일 다운로드
- `parser/`: LLM 기반 파싱 로직
- `utils/`: 날짜 검증, 파일 처리 유틸리티

**API:**
- `routes/`: API 엔드포인트 정의 (컨트롤러)
- `services/`: 비즈니스 로직 (서비스 레이어)
- `schemas/`: Pydantic 모델 (데이터 검증)
- `database/`: DB 연결 관리

**Frontend:**
- `pages/`: 페이지 단위 컴포넌트
- `components/`: 재사용 가능한 컴포넌트
- `services/`: API 통신 로직
- `types/`: TypeScript 타입 정의

## API 문서

API 서버 실행 후 자동 생성된 문서 확인:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 기술 스택

### 백엔드
- **Python 3.11**: 메인 프로그래밍 언어
- **FastAPI**: 고성능 비동기 웹 프레임워크
- **Pydantic**: 데이터 검증 및 설정 관리
- **BeautifulSoup4**: 웹 크롤링
- **Anthropic Claude API**: LLM 기반 데이터 파싱
- **PyMySQL**: MariaDB 연결

### 프론트엔드
- **React 18**: UI 라이브러리
- **TypeScript**: 타입 안전성
- **Vite**: 빌드 도구
- **Axios**: HTTP 클라이언트
- **React Router**: 라우팅

### 인프라
- **MariaDB 11.2**: 관계형 데이터베이스
- **Docker & Docker Compose**: 컨테이너화
- **Nginx**: 프론트엔드 서빙 및 리버스 프록시

## 라이센스

MIT
