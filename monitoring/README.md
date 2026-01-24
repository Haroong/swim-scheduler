# 모니터링 시스템 사용 가이드

이 디렉토리는 swim-scheduler 프로젝트의 로그 및 메트릭 모니터링을 위한 Loki, Prometheus, Grafana 설정을 포함합니다.

## 📊 구성 요소

### 1. Loki (로그 수집)
- **포트**: 3100
- **용도**: Parser 서비스의 로그 수집 및 저장
- **보존 기간**: 31일

### 2. Prometheus (메트릭 수집)
- **포트**: 9090
- **용도**: Parser 및 API 서비스의 성능 메트릭 수집
- **수집 주기**: 15초

### 3. Grafana (통합 대시보드)
- **포트**: 3001
- **기본 계정**: admin / admin
- **기능**: 로그 + 메트릭 통합 조회 및 시각화

## 🚀 시작하기

### 1. 모니터링 스택 실행

```bash
# 전체 스택 실행
docker-compose up -d

# 모니터링 서비스만 실행
docker-compose up -d loki prometheus grafana
```

### 2. 프로덕션 환경에서 Loki 활성화

`.env` 파일에 다음 설정 추가:

```env
ENV=prod
LOKI_ENABLED=true
LOKI_URL=http://loki:3100/loki/api/v1/push
```

### 3. Grafana 접속

브라우저에서 http://localhost:3001 접속
- 사용자: `admin`
- 비밀번호: `.env`의 `GRAFANA_PASSWORD` 값

## 📈 사용 방법

### Loki에서 로그 조회

Grafana에서 "Explore" 메뉴 선택 후:

```logql
# 모든 파서 로그 조회
{application="swim-scheduler-parser"}

# 에러 로그만 조회
{application="swim-scheduler-parser"} |= "ERROR"

# 특정 시설 로그 조회
{application="swim-scheduler-parser"} |= "중원유스센터"

# 파싱 성공 로그 필터링
{application="swim-scheduler-parser"} |= "파싱 성공"

# JSON 필드로 필터링
{application="swim-scheduler-parser"} | json | level="ERROR"
```

### Prometheus에서 메트릭 조회

```promql
# 파싱 성공률
rate(parser_success_total[5m]) / (rate(parser_success_total[5m]) + rate(parser_failed_total[5m]))

# 평균 파싱 시간
rate(parser_duration_seconds_sum[5m]) / rate(parser_duration_seconds_count[5m])

# 시설별 처리 건수
sum by (facility) (parser_success_total)
```

## 🎯 대시보드 생성

### 로그 대시보드 예시

1. Grafana에서 "+" → "Dashboard" 클릭
2. "Add visualization" 선택
3. 데이터 소스: Loki
4. 쿼리 입력:
   ```logql
   {application="swim-scheduler-parser"} |= "파싱"
   ```

### 메트릭 대시보드 예시

1. 새 패널 추가
2. 데이터 소스: Prometheus
3. 쿼리 입력:
   ```promql
   rate(parser_success_total[5m])
   ```

## 🔍 일반적인 쿼리 예제

### 최근 에러 로그 확인
```logql
{application="swim-scheduler-parser"} |= "ERROR" | json | line_format "{{.timestamp}} {{.message}}"
```

### 시간대별 파싱 건수
```logql
count_over_time({application="swim-scheduler-parser"} |= "파싱 성공"[1h])
```

### 시설별 로그 분리
```logql
{application="swim-scheduler-parser"} | json | facility="중원유스센터"
```

## 🛠 설정 파일

### loki-config.yml
Loki의 저장소 및 보존 정책 설정

### prometheus.yml
메트릭 수집 대상 및 주기 설정

### grafana/provisioning/
- `datasources/`: Loki, Prometheus 자동 연결
- `dashboards/`: 대시보드 자동 프로비저닝

## 📝 로그 포맷

Parser에서 생성하는 로그는 JSON 형식:

```json
{
  "timestamp": "2026-01-24T12:34:56",
  "level": "INFO",
  "logger": "swim_parser",
  "message": "DB 저장 성공",
  "module": "parsing_service",
  "function": "parse_and_save",
  "line": 120,
  "extra": {
    "facility": "중원유스센터",
    "schedules_count": 5,
    "source_url": "https://..."
  }
}
```

## 🔧 트러블슈팅

### Loki에 로그가 안 보일 때

1. Parser 환경변수 확인:
   ```bash
   docker exec swim-scheduler-parser env | grep LOKI
   ```

2. Loki 컨테이너 로그 확인:
   ```bash
   docker logs swim-scheduler-loki
   ```

3. 네트워크 연결 확인:
   ```bash
   docker exec swim-scheduler-parser ping loki
   ```

### Prometheus에 메트릭이 안 보일 때

1. Parser가 메트릭을 expose하는지 확인:
   ```bash
   curl http://localhost:8001/metrics
   ```

2. Prometheus targets 확인:
   - http://localhost:9090/targets 접속

## 📚 추가 자료

- [Loki LogQL 문서](https://grafana.com/docs/loki/latest/logql/)
- [Prometheus PromQL 문서](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Grafana 대시보드 문서](https://grafana.com/docs/grafana/latest/dashboards/)

## 💡 팁

1. **개발 환경**: Loki 비활성화, 콘솔 로그만 사용
2. **프로덕션**: Loki 활성화, JSON 포맷으로 로그 수집
3. **로그 레벨**: 프로덕션에서는 INFO 이상만 수집하여 디스크 절약
4. **알림 설정**: Grafana Alerting으로 에러 발생 시 알림 설정 가능
