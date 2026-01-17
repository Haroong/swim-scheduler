# SwimParser

성남시 수영장 자유수영 정보 수집기 (MVP)

성남시청소년청년재단 수영장 공지 게시판에서 자유수영 관련 정보를 자동으로 수집하는 크롤러입니다.

## 기능

- 게시판에서 "수영" 키워드 포함 게시글 자동 수집
- 상세 페이지에서 첨부파일(HWP) 다운로드
- HWP 파일에서 텍스트 추출
- 정규화된 JSON 형식으로 데이터 저장

## 설치

```bash
pip install -r requirements.txt
```

## 실행

```bash
python main.py
```

## 프로젝트 구조

```
project/
├── crawler/
│   ├── list_crawler.py         # 게시글 목록 수집
│   ├── detail_crawler.py       # 상세 페이지 파싱
│   └── attachment_downloader.py # 첨부파일 다운로드
├── parser/
│   └── hwp_text_extractor.py   # HWP 텍스트 추출
├── models/
│   └── swim_program.py         # 데이터 모델
├── storage/
│   └── raw_data/               # 다운로드된 첨부파일
├── main.py                     # 메인 실행 파일
└── requirements.txt
```

## 출력

수집된 데이터는 `storage/swim_programs.json` 파일에 저장됩니다.

```json
{
  "pool_name": "중원유스센터",
  "program_type": "자유수영",
  "raw_text": "추출된 텍스트...",
  "source_url": "https://...",
  "notice_title": "게시글 제목",
  "notice_date": "2026-01-16",
  "attachment_filename": "파일명.hwp",
  "created_at": "2026-01-16T..."
}
```

## 크롤링 대상

- URL: https://www.snyouth.or.kr/fmcs/289
- 키워드: "수영" (자유수영 포함)

## 주의사항

- 서버 부하 방지를 위해 요청 간 0.5초 딜레이 적용
- HWP 파일이 없는 경우 본문 텍스트를 대신 저장
- 파싱 실패 시 에러 없이 스킵 (로그 기록)
