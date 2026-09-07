#!/usr/bin/env python3
"""Check the real CLI paths offline with fake API responses."""

import contextlib
import importlib
import io
import json
from pathlib import Path
import sys
import tempfile
import types
from unittest.mock import patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "agents/python"))
reply = None
requests = []


def create_message(**kwargs):
    requests.append(kwargs)
    return types.SimpleNamespace(content=[types.SimpleNamespace(text=json.dumps(reply))])


client = types.SimpleNamespace(messages=types.SimpleNamespace(create=create_message))
sys.modules["anthropic"] = types.SimpleNamespace(Anthropic=lambda **kwargs: client)
valid = {
    "document_summarizer": dict(document_type="meeting", summary="ok", key_points=[], decisions=[],
                                risks=[], open_questions=[], next_actions=[], source_gaps=[]),
    "endpoint_analysis": dict(endpoint=dict(method="GET", path="/test"), summary="ok", request_fields=[],
                              response_fields=[], behavior_notes=[], error_cases=[], dependencies=[],
                              compatibility_risks=[], test_cases=[], documentation_gaps=[]),
    "pr_review_assistant": dict(summary="ok", risk_points=[], missing_tests=[], compatibility_risks=[],
                                questions_for_author=[], safe_suggestions=[]),
    "architecture_review": dict(summary="ok", assumptions=[], strengths=[], risks=[], tradeoffs=[],
                                recommended_changes=[dict(title="replica", priority="high", rationale="availability")],
                                open_questions=[]),
    "consistency_check": dict(summary="ok", compared_sources=dict(source_a="a", source_b="b",
                              record_count_a=0, record_count_b=0), inconsistencies=[],
                              statistics=dict(total_checked=0, total_inconsistent=0, missing_in_source=0,
                                              missing_in_target=0, field_value_mismatch=0),
                              open_questions=[], recommendations=[]),
}


def run_cli(name, payload, args):
    global reply
    reply = payload
    agent = importlib.import_module(f"{name}.agent")
    with patch.object(sys, "argv", ["agent.py", *args]):
        agent.main()


checks = 0
with tempfile.TemporaryDirectory(prefix="agcoco-agents-") as directory:
    output = Path(directory) / "result.json"
    for name, payload in valid.items():
        with contextlib.redirect_stdout(io.StringIO()):
            run_cli(name, payload, ["--demo", "--output", str(output)])
        assert json.loads(output.read_text()) == payload, name
        checks += 1
        missing = dict(payload)
        del missing["summary"]
        list_field = next(key for key, value in payload.items() if isinstance(value, list))
        for bad in [{}, [], None, 1, "unknown", missing, dict(payload, summary=None),
                    dict(payload, unexpected="extra"), dict(payload, **{list_field: None}),
                    dict(payload, **{list_field: [42]})]:
            output.write_text("previous result")
            logs = io.StringIO()
            with contextlib.redirect_stdout(logs):
                try:
                    run_cli(name, bad, ["--demo", "--output", str(output)])
                except ValueError:
                    pass
                else:
                    raise AssertionError(f"{name} accepted invalid response: {bad}")
            assert output.read_text() == "previous result", name
            assert "[분석 완료]" not in logs.getvalue() and "결과 저장됨" not in logs.getvalue(), name
            checks += 1

    for name, key, nested in [
        ("endpoint_analysis", "endpoint", {}),
        ("architecture_review", "recommended_changes", [dict(title="x", priority="urgent", rationale="x")]),
        ("consistency_check", "statistics", dict(valid["consistency_check"]["statistics"], total_checked=True)),
    ]:
        with contextlib.redirect_stdout(io.StringIO()):
            try:
                run_cli(name, dict(valid[name], **{key: nested}), ["--demo"])
            except ValueError:
                pass
            else:
                raise AssertionError(f"{name} accepted malformed nested field")
        checks += 1

    paths = []
    for folder, marker in [("one", "FIRST_SOURCE"), ("two", "SECOND_SOURCE")]:
        path = Path(directory) / folder / "Controller.php"
        path.parent.mkdir()
        path.write_text(marker)
        paths.append(str(path))
    diff = Path(directory) / "change.diff"
    diff.write_text("--- a/test.php\n+++ b/test.php\n@@ -1 +1 @@\n-old\n+new\n")
    for name, args in [("endpoint_analysis", ["--code", *paths]),
                       ("pr_review_assistant", ["--diff", str(diff), "--context", *paths])]:
        with contextlib.redirect_stdout(io.StringIO()):
            run_cli(name, valid[name], args)
        prompt = requests[-1]["messages"][0]["content"]
        assert all(item in prompt for item in [*paths, "FIRST_SOURCE", "SECOND_SOURCE"]), name
        checks += 1

print(f"PASS: {checks} agent checks (no API calls)")
