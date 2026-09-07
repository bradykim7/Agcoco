"""
Agent 1: Document Summarizer
----------------------------
내부 문서(회의록, 설계 문서, 인시던트 노트, 주간 보고서 등)를
구조화된 운영 요약으로 정규화합니다.

사용법:
    python agent.py --file path/to/document.md
    python agent.py --text "문서 내용을 직접 입력"
    python agent.py --demo   # 내장 샘플로 테스트
"""

import argparse
import json
import os
import sys

import anthropic

# 상위 디렉토리에서 shared 모듈 import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shared.global_policy import GLOBAL_AGENT_POLICY
from shared.schema import validate_schema
from document_summarizer.prompt import DOCUMENT_SUMMARIZER_PROMPT, DOCUMENT_SUMMARIZER_SCHEMA

# ---------------------------------------------------------------------------
# 설정
# ---------------------------------------------------------------------------

MODEL = "claude-haiku-4-5-20251001"
MAX_TOKENS = 4096

# ---------------------------------------------------------------------------
# 시스템 프롬프트 조합
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = GLOBAL_AGENT_POLICY + "\n\n" + DOCUMENT_SUMMARIZER_PROMPT

# ---------------------------------------------------------------------------
# JSON 파싱 헬퍼
# ---------------------------------------------------------------------------

def parse_json_response(text: str) -> dict:
    """
    모델 응답에서 JSON을 안전하게 파싱합니다.
    마크다운 코드 블록이 포함된 경우도 처리합니다.
    """
    text = text.strip()

    # ```json ... ``` 블록 제거
    if text.startswith("```"):
        lines = text.splitlines()
        # 첫 줄(```json 또는 ```) 과 마지막 줄(```) 제거
        text = "\n".join(lines[1:-1]).strip()

    return json.loads(text)


# ---------------------------------------------------------------------------
# 에이전트 실행 함수
# ---------------------------------------------------------------------------

def run_document_summarizer(
    document_text: str,
    document_type_hint: str = "unknown",
    audience: str = "internal_team",
    source_documents: list[str] | None = None,
) -> dict:
    """
    문서 정리 에이전트를 실행하고 구조화된 결과를 반환합니다.

    Args:
        document_text: 분석할 문서 본문
        document_type_hint: 문서 유형 힌트 (예: weekly_report, meeting_notes, design_doc)
        audience: 대상 독자 (예: internal_team, leadership)
        source_documents: 참조 파일명 목록

    Returns:
        파싱된 JSON 딕셔너리
    """
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    # 입력 컨텍스트 구성
    input_context = {
        "document_type_hint": document_type_hint,
        "audience": audience,
        "source_documents": source_documents or [],
    }

    user_message = f"""
Input context:
{json.dumps(input_context, ensure_ascii=False, indent=2)}

Document content:
---
{document_text}
---

Analyze the document above and return the result as JSON only.
"""

    print(f"[Agent] 문서 분석 중... (model: {MODEL})")
    print(f"[Agent] 문서 유형 힌트: {document_type_hint}")
    print(f"[Agent] 문서 길이: {len(document_text)} chars")
    print("-" * 60)

    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": user_message}
        ],
    )

    # 응답 텍스트 추출
    raw_text = response.content[0].text

    # JSON 파싱
    try:
        result = parse_json_response(raw_text)
    except json.JSONDecodeError as e:
        print(f"[Error] JSON 파싱 실패: {e}")
        print(f"[Raw response]\n{raw_text}")
        raise

    # 스키마 검증
    validate_schema(result, DOCUMENT_SUMMARIZER_SCHEMA)

    return result


# ---------------------------------------------------------------------------
# 데모용 샘플 문서
# ---------------------------------------------------------------------------

DEMO_DOCUMENT = """
## 주간 보고 - 2026년 4월 1주차

### 참석자
- 김팀장, 박개발, 이QA, 최인프라

### 이번 주 완료 사항
- 메일 자동완성 API v2 마이그레이션 완료 (PR #1234 머지됨)
- SQLite ↔ MariaDB 정합성 점검 스크립트 초안 작성
- 인시던트 #892 원인 분석 완료: Redis TTL 설정 오류로 세션 만료 이슈 발생

### 주요 결정 사항
- 정합성 점검은 매일 새벽 2시 배치로 돌리기로 확정
- v1 API 지원 종료일을 2026년 6월 30일로 결정

### 리스크
- 레거시 클라이언트 중 일부가 v1 API를 아직 사용 중 (약 12개 클라이언트)
- 정합성 점검 스크립트가 대용량 계정에서 타임아웃 발생 가능성 있음

### 미결 사항
- 레거시 클라이언트 마이그레이션 지원 계획 미정
- 타임아웃 임계값 기준값 논의 필요

### 다음 주 할 일
- 레거시 클라이언트 목록 정리 (담당: 박개발, 4/10까지)
- 정합성 스크립트 성능 테스트 (담당: 이QA, 4/11까지)
- v1 종료 공지 초안 작성 (담당: 김팀장, 4/9까지)
"""


# ---------------------------------------------------------------------------
# CLI 진입점
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Document Summarizer Agent")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--file", help="분석할 문서 파일 경로")
    group.add_argument("--text", help="분석할 문서 텍스트 직접 입력")
    group.add_argument("--demo", action="store_true", help="내장 샘플 문서로 테스트")

    parser.add_argument(
        "--type-hint",
        default="unknown",
        help="문서 유형 힌트 (예: weekly_report, meeting_notes, design_doc, incident_note)",
    )
    parser.add_argument(
        "--audience",
        default="internal_team",
        help="대상 독자 (기본값: internal_team)",
    )
    parser.add_argument(
        "--output",
        help="결과를 저장할 JSON 파일 경로 (지정하지 않으면 stdout 출력)",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        default=True,
        help="JSON을 들여쓰기해서 출력 (기본값: True)",
    )

    args = parser.parse_args()

    # 문서 텍스트 결정
    if args.demo:
        document_text = DEMO_DOCUMENT
        type_hint = "weekly_report"
        print("[Demo 모드] 내장 샘플 문서를 사용합니다.")
    elif args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            document_text = f.read()
        type_hint = args.type_hint
    else:
        document_text = args.text
        type_hint = args.type_hint

    # 에이전트 실행
    result = run_document_summarizer(
        document_text=document_text,
        document_type_hint=type_hint,
        audience=args.audience,
    )

    # 결과 출력
    indent = 2 if args.pretty else None
    output_json = json.dumps(result, ensure_ascii=False, indent=indent)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_json)
        print(f"\n[완료] 결과 저장됨: {args.output}")
    else:
        print("\n[결과]")
        print(output_json)


if __name__ == "__main__":
    main()
