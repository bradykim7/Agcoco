"""
Agent 4: Architecture Review
-----------------------------
아키텍처 제안서를 분석해 운영 트레이드오프와 설계 리스크를 구조화합니다.
"좋다/나쁘다" 판단 없이, 제약 조건과 트래픽 가정에 근거한 구체적 리스크를 제시합니다.

사용법:
    python agent.py --demo
    python agent.py --file architecture.md --system consistency-check-platform
    python agent.py --text "아키텍처 설명..." --constraints "DB direct access limited"
"""

import argparse
import json
import os
import sys

import anthropic

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shared.global_policy import GLOBAL_AGENT_POLICY
from shared.schema import validate_schema
from architecture_review.prompt import ARCHITECTURE_REVIEW_PROMPT, ARCHITECTURE_REVIEW_SCHEMA

# ---------------------------------------------------------------------------
# 설정
# ---------------------------------------------------------------------------

MODEL = "claude-opus-4-7"
MAX_TOKENS = 4096

SYSTEM_PROMPT = GLOBAL_AGENT_POLICY + "\n\n" + ARCHITECTURE_REVIEW_PROMPT

# ---------------------------------------------------------------------------
# 헬퍼
# ---------------------------------------------------------------------------

def parse_json_response(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1]).strip()
    return json.loads(text)


def format_risk_summary(risks: list) -> str:
    counts = {"high": 0, "medium": 0, "low": 0}
    for r in risks:
        sev = r.get("severity", "low")
        counts[sev] = counts.get(sev, 0) + 1
    parts = []
    if counts["high"]:
        parts.append(f"HIGH {counts['high']}건")
    if counts["medium"]:
        parts.append(f"MEDIUM {counts['medium']}건")
    if counts["low"]:
        parts.append(f"LOW {counts['low']}건")
    return ", ".join(parts) if parts else "리스크 없음"


# ---------------------------------------------------------------------------
# 에이전트 실행
# ---------------------------------------------------------------------------

def run_architecture_review(
    architecture_text: str,
    system_name: str = "",
    traffic_assumptions: list = None,
    constraints: list = None,
    review_dimensions: list = None,
) -> dict:
    """
    아키텍처 리뷰 에이전트를 실행합니다.

    Args:
        architecture_text  : 아키텍처 설명 문서 (자유 형식)
        system_name        : 시스템 이름 (예: consistency-check-platform)
        traffic_assumptions: 트래픽/규모 가정 목록
        constraints        : 제약 조건 목록 (예: DB direct access limited)
        review_dimensions  : 집중 검토 차원 목록 (미지정 시 전체)

    Returns:
        파싱된 JSON 딕셔너리
    """
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    # 입력 컨텍스트 구성
    input_context = {
        "system_name": system_name or "unknown",
        "traffic_assumptions": traffic_assumptions or [],
        "constraints": constraints or [],
        "review_dimensions": review_dimensions or [
            "availability",
            "single_points_of_failure",
            "scalability",
            "failure_propagation",
            "data_consistency",
            "security_boundaries",
            "monitoring_and_traceability",
            "deployment_and_rollback",
            "operational_burden",
        ],
    }

    user_message = "\n".join([
        "Input context:",
        json.dumps(input_context, ensure_ascii=False, indent=2),
        "",
        "=== Architecture Description ===",
        architecture_text,
        "",
        "Review the architecture above based on the stated constraints and traffic assumptions.",
        "Return structured JSON only.",
        "Separate confirmed risks from hypothetical risks using evidence field.",
        "For tradeoffs, explain both the gain and the cost explicitly.",
    ])

    print(f"[Agent] 아키텍처 리뷰 시작...")
    print(f"[Agent] 시스템: {system_name or '미지정'}")
    print(f"[Agent] 트래픽 가정: {len(traffic_assumptions or [])}개")
    print(f"[Agent] 제약 조건: {len(constraints or [])}개")
    print("-" * 60)

    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    raw_text = response.content[0].text

    try:
        result = parse_json_response(raw_text)
    except json.JSONDecodeError as e:
        print(f"[Error] JSON 파싱 실패: {e}")
        print(f"[Raw response]\n{raw_text}")
        raise

    validate_schema(result, ARCHITECTURE_REVIEW_SCHEMA)

    risks = result.get("risks", [])
    tradeoffs = result.get("tradeoffs", [])
    changes = result.get("recommended_changes", [])

    print(f"\n[분석 완료] 리스크: {format_risk_summary(risks)}")
    print(f"[분석 완료] 트레이드오프: {len(tradeoffs)}건")
    print(f"[분석 완료] 권장 변경: {len(changes)}건")
    print(f"[분석 완료] 미결 질문: {len(result.get('open_questions', []))}건")

    return result


# ---------------------------------------------------------------------------
# 데모 데이터
# ---------------------------------------------------------------------------

DEMO_SYSTEM_NAME = "consistency-check-platform"

DEMO_TRAFFIC_ASSUMPTIONS = [
    "메일 서버 1,000대 대상",
    "요청 기반(on-demand) 스냅샷 비교 — 실시간 아님",
    "운영 메일 트래픽에 영향 없어야 함",
    "점검 결과는 내부 관리자만 조회",
]

DEMO_CONSTRAINTS = [
    "운영 DB(MariaDB)에 대한 직접 접근 제한 — 읽기 전용 replica만 허용",
    "점검 서비스 오류가 운영 서비스로 전파되면 안 됨",
    "읽기 중심 설계 선호",
    "초기 버전은 자동 수정 없이 감지만 수행",
]

DEMO_ARCHITECTURE_TEXT = """
## 정합성 점검 플랫폼 아키텍처 v0.1

### 개요
MariaDB(운영)와 SQLite(로컬 캐시) 간의 데이터 정합성을 주기적으로 비교하고
불일치를 감지하는 플랫폼.

### 컴포넌트 구성

1. **Snapshot Collector**
   - MariaDB read replica에서 대상 테이블 스냅샷을 수집
   - SQLite 파일에서 로컬 스냅샷 수집
   - 수집 결과를 중간 저장소(Redis)에 TTL 1시간으로 캐싱

2. **Consistency Checker**
   - Redis에서 두 스냅샷을 가져와 키 기반 비교
   - 불일치 분류: missing_in_source, missing_in_target, field_value_mismatch
   - 비교 결과를 Result DB(별도 PostgreSQL)에 저장

3. **API Server**
   - 관리자가 점검 결과를 조회하는 REST API
   - 점검 실행 트리거 엔드포인트 제공
   - 인증: 내부 API 키

4. **Scheduler**
   - 매일 새벽 2시 전체 점검 배치 실행
   - on-demand 점검 요청도 API를 통해 지원

### 데이터 흐름
MariaDB replica → Snapshot Collector → Redis
SQLite files   → Snapshot Collector → Redis
                                       ↓
                              Consistency Checker → Result DB → API Server

### 배포
- 모든 컴포넌트는 단일 서버에 Docker Compose로 배포
- Redis, PostgreSQL도 동일 서버 내 컨테이너로 운영
"""


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Architecture Review Agent")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--demo", action="store_true", help="내장 샘플 아키텍처로 테스트")
    group.add_argument("--file", help="아키텍처 문서 파일 경로")
    group.add_argument("--text", help="아키텍처 설명 텍스트 직접 입력")

    parser.add_argument("--system", default="", help="시스템 이름")
    parser.add_argument(
        "--traffic",
        nargs="+",
        help="트래픽/규모 가정 (예: --traffic '서버 1000대' 'on-demand 요청')",
    )
    parser.add_argument(
        "--constraints",
        nargs="+",
        help="제약 조건 (예: --constraints 'DB 직접 접근 제한' '읽기 전용')",
    )
    parser.add_argument(
        "--dimensions",
        nargs="+",
        help="집중 검토 차원 (미지정 시 전체 9개 차원)",
    )
    parser.add_argument("--output", help="결과 저장 파일 경로")

    args = parser.parse_args()

    if args.demo:
        result = run_architecture_review(
            architecture_text=DEMO_ARCHITECTURE_TEXT,
            system_name=DEMO_SYSTEM_NAME,
            traffic_assumptions=DEMO_TRAFFIC_ASSUMPTIONS,
            constraints=DEMO_CONSTRAINTS,
        )
    elif args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            arch_text = f.read()
        result = run_architecture_review(
            architecture_text=arch_text,
            system_name=args.system,
            traffic_assumptions=args.traffic or [],
            constraints=args.constraints or [],
            review_dimensions=args.dimensions,
        )
    else:
        result = run_architecture_review(
            architecture_text=args.text,
            system_name=args.system,
            traffic_assumptions=args.traffic or [],
            constraints=args.constraints or [],
            review_dimensions=args.dimensions,
        )

    output_json = json.dumps(result, ensure_ascii=False, indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_json)
        print(f"\n[완료] 결과 저장됨: {args.output}")
    else:
        print("\n[결과]")
        print(output_json)


if __name__ == "__main__":
    main()
