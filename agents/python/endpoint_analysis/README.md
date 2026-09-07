# Agent 2: Endpoint Analysis

API 엔드포인트의 요청/응답 구조, 검증 규칙, 에러 케이스,
하위 호환성 리스크, 테스트 케이스를 구조화해서 분석합니다.

## 실행

Python 3.10+와 `anthropic` 패키지, `ANTHROPIC_API_KEY`가 필요합니다. 아래 명령은 해당 에이전트 디렉터리에서 실행합니다. `--demo`도 실제 API를 호출합니다.

응답은 [공통 검증기](../shared/schema.py)로 필수 필드·중첩 타입·enum·추가 필드를 검사합니다. 위반하면 오류로 종료하며 결과 파일을 생성하거나 덮어쓰지 않습니다. 오프라인 검사는 저장소 루트에서 `python3 -B scripts/check-agent-regressions.py`로 실행합니다.

```bash
# 데모
python agent.py --demo

# 코드 파일 직접 지정
python agent.py \
  --code AutoCompleteController.php AutoCompleteService.php \
  --method GET \
  --path /api/v2/mail/auto-complete \
  --focus "backward_compatibility" "null_handling"

# 스펙 파일 포함
python agent.py \
  --code Controller.php \
  --spec openapi.yaml \
  --method POST \
  --path /api/v2/mail/send \
  --output result.json
```

`--code app/Mail/Controller.php app/Contact/Controller.php`처럼 이름이 같은 파일도 입력 경로별로 모두 전달됩니다.

## 출력 스키마

```json
{
  "endpoint": { "method": "GET", "path": "/api/v2/..." },
  "summary": "string",
  "request_fields": [
    { "name": "", "type": "", "required": false, "default": "", "validation": "", "notes": "" }
  ],
  "response_fields": [
    { "name": "", "type": "", "nullable": false, "notes": "" }
  ],
  "behavior_notes": ["string"],
  "error_cases": [
    { "status_code": 400, "condition": "", "response_body": "" }
  ],
  "dependencies": ["string"],
  "compatibility_risks": ["string"],
  "test_cases": [
    { "title": "", "input": "", "expected": "", "priority": "high" }
  ],
  "documentation_gaps": ["string"]
}
```

## 필드 설명

| 필드 | 설명 |
|------|------|
| `request_fields` | 요청 파라미터별 타입·필수여부·검증규칙 |
| `response_fields` | 응답 필드별 타입·nullable 여부 |
| `behavior_notes` | 코드에서 발견된 동작 특이사항 |
| `error_cases` | HTTP 상태코드별 에러 조건과 응답 |
| `dependencies` | 의존하는 서비스·DB·외부 시스템 |
| `compatibility_risks` | 하위 호환성 위험 항목 |
| `test_cases` | 우선순위별 테스트 케이스 제안 |
| `documentation_gaps` | 코드와 스펙 간 불일치·누락 항목 |
