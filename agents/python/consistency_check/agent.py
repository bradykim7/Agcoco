"""
Agent 5: Consistency Check
---------------------------
두 데이터 스냅샷(MariaDB ↔ SQLite 등)을 비교해 불일치를 감지하고
구조화된 리포트를 생성합니다.

사용법:
    python agent.py --demo
    python agent.py --source-a mariadb_snapshot.json --source-b sqlite_snapshot.json --key account_id
    python agent.py --source-a a.json --source-b b.json --key id --fields email quota status
"""

import argparse
import json
import os
import sys

import anthropic

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shared.global_policy import GLOBAL_AGENT_POLICY
from shared.schema import validate_schema
from consistency_check.prompt import CONSISTENCY_CHECK_PROMPT, CONSISTENCY_CHECK_SCHEMA

# ---------------------------------------------------------------------------
# 설정
# ---------------------------------------------------------------------------

MODEL = "claude-haiku-4-5-20251001"
MAX_TOKENS = 4096

SYSTEM_PROMPT = GLOBAL_AGENT_POLICY + "\n\n" + CONSISTENCY_CHECK_PROMPT

# ---------------------------------------------------------------------------
# 헬퍼
# ---------------------------------------------------------------------------

def parse_json_response(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1]).strip()
    return json.loads(text)


def format_statistics(stats: dict) -> str:
    return (
        f"전체 {stats.get('total_checked', 0)}건 중 "
        f"불일치 {stats.get('total_inconsistent', 0)}건 "
        f"(source누락 {stats.get('missing_in_source', 0)}, "
        f"target누락 {stats.get('missing_in_target', 0)}, "
        f"값불일치 {stats.get('field_value_mismatch', 0)})"
    )


def format_severity_summary(inconsistencies: list) -> str:
    counts = {"high": 0, "medium": 0, "low": 0}
    for item in inconsistencies:
        sev = item.get("severity", "low")
        counts[sev] = counts.get(sev, 0) + 1
    parts = []
    if counts["high"]:
        parts.append(f"HIGH {counts['high']}건")
    if counts["medium"]:
        parts.append(f"MEDIUM {counts['medium']}건")
    if counts["low"]:
        parts.append(f"LOW {counts['low']}건")
    return ", ".join(parts) if parts else "불일치 없음"


# ---------------------------------------------------------------------------
# 에이전트 실행
# ---------------------------------------------------------------------------

def run_consistency_check(
    source_a_name: str,
    source_b_name: str,
    records_a: list[dict],
    records_b: list[dict],
    key_field: str,
    checked_fields: list[str] | None = None,
    threshold_notes: list[str] | None = None,
) -> dict:
    """
    데이터 정합성 점검 에이전트를 실행합니다.

    Args:
        source_a_name   : 소스 A 이름 (예: MariaDB)
        source_b_name   : 소스 B 이름 (예: SQLite)
        records_a       : 소스 A 레코드 목록 (dict 리스트)
        records_b       : 소스 B 레코드 목록 (dict 리스트)
        key_field       : 레코드 매칭 기준 키 필드명
        checked_fields  : 비교할 필드 목록 (None이면 전체)
        threshold_notes : 허용 오차 기준 메모 (예: timestamp 1분 이내 차이는 무시)

    Returns:
        파싱된 JSON 딕셔너리
    """
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    input_context = {
        "source_a": source_a_name,
        "source_b": source_b_name,
        "key_field": key_field,
        "checked_fields": checked_fields or "all",
        "threshold_notes": threshold_notes or [],
    }

    user_message = "\n".join([
        "Input context:",
        json.dumps(input_context, ensure_ascii=False, indent=2),
        "",
        f"=== {source_a_name} Records ({len(records_a)} rows) ===",
        json.dumps(records_a, ensure_ascii=False, indent=2),
        "",
        f"=== {source_b_name} Records ({len(records_b)} rows) ===",
        json.dumps(records_b, ensure_ascii=False, indent=2),
        "",
        "Compare the two datasets using key_field to join records.",
        "Report all inconsistencies. Return structured JSON only.",
    ])

    print(f"[Agent] 데이터 정합성 점검 시작...")
    print(f"[Agent] 소스 A: {source_a_name} ({len(records_a)}건)")
    print(f"[Agent] 소스 B: {source_b_name} ({len(records_b)}건)")
    print(f"[Agent] 키 필드: {key_field}")
    print(f"[Agent] 비교 필드: {checked_fields or '전체'}")
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

    validate_schema(result, CONSISTENCY_CHECK_SCHEMA)

    inconsistencies = result.get("inconsistencies", [])
    stats = result.get("statistics", {})

    print(f"\n[분석 완료] {format_statistics(stats)}")
    print(f"[분석 완료] 심각도: {format_severity_summary(inconsistencies)}")
    print(f"[분석 완료] 권고사항: {len(result.get('recommendations', []))}건")

    return result


# ---------------------------------------------------------------------------
# 데모 데이터
# ---------------------------------------------------------------------------

DEMO_SOURCE_A_NAME = "MariaDB (운영 replica)"
DEMO_SOURCE_B_NAME = "SQLite (로컬 캐시)"
DEMO_KEY_FIELD = "account_id"
DEMO_CHECKED_FIELDS = ["email", "quota_mb", "status", "enabled", "updated_at"]

DEMO_RECORDS_A = [
    {"account_id": "acct_001", "email": "alice@example.com",   "quota_mb": 5120,  "status": "active",    "enabled": True,  "updated_at": "2026-04-01T10:00:00Z"},
    {"account_id": "acct_002", "email": "bob@example.com",     "quota_mb": 2048,  "status": "active",    "enabled": True,  "updated_at": "2026-04-02T09:30:00Z"},
    {"account_id": "acct_003", "email": "carol@example.com",   "quota_mb": 1024,  "status": "suspended", "enabled": False, "updated_at": "2026-04-03T14:00:00Z"},
    {"account_id": "acct_004", "email": "dave@example.com",    "quota_mb": 3072,  "status": "active",    "enabled": True,  "updated_at": "2026-04-04T08:00:00Z"},
    {"account_id": "acct_005", "email": "eve@example.com",     "quota_mb": 10240, "status": "active",    "enabled": True,  "updated_at": "2026-04-05T11:00:00Z"},
]

DEMO_RECORDS_B = [
    {"account_id": "acct_001", "email": "alice@example.com",   "quota_mb": 5120,  "status": "active",    "enabled": True,  "updated_at": "2026-04-01T10:00:00Z"},
    {"account_id": "acct_002", "email": "bob@example.com",     "quota_mb": 1024,  "status": "active",    "enabled": True,  "updated_at": "2026-04-02T09:30:00Z"},  # quota_mb 불일치
    {"account_id": "acct_003", "email": "carol@example.com",   "quota_mb": 1024,  "status": "active",    "enabled": True,  "updated_at": "2026-04-03T14:00:00Z"},  # status, enabled 불일치
    # acct_004 누락 (SQLite에 없음)
    {"account_id": "acct_005", "email": "eve@example.com",     "quota_mb": 10240, "status": "active",    "enabled": True,  "updated_at": "2026-04-05T11:00:00Z"},
    {"account_id": "acct_006", "email": "frank@example.com",   "quota_mb": 2048,  "status": "active",    "enabled": True,  "updated_at": "2026-04-06T07:00:00Z"},  # MariaDB에 없음
]

DEMO_THRESHOLD_NOTES = [
    "updated_at 필드는 1분(60초) 이내 차이는 무시",
    "quota_mb는 정확히 일치해야 함",
    "status, enabled는 정확히 일치해야 함",
]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Consistency Check Agent")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--demo", action="store_true", help="내장 샘플 데이터로 테스트")
    group.add_argument("--source-a", help="소스 A JSON 파일 경로 (레코드 배열)")

    parser.add_argument("--source-b", help="소스 B JSON 파일 경로 (레코드 배열)")
    parser.add_argument("--source-a-name", default="Source A", help="소스 A 이름")
    parser.add_argument("--source-b-name", default="Source B", help="소스 B 이름")
    parser.add_argument("--key", default="id", help="레코드 매칭 키 필드 (기본값: id)")
    parser.add_argument(
        "--fields",
        nargs="+",
        help="비교할 필드 목록 (미지정 시 전체)",
    )
    parser.add_argument(
        "--threshold",
        nargs="+",
        help="허용 오차 기준 메모 (예: --threshold 'updated_at 60초 이내 무시')",
    )
    parser.add_argument("--output", help="결과 저장 파일 경로")

    args = parser.parse_args()

    if args.demo:
        result = run_consistency_check(
            source_a_name=DEMO_SOURCE_A_NAME,
            source_b_name=DEMO_SOURCE_B_NAME,
            records_a=DEMO_RECORDS_A,
            records_b=DEMO_RECORDS_B,
            key_field=DEMO_KEY_FIELD,
            checked_fields=DEMO_CHECKED_FIELDS,
            threshold_notes=DEMO_THRESHOLD_NOTES,
        )
    else:
        if not args.source_b:
            parser.error("--source-b 파일 경로가 필요합니다.")

        with open(args.source_a, "r", encoding="utf-8") as f:
            records_a = json.load(f)
        with open(args.source_b, "r", encoding="utf-8") as f:
            records_b = json.load(f)

        result = run_consistency_check(
            source_a_name=args.source_a_name,
            source_b_name=args.source_b_name,
            records_a=records_a,
            records_b=records_b,
            key_field=args.key,
            checked_fields=args.fields,
            threshold_notes=args.threshold or [],
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
