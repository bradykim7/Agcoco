# Agent 5: Consistency Check

두 데이터 스냅샷(MariaDB ↔ SQLite 등)을 비교해 불일치를 감지하고
구조화된 리포트를 생성하는 에이전트입니다.

## 설치

```bash
pip install anthropic
export ANTHROPIC_API_KEY="your-key-here"
```

## 실행

Python 3.10+와 `anthropic` 패키지, `ANTHROPIC_API_KEY`가 필요합니다. 아래 명령은 해당 에이전트 디렉터리에서 실행합니다. `--demo`도 실제 API를 호출합니다.

응답은 [공통 검증기](../shared/schema.py)로 필수 필드·중첩 타입·enum·추가 필드를 검사합니다. 위반하면 오류로 종료하며 결과 파일을 생성하거나 덮어쓰지 않습니다. 오프라인 검사는 저장소 루트에서 `python3 -B scripts/check-agent-regressions.py`로 실행합니다.

```bash
# 데모 (내장 샘플 데이터)
python agent.py --demo

# JSON 파일 비교
python agent.py \
  --source-a mariadb_snapshot.json \
  --source-b sqlite_snapshot.json \
  --key account_id

# 비교 필드 지정
python agent.py \
  --source-a a.json --source-b b.json \
  --key id \
  --fields email quota_mb status enabled

# 허용 오차 기준 포함
python agent.py \
  --source-a a.json --source-b b.json \
  --key id \
  --threshold "updated_at 60초 이내 차이는 무시"

# 결과를 파일로 저장
python agent.py --demo --output result.json
```

## 입력 형식

`--source-a` / `--source-b` 는 레코드 배열 형태의 JSON 파일을 받습니다.

```json
[
  {"account_id": "acct_001", "email": "alice@example.com", "quota_mb": 5120},
  {"account_id": "acct_002", "email": "bob@example.com",   "quota_mb": 2048}
]
```

## 출력 스키마

```json
{
  "summary": "string",
  "compared_sources": {
    "source_a": "string",
    "source_b": "string",
    "record_count_a": 0,
    "record_count_b": 0
  },
  "inconsistencies": [
    {
      "type": "field_value_mismatch",
      "severity": "high",
      "key": "string",
      "field": "string",
      "value_a": "string",
      "value_b": "string",
      "evidence": ["string"]
    }
  ],
  "statistics": {
    "total_checked": 0,
    "total_inconsistent": 0,
    "missing_in_source": 0,
    "missing_in_target": 0,
    "field_value_mismatch": 0
  },
  "open_questions": ["string"],
  "recommendations": ["string"]
}
```

## 불일치 유형

| 유형 | 설명 |
|------|------|
| `missing_in_source` | target에는 있지만 source에 없는 레코드 |
| `missing_in_target` | source에는 있지만 target에 없는 레코드 |
| `field_value_mismatch` | 두 소스에 레코드는 있지만 필드 값이 다름 |

## 심각도 기준

| 심각도 | 해당 케이스 |
|--------|-------------|
| `high` | email, 인증 관련 필드 불일치 |
| `medium` | quota_mb, status, enabled 등 비즈니스 핵심 필드 |
| `low` | 메타데이터, 표시 이름, 비핵심 카운터 |
