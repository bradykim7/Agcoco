"""
Agent 2: Endpoint Analysis
--------------------------
API 엔드포인트의 요청/응답 구조, 검증 규칙, 에러 케이스,
하위 호환성 리스크, 테스트 케이스를 구조화해서 분석합니다.

사용법:
    python agent.py --demo
    python agent.py --code AutoCompleteController.php --method GET --path /api/v2/mail/auto-complete
    python agent.py --spec openapi.yaml --method POST --path /api/v2/mail/send
"""

import argparse
import json
import os
import sys

import anthropic

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shared.global_policy import GLOBAL_AGENT_POLICY
from shared.schema import validate_schema
from endpoint_analysis.prompt import ENDPOINT_ANALYSIS_PROMPT, ENDPOINT_ANALYSIS_SCHEMA

# ---------------------------------------------------------------------------
# 설정
# ---------------------------------------------------------------------------

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 4096

SYSTEM_PROMPT = GLOBAL_AGENT_POLICY + "\n\n" + ENDPOINT_ANALYSIS_PROMPT

# ---------------------------------------------------------------------------
# 헬퍼
# ---------------------------------------------------------------------------

def parse_json_response(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1]).strip()
    return json.loads(text)


def build_context_block(
    method: str,
    path: str,
    code_snippets: dict[str, str],
    spec_text: str | None,
    focus_points: list[str],
) -> str:
    """에이전트에게 전달할 컨텍스트 블록을 구성합니다."""
    lines = []

    lines.append(f"Endpoint: {method.upper()} {path}")
    lines.append("")

    if focus_points:
        lines.append("Focus points:")
        for fp in focus_points:
            lines.append(f"  - {fp}")
        lines.append("")

    if spec_text:
        lines.append("=== API Specification ===")
        lines.append(spec_text)
        lines.append("")

    for filename, content in code_snippets.items():
        lines.append(f"=== {filename} ===")
        lines.append(content)
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 에이전트 실행
# ---------------------------------------------------------------------------

def run_endpoint_analysis(
    method: str,
    path: str,
    code_snippets: dict[str, str] | None = None,
    spec_text: str | None = None,
    focus_points: list[str] | None = None,
) -> dict:
    """
    엔드포인트 분석 에이전트를 실행합니다.

    Args:
        method: HTTP 메서드 (GET, POST, PUT, DELETE 등)
        path: 엔드포인트 경로 (예: /api/v2/mail/auto-complete)
        code_snippets: {"파일 경로": "코드 내용"} 형태의 관련 코드
        spec_text: OpenAPI/Swagger 등 스펙 문서 텍스트
        focus_points: 특별히 분석에 집중할 항목 목록

    Returns:
        파싱된 JSON 딕셔너리
    """
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    context = build_context_block(
        method=method,
        path=path,
        code_snippets=code_snippets or {},
        spec_text=spec_text,
        focus_points=focus_points or [],
    )

    user_message = f"""
Analyze the following endpoint and return structured JSON only.

{context}
"""

    print(f"[Agent] 엔드포인트 분석 중: {method.upper()} {path}")
    print(f"[Agent] 코드 파일 수: {len(code_snippets or {})}")
    print(f"[Agent] 스펙 문서: {'있음' if spec_text else '없음'}")
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

    validate_schema(result, ENDPOINT_ANALYSIS_SCHEMA)

    return result


# ---------------------------------------------------------------------------
# 데모용 샘플
# ---------------------------------------------------------------------------

DEMO_CODE_SNIPPETS = {
    "AutoCompleteController.php": """
<?php
class AutoCompleteController extends BaseController
{
    public function index(Request $request): JsonResponse
    {
        $types = $request->input('types', ['contact', 'group']);
        $query = $request->input('q', '');
        $limit = min((int) $request->input('limit', 20), 100);

        if (strlen($query) < 2) {
            return response()->json(['error' => 'Query too short'], 400);
        }

        $results = $this->autoCompleteService->search($query, $types, $limit);

        return response()->json([
            'data' => $results,
            'total' => count($results),
        ]);
    }
}
""",
    "AutoCompleteService.php": """
<?php
class AutoCompleteService
{
    public function search(string $query, array $types, int $limit): array
    {
        $results = [];

        if (in_array('contact', $types)) {
            $results = array_merge($results, $this->searchContacts($query, $limit));
        }

        if (in_array('group', $types)) {
            $results = array_merge($results, $this->searchGroups($query, $limit));
        }

        // NOTE: 'alias' type는 아직 미구현, 요청해도 무시됨
        return array_slice($results, 0, $limit);
    }
}
""",
    "openapi.yaml (excerpt)": """
/api/v2/mail/auto-complete:
  get:
    summary: 메일 수신자 자동완성
    parameters:
      - name: q
        in: query
        required: true
        schema:
          type: string
      - name: types
        in: query
        schema:
          type: array
          items:
            type: string
            enum: [contact, group, alias]
      - name: limit
        in: query
        schema:
          type: integer
          default: 20
    responses:
      200:
        description: 성공
        content:
          application/json:
            schema:
              type: object
              properties:
                data:
                  type: array
                total:
                  type: integer
""",
}

DEMO_FOCUS_POINTS = [
    "types 파라미터 유효값과 실제 동작 차이",
    "backward compatibility",
    "limit 파라미터 경계값 처리",
    "q 파라미터 최소 길이 검증",
]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Endpoint Analysis Agent")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--demo", action="store_true", help="내장 샘플로 테스트")
    group.add_argument("--code", nargs="+", help="분석할 코드 파일 경로 목록")

    parser.add_argument("--method", default="GET", help="HTTP 메서드 (기본값: GET)")
    parser.add_argument("--path", default="", help="엔드포인트 경로")
    parser.add_argument("--spec", help="OpenAPI/Swagger 스펙 파일 경로")
    parser.add_argument(
        "--focus",
        nargs="+",
        help="집중 분석 항목 (예: --focus backward_compatibility null_handling)",
    )
    parser.add_argument("--output", help="결과 저장 파일 경로")

    args = parser.parse_args()

    if args.demo:
        result = run_endpoint_analysis(
            method="GET",
            path="/api/v2/mail/auto-complete",
            code_snippets=DEMO_CODE_SNIPPETS,
            focus_points=DEMO_FOCUS_POINTS,
        )
    else:
        # 코드 파일 읽기
        code_snippets = {}
        for file_path in args.code or []:
            with open(file_path, "r", encoding="utf-8") as f:
                code_snippets[file_path] = f.read()

        # 스펙 파일 읽기
        spec_text = None
        if args.spec:
            with open(args.spec, "r", encoding="utf-8") as f:
                spec_text = f.read()

        result = run_endpoint_analysis(
            method=args.method,
            path=args.path,
            code_snippets=code_snippets,
            spec_text=spec_text,
            focus_points=args.focus or [],
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
