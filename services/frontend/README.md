# Swim Scheduler Frontend

성남시 수영장 자유수영 스케줄을 보여주는 React 기반 프론트엔드

## 기술 스택

- **React 18**: UI 라이브러리
- **TypeScript**: 타입 안전성
- **Vite**: 빌드 도구
- **React Router**: 라우팅
- **Axios**: HTTP 클라이언트

## 설치 및 실행

### 1. 의존성 설치

```bash
cd services/frontend
npm install
```

### 2. 환경 변수 설정

`.env.example`을 복사하여 `.env` 파일을 생성:

```bash
cp .env.example .env
```

### 3. 개발 서버 실행

```bash
npm run dev
```

개발 서버가 http://localhost:5173 에서 실행됩니다.

## 빌드

프로덕션 빌드:

```bash
npm run build
```

빌드 결과물은 `dist/` 디렉토리에 생성됩니다.

빌드 미리보기:

```bash
npm run preview
```

## 프로젝트 구조

```
services/frontend/
├── public/              # 정적 파일
├── src/
│   ├── components/      # 재사용 가능한 컴포넌트
│   ├── hooks/          # 커스텀 React 훅
│   ├── pages/          # 페이지 컴포넌트
│   │   └── ScheduleCalendar.tsx  # 스케줄 캘린더 페이지
│   ├── services/       # API 클라이언트
│   │   └── api.ts      # API 요청 함수
│   ├── types/          # TypeScript 타입 정의
│   │   └── schedule.ts # 스케줄 관련 타입
│   ├── App.tsx         # 메인 앱 컴포넌트
│   ├── App.css
│   ├── main.tsx        # 엔트리 포인트
│   └── index.css       # 글로벌 스타일
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── README.md
```

## 주요 기능

### 스케줄 캘린더

- 시설별 필터링
- 월별 필터링
- 스케줄 상세 정보 표시
- 이용료 정보
- 유의사항

## API 연동

백엔드 API와 통신하기 위해 Vite의 프록시 기능을 사용합니다.

`vite.config.ts`에서 설정:

```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
}
```

개발 환경에서 `/api/*` 요청은 자동으로 `http://localhost:8000/api/*`로 프록시됩니다.

## 개발 가이드

### 새 페이지 추가

1. `src/pages/`에 컴포넌트 생성
2. `src/App.tsx`에 라우트 추가

### 새 API 엔드포인트 추가

1. `src/types/schedule.ts`에 타입 정의
2. `src/services/api.ts`에 API 함수 추가
3. 컴포넌트에서 사용

### 스타일링

- 각 컴포넌트마다 `.css` 파일 사용
- 글로벌 스타일은 `index.css`에 정의
