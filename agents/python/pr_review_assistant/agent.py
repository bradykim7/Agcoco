"""
Agent 3: PR Review Assistant
-----------------------------
PR diff와 관련 코드를 분석해 리스크 중심의 리뷰 노트를 생성합니다.
승인/거절 판단은 하지 않으며, 근거 기반의 리뷰 보조만 수행합니다.

사용법:
    python agent.py --demo
    python agent.py --diff changes.diff --checklist backward_compatibility n_plus_one
    python agent.py --diff changes.diff --context Service.php --output review.json
"""

import argparse
import json
import os
import sys

import anthropic

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shared.global_policy import GLOBAL_AGENT_POLICY
from shared.schema import validate_schema
from pr_review_assistant.prompt import PR_REVIEW_ASSISTANT_PROMPT, PR_REVIEW_ASSISTANT_SCHEMA

# ---------------------------------------------------------------------------
# 설정
# ---------------------------------------------------------------------------

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 4096

SYSTEM_PROMPT = GLOBAL_AGENT_POLICY + "\n\n" + PR_REVIEW_ASSISTANT_PROMPT

VALID_CHECKLIST_ITEMS = [
    "backward_compatibility",
    "data_integrity",
    "security_and_auth",
    "error_handling",
    "n_plus_one",
    "logging_and_monitoring",
    "test_coverage",
    "null_handling",
]

# ---------------------------------------------------------------------------
# 헬퍼
# ---------------------------------------------------------------------------

def parse_json_response(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1]).strip()
    return json.loads(text)


def format_severity_summary(risk_points: list) -> str:
    counts = {"high": 0, "medium": 0, "low": 0}
    for rp in risk_points:
        sev = rp.get("severity", "low")
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

def run_pr_review(
    diff_text: str,
    pr_title: str = "",
    pr_description: str = "",
    context_files: dict = None,
    checklist: list = None,
    repo: str = "",
    pr_number: int = None,
) -> dict:
    """
    PR 리뷰 보조 에이전트를 실행합니다.

    Args:
        diff_text      : PR의 unified diff 텍스트
        pr_title       : PR 제목
        pr_description : PR 설명
        context_files  : {"파일 경로": "전체 코드"} - diff 외 참고 파일
        checklist      : 집중 검토 항목 목록
        repo           : 레포지토리명 (예: org/repo)
        pr_number      : PR 번호

    Returns:
        파싱된 JSON 딕셔너리
    """
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    # 메타 정보
    meta_lines = []
    if repo:
        meta_lines.append(f"Repository: {repo}")
    if pr_number:
        meta_lines.append(f"PR: #{pr_number}")
    if pr_title:
        meta_lines.append(f"Title: {pr_title}")
    if pr_description:
        meta_lines.append(f"Description:\n{pr_description}")

    # 체크리스트
    active_checklist = checklist or VALID_CHECKLIST_ITEMS
    checklist_block = "Review checklist (focus on these):\n" + "\n".join(
        f"  - {item}" for item in active_checklist
    )

    # 컨텍스트 파일
    context_block = ""
    if context_files:
        sections = []
        for fname, content in context_files.items():
            sections.append(f"=== Context: {fname} ===\n{content}")
        context_block = "\n\n".join(sections)

    user_message = "\n".join([
        "\n".join(meta_lines),
        "",
        checklist_block,
        "",
        "=== PR Diff ===",
        diff_text,
        "",
        context_block,
        "",
        "Review the diff above and return structured JSON only.",
        "Raise issues only when you have specific evidence in the diff or context files.",
    ])

    print(f"[Agent] PR 리뷰 분석 중...")
    if repo and pr_number:
        print(f"[Agent] 대상: {repo} #{pr_number}")
    print(f"[Agent] Diff 길이: {len(diff_text)} chars")
    print(f"[Agent] 컨텍스트 파일 수: {len(context_files or {})}")
    print(f"[Agent] 체크리스트: {', '.join(active_checklist)}")
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

    validate_schema(result, PR_REVIEW_ASSISTANT_SCHEMA)

    risk_points = result.get("risk_points", [])
    print(f"\n[분석 완료] 리스크: {format_severity_summary(risk_points)}")
    print(f"[분석 완료] 누락 테스트: {len(result.get('missing_tests', []))}건")
    print(f"[분석 완료] 작성자 질문: {len(result.get('questions_for_author', []))}건")

    return result


# ---------------------------------------------------------------------------
# 데모 데이터
# ---------------------------------------------------------------------------

DEMO_PR_TITLE = "feat: 메일 자동완성 API v2 - types 파라미터 확장"
DEMO_PR_DESCRIPTION = """
types 파라미터에 alias 타입을 추가합니다.
기존 contact, group 타입은 그대로 유지됩니다.
limit 기본값을 20에서 50으로 변경합니다.
"""

DEMO_DIFF = """\
diff --git a/app/Http/Controllers/Api/V2/AutoCompleteController.php b/app/Http/Controllers/Api/V2/AutoCompleteController.php
index a1b2c3d..e4f5g6h 100644
--- a/app/Http/Controllers/Api/V2/AutoCompleteController.php
+++ b/app/Http/Controllers/Api/V2/AutoCompleteController.php
@@ -12,7 +12,7 @@ class AutoCompleteController extends BaseController
     public function index(Request $request): JsonResponse
     {
-        $types = $request->input('types', ['contact', 'group']);
+        $types = $request->input('types', ['contact', 'group', 'alias']);
-        $limit = min((int) $request->input('limit', 20), 100);
+        $limit = min((int) $request->input('limit', 50), 100);
         $query = $request->input('q', '');

         if (strlen($query) < 2) {
             return response()->json(['error' => 'Query too short'], 400);
         }

+        if (!is_array($types)) {
+            $types = explode(',', $types);
+        }
+
         $results = $this->autoCompleteService->search($query, $types, $limit);

         return response()->json([
             'data' => $results,
             'total' => count($results),
         ]);
     }

diff --git a/app/Services/AutoCompleteService.php b/app/Services/AutoCompleteService.php
index b2c3d4e..f5g6h7i 100644
--- a/app/Services/AutoCompleteService.php
+++ b/app/Services/AutoCompleteService.php
@@ -8,6 +8,12 @@ class AutoCompleteService
     public function search(string $query, array $types, int $limit): array
     {
         $results = [];
+
+        if (in_array('alias', $types)) {
+            $aliases = $this->aliasRepository->findByQuery($query);
+            foreach ($aliases as $alias) {
+                $results[] = ['type' => 'alias', 'email' => $alias->address, 'name' => $alias->label];
+            }
+        }

         if (in_array('contact', $types)) {
             $results = array_merge($results, $this->searchContacts($query, $limit));
         }
@@ -18,6 +24,7 @@ class AutoCompleteService
             $results = array_merge($results, $this->searchGroups($query, $limit));
         }

-        return array_slice($results, 0, $limit);
+        return array_slice($results, 0, $limit, true);
     }
 }
"""

DEMO_CONTEXT_FILES = {
    "AliasRepository.php": """\
class AliasRepository
{
    public function findByQuery(string $query): Collection
    {
        return Alias::where('address', 'LIKE', "%{$query}%")
                    ->orWhere('label', 'LIKE', "%{$query}%")
                    ->get();  // limit 없음
    }
}
""",
}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="PR Review Assistant Agent")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--demo", action="store_true", help="내장 샘플 PR로 테스트")
    group.add_argument("--diff", help="분석할 diff 파일 경로")

    parser.add_argument("--context", nargs="+", help="참고할 컨텍스트 파일 경로 목록")
    parser.add_argument("--checklist", nargs="+",
                        choices=VALID_CHECKLIST_ITEMS,
                        help="집중 검토 항목 (미지정 시 전체)")
    parser.add_argument("--repo", default="", help="레포지토리명 (예: org/repo)")
    parser.add_argument("--pr-number", type=int, help="PR 번호")
    parser.add_argument("--pr-title", default="", help="PR 제목")
    parser.add_argument("--pr-description", default="", help="PR 설명")
    parser.add_argument("--output", help="결과 저장 파일 경로")

    args = parser.parse_args()

    if args.demo:
        result = run_pr_review(
            diff_text=DEMO_DIFF,
            pr_title=DEMO_PR_TITLE,
            pr_description=DEMO_PR_DESCRIPTION,
            context_files=DEMO_CONTEXT_FILES,
            repo="your-org/your-repo",
            pr_number=1234,
        )
    else:
        with open(args.diff, "r", encoding="utf-8") as f:
            diff_text = f.read()

        context_files = {}
        for fpath in (args.context or []):
            with open(fpath, "r", encoding="utf-8") as f:
                context_files[fpath] = f.read()

        result = run_pr_review(
            diff_text=diff_text,
            pr_title=args.pr_title,
            pr_description=args.pr_description,
            context_files=context_files,
            checklist=args.checklist,
            repo=args.repo,
            pr_number=args.pr_number,
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
