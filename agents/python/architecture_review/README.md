# Agent 4: Architecture Review

아키텍처 제안서를 분석해 운영 트레이드오프와 설계 리스크를 구조화합니다.
"좋다/나쁘다" 판단 없이, 제약 조건과 트래픽 가정에 근거한 구체적 리스크를 제시합니다.

## 실행

Python 3.10+와 `anthropic` 패키지, `ANTHROPIC_API_KEY`가 필요합니다. 아래 명령은 해당 에이전트 디렉터리에서 실행합니다. `--demo`도 실제 API를 호출합니다.

응답은 [공통 검증기](../shared/schema.py)로 필수 필드·중첩 타입·enum·추가 필드를 검사합니다. 위반하면 오류로 종료하며 결과 파일을 생성하거나 덮어쓰지 않습니다. 오프라인 검사는 저장소 루트에서 `python3 -B scripts/check-agent-regressions.py`로 실행합니다.

```bash
# 데모
python agent.py --demo

# 파일 입력
python agent.py \
  --file architecture.md \
  --system consistency-check-platform \
  --traffic "서버 1000대" "on-demand 요청" \
  --constraints "DB 직접 접근 제한" "읽기 전용 replica만 허용"

# 텍스트 직접 입력
python agent.py \
  --text "아키텍처 설명..." \
  --system my-system \
  --output review.json
```

## 검토 차원 (9개)

| 차원 | 설명 |
|------|------|
| `availability` | 가용성 목표 달성 여부 |
| `single_points_of_failure` | 단일 장애점 |
| `scalability` | 트래픽/데이터 증가 대응 |
| `failure_propagation` | 장애 전파 범위 |
| `data_consistency` | 데이터 일관성 보장 |
| `security_boundaries` | 보안 경계 |
| `monitoring_and_traceability` | 모니터링/추적 |
| `deployment_and_rollback` | 배포/롤백 복잡도 |
| `operational_burden` | 운영 부담 |

## 출력 스키마

```json
{
  "summary": "string",
  "assumptions": ["string"],
  "strengths": ["string"],
  "risks": [
    {
      "title": "string",
      "severity": "high",
      "impact": "string",
      "affected_components": ["string"],
      "evidence": ["string"],
      "mitigation": "string"
    }
  ],
  "tradeoffs": [
    {
      "decision": "string",
      "gain": "string",
      "cost": "string"
    }
  ],
  "recommended_changes": [
    {
      "title": "string",
      "priority": "high",
      "rationale": "string"
    }
  ],
  "open_questions": ["string"]
}
```

## 필드 설명

| 필드 | 설명 |
|------|------|
| `assumptions` | 에이전트가 분석에 사용한 가정 (명시적으로 분리) |
| `strengths` | 잘 설계된 부분 — 리스크만 보고하지 않음 |
| `risks.evidence` | 리스크의 근거 — 아키텍처 텍스트에서 직접 인용 |
| `risks.mitigation` | 구체적인 완화 방안 |
| `tradeoffs` | 설계 결정의 득과 실을 명시적으로 분리 |
| `recommended_changes` | 우선순위별 개선 권고 |
| `open_questions` | 설계자에게 확인이 필요한 미결 질문 |
