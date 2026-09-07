# Agent 3: PR Review Assistant

PR diff와 관련 코드를 분석해 리스크 중심 리뷰 노트를 생성합니다.
승인/거절 판단은 하지 않으며, 근거 기반의 리뷰 보조만 수행합니다.

## 실행

Python 3.10+와 `anthropic` 패키지, `ANTHROPIC_API_KEY`가 필요합니다. 아래 명령은 해당 에이전트 디렉터리에서 실행합니다. `--demo`도 실제 API를 호출합니다.

응답은 [공통 검증기](../shared/schema.py)로 필수 필드·중첩 타입·enum·추가 필드를 검사합니다. 위반하면 오류로 종료하며 결과 파일을 생성하거나 덮어쓰지 않습니다. 오프라인 검사는 저장소 루트에서 `python3 -B scripts/check-agent-regressions.py`로 실행합니다.

```bash
# 데모
python agent.py --demo

# diff 파일 지정
python agent.py \
  --diff changes.diff \
  --repo your-org/your-repo \
  --pr-number 1234 \
  --pr-title "feat: 자동완성 alias 타입 추가"

# 컨텍스트 파일 포함 + 체크리스트 지정
python agent.py \
  --diff changes.diff \
  --context Service.php Repository.php \
  --checklist backward_compatibility n_plus_one null_handling \
  --output review.json
```

`--context app/Mail/Service.php app/Contact/Service.php`처럼 이름이 같은 파일도 입력 경로별로 모두 전달됩니다.

## 체크리스트 항목

| 항목 | 설명 |
|------|------|
| `backward_compatibility` | API/DB 하위 호환성 |
| `data_integrity` | 데이터 정합성 |
| `security_and_auth` | 인증/인가/SQL 인젝션 |
| `error_handling` | try-catch, 실패 처리 |
| `n_plus_one` | N+1 쿼리, 과도한 DB 호출 |
| `logging_and_monitoring` | 로그, 트레이싱 |
| `test_coverage` | 테스트 누락 |
| `null_handling` | null/undefined 처리 |

## 출력 스키마

```json
{
  "summary": "string",
  "risk_points": [
    {
      "title": "string",
      "severity": "high",
      "category": "string",
      "reason": "string",
      "evidence": ["string"],
      "needs_confirmation": false,
      "suggested_review_comment": "string"
    }
  ],
  "missing_tests": ["string"],
  "compatibility_risks": ["string"],
  "questions_for_author": ["string"],
  "safe_suggestions": ["string"]
}
```

## 필드 설명

| 필드 | 설명 |
|------|------|
| `risk_points` | 증거 기반 리스크 목록 (severity + category 포함) |
| `needs_confirmation` | 의심스럽지만 확정되지 않은 이슈 |
| `suggested_review_comment` | PR에 바로 붙일 수 있는 리뷰 코멘트 초안 |
| `missing_tests` | 커버되지 않은 케이스 목록 |
| `compatibility_risks` | 하위 호환성 위험 항목 |
| `questions_for_author` | 작성자에게 확인이 필요한 질문 |
| `safe_suggestions` | 리스크 없는 개선 제안 |
