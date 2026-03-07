# EventBus Architecture

Parser 내부의 인프로세스 동기 이벤트 버스.
`save_to_db()`의 사이드 이펙트(알림, 캐시 무효화, 휴장 감지)를 핵심 로직에서 분리한다.

---

## 전체 흐름

```
save_to_db()
  │
  │  repo.save_parsed_data(data)   ← DB 저장 (핵심 로직)
  │
  └─ event_bus.publish(ScheduleSaved)
          │
          ├─► DiscordEventHandler.on_schedule_saved()
          │       └─ Discord 알림: 새 스케줄 저장
          │
          ├─► CacheEventHandler.on_schedule_saved()
          │       └─ Redis PUBLISH → API 캐시 무효화
          │
          └─► ClosureDetectionHandler.on_schedule_saved()
                  │  휴장 여부 판단
                  │
                  └─ event_bus.publish(PoolClosureDetected)
                          │
                          └─► DiscordEventHandler.on_pool_closure()
                                  └─ Discord 알림: 수영장 휴장
```

---

## 파일 구조

```
services/parser/
├── core/events/
│   ├── __init__.py          # EventBus, ScheduleSaved, PoolClosureDetected export
│   ├── event_bus.py         # EventBus 클래스 (subscribe / publish)
│   └── events.py            # 도메인 이벤트 dataclass 정의
│
├── application/
│   └── event_handlers.py    # DiscordEventHandler, CacheEventHandler, ClosureDetectionHandler
│
└── main.py                  # _create_event_bus()에서 조립, save_to_db()에서 사용
```

---

## 핵심 컴포넌트

### EventBus (`core/events/event_bus.py`)

```python
class EventBus:
    subscribe(event_type, handler)   # 이벤트 타입에 핸들러 등록
    publish(event)                   # 이벤트 발행 → 등록된 핸들러 순차 실행
```

- **동기 실행**: 핸들러는 publish 호출 스레드에서 즉시 실행
- **Fail-safe**: 핸들러 예외 시 로그만 남기고 다음 핸들러 계속 실행
- **스코프**: `save_to_db()` 호출마다 새로 생성 (전역 싱글턴 아님)

### 도메인 이벤트 (`core/events/events.py`)

| 이벤트 | 필드 | 발행 시점 |
|--------|------|-----------|
| `ScheduleSaved` | `data`, `facility_name`, `valid_month` | DB에 새 스케줄 저장 후 |
| `PoolClosureDetected` | `facility_name`, `valid_month`, `reason`, `source_url` | 휴장 감지 시 |

### 이벤트 핸들러 (`application/event_handlers.py`)

| 핸들러 | 구독 이벤트 | 역할 |
|--------|-------------|------|
| `DiscordEventHandler` | `ScheduleSaved`, `PoolClosureDetected` | Discord Webhook 알림 |
| `CacheEventHandler` | `ScheduleSaved` | Redis Pub/Sub으로 API 캐시 무효화 |
| `ClosureDetectionHandler` | `ScheduleSaved` | 휴장 감지 → `PoolClosureDetected` 발행 |

---

## 와이어링 (`main.py:_create_event_bus()`)

```
ScheduleSaved ──────┬──► DiscordEventHandler.on_schedule_saved
                    ├──► CacheEventHandler.on_schedule_saved
                    └──► ClosureDetectionHandler.on_schedule_saved
                              │
PoolClosureDetected ────► DiscordEventHandler.on_pool_closure
```

핸들러 실행 순서는 `subscribe()` 호출 순서와 동일하다.

---

## 새 핸들러 추가 방법

1. `application/event_handlers.py`에 핸들러 클래스 추가
2. `main.py:_create_event_bus()`에서 `bus.subscribe()` 호출

`save_to_db()` 코드는 수정하지 않아도 된다.

```python
# 예: Slack 알림 핸들러 추가
class SlackEventHandler:
    def on_schedule_saved(self, event: ScheduleSaved) -> None:
        self._client.send(...)

# _create_event_bus()에 한 줄 추가
bus.subscribe(ScheduleSaved, slack_handler.on_schedule_saved)
```

---

## Fail-safe 동작

| 상황 | 결과 |
|------|------|
| Discord Webhook 실패 | 로그 경고, 캐시 무효화/휴장 감지는 정상 진행 |
| Redis 연결 불가 | 로그 경고, Discord 알림/휴장 감지는 정상 진행 |
| 핸들러 예외 발생 | EventBus가 catch, 다음 핸들러 계속 실행 |
| 모든 핸들러 실패 | DB 저장은 이미 완료됨 (핵심 로직에 영향 없음) |
