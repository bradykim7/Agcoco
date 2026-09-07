#!/usr/bin/env python3
"""Offline checks; no launchd registration, remote calls, or destructive commands."""

import json
import os
from pathlib import Path
import plistlib
import shlex
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
checks = 0
for hook in [ROOT / "hooks/block-dangerous-git.sh",
             ROOT / "skills/misc/git-guardrails-claude-code/scripts/block-dangerous-git.sh",
             ROOT / "plugins/git-tools/skills/git-guardrails-claude-code/scripts/block-dangerous-git.sh"]:
    blocked = [
        "git commit -m example", "git commit --amend", "git push origin main",
        "git -C /tmp/example push origin main",
        "git -C '/tmp/path with spaces' -c core.hooksPath=/tmp/hooks commit -m example",
        "git -C/tmp/example -ccore.hooksPath=/tmp/hooks commit --amend",
        "git --git-dir=/tmp/example/.git --work-tree=/tmp/example reset --hard",
        "git --git-dir /tmp/example/.git --no-pager reset HEAD --hard",
        "git clean -df", "git -C /tmp/example clean -xffd", "git clean --force",
        "git restore --source=HEAD -- .", "git checkout -- .",
        "git --no-pager branch -D main", "git branch --force --delete master",
        "git -C /tmp/example filter-repo --path example", "git rebase origin/main",
        "git status && git -C /tmp/example push", "git status\ngit commit -m example",
        "(git -C /tmp/example commit -m example)",
        "if true; then git -C /tmp/example commit -m example; fi",
        "command -- git -C /tmp/example commit -m example",
        "command -p git -C /tmp/example commit -m example",
        "exec -a example git -C /tmp/example commit -m example",
        "env FOO=bar git -C /tmp/example commit -m example",
        "sudo -u example git -C /tmp/example push", "/usr/bin/git -C /tmp/example push",
        "bash -lc 'git -C /tmp/example commit -m example'",
        "printf ok # comment\ngit commit -m example",
        "printf ok # comment\ngit -C /tmp/example push origin main",
        ">/tmp/agcoco-review.log git commit -m example",
        "2>/tmp/agcoco-review.log git -C /tmp/example push",
        "git >/tmp/agcoco-review.log commit -m example",
        'printf "%s\\n" "$(git push origin main)"',
        'RESULT="$(git commit -m example)"',
        'printf "%s" "$(printf "%s" "$(git push)")"',
        'printf "%s" `git push`',
        "cat <(git push)",
        "cat <<EOF\nWe're ready.\n$(git push)\nEOF",
        "cat <<'EOF'\nWe're ready.\nEOF\ngit commit -m example",
        "cat <<-'EOF'\n\tWe're ready.\n\tEOF\ngit push",
        "printf '한글' # comment\ngit push",
        "command -- env FOO=bar git push",
        'g"it" \'com\'mit -m example',
        "gi\\\nt pu\\\nsh",
        'bash -lc \'printf ok # comment\ngit push\'',
        'git -C "$repo" commit -m example',
        'git "$operation"', '"$executable" status', 'bash -c "$script"',
        "git $'push'", 'git $"push"', 'git reset "$mode"',
        "cat <<'EOF'\nmissing delimiter",
        'bash -c "printf \'%s\' \\"\\$(git push)\\""',
        "git commit -m 'unterminated",
    ]
    allowed = [
        "git status --short", "git -C /tmp/example diff", "git -c color.ui=false log -1",
        "git --no-pager log -1", "git clean -nd", "git checkout feature/example",
        "git restore file.txt", "git reset --soft HEAD~1",
        "git log -1 --format='Document git push usage'",
        "printf '%s' 'git commit -m example'", "printf '%s' git push",
        "echo 'git -C /tmp/example push'", "git status # git push origin main",
        "bash -lc 'git -C /tmp/example status'", "git --help commit", "command -v git",
        "cat <<'EOF'\nWe're ready.\nEOF",
        "cat <<'EOF'\n$(git push)\n`git commit`\nEOF",
        'cat <<"EOF"\nWe\'re ready.\n$(git push)\nEOF',
        "cat <<\\EOF\nWe're ready.\n$(git push)\nEOF",
        "cat <<-'EOF'\n\tWe're ready.\n\tEOF",
        "cat <<EOF\nWe're ready.\n$(git status)\nEOF",
        "cat <<'ONE' <<'TWO'\nWe're ready.\nONE\n$(git push)\nTWO",
        "printf '%s\\n' ';' git push", "printf '%s\\n' '(' git push ')'",
        "printf '%s\\n' '#' git push",
        "printf '한글' # comment\ngit status",
        ">/tmp/agcoco-review.log git status",
        'git -C "$repo" status',
        'printf "%s" "$(git status)"',
        "bash -lc \"cat <<'EOF'\nWe're ready.\nEOF\"",
        "printf '%s' ''", 'printf "%s" ""',
        'printf "%s" "$HOME"', "printf '%s' $'git push'",
        'echo $((1 + 2))', '[[ -f README.md ]] && git status',
        'bash -c "printf \'%s\' \'\\$(git push)\'"',
    ]
    for command, expected in [(c, 2) for c in blocked] + [(c, 0) for c in allowed]:
        result = subprocess.run(["bash", str(hook)], text=True, capture_output=True,
                                input=json.dumps({"tool_input": {"command": command}}))
        assert result.returncode == expected, (hook, command, result.stderr)
        checks += 1

with tempfile.TemporaryDirectory(prefix="agcoco-parser-") as directory:
    guard = ROOT / "hooks/git-command-guard.py"
    # A missing or broken parser must not silently disable the guard.
    for scenario in ["missing", "invalid JSON", "invalid AST"]:
        parser = Path(directory) / "shfmt"
        if scenario != "missing":
            parser.write_text("#!/bin/sh\nprintf '%s' " + shlex.quote(
                "not JSON" if scenario == "invalid JSON" else '{"Type":"Unknown"}'))
            parser.chmod(0o755)
        result = subprocess.run([sys.executable, "-B", str(guard), "git status", "main,master"],
                                env=dict(os.environ, PATH=directory), text=True, capture_output=True)
        assert result.returncode == 2 and "BLOCKED" in result.stderr, (scenario, result.stderr)
        checks += 1

for command, expected in [
    ("rm -rf /", 2), ("rm -rf ~", 2), ("rm -rf ~/", 2),
    ("rm -rf ~/ && echo done", 2), ("rm -rf ~/ /tmp/example", 2),
    ("rm -rf /tmp/example", 0), ("git status --short", 0),
]:
    result = subprocess.run(["bash", str(ROOT / "hooks/block-dangerous-git.sh")],
                            input=json.dumps({"tool_input": {"command": command}}),
                            text=True, capture_output=True)
    assert result.returncode == expected, (command, result.stderr)
    checks += 1

# Run the actual parsing block, without the install/launchctl steps.
setup = (ROOT / "scripts/jira-daily-setup.sh").read_text()
schedule = setup[setup.index('TIMES_INPUT="${TIMES_INPUT:-'):setup.index('info "스케줄:')]
parse = "error() { printf '%s\\n' \"$1\" >&2; };\n" + schedule + '\nprintf \'%s\' "$SCHEDULE_DICTS"'
for value, expected_times in [("", [(8, 30), (13, 30)]), ("08:09", [(8, 9)]),
                               ("00:00,23:59", [(0, 0), (23, 59)])]:
    result = subprocess.run(["bash", "-c", parse], env=dict(os.environ, TIMES_INPUT=value),
                            text=True, capture_output=True)
    assert result.returncode == 0 and not result.stderr, (value, result.stderr)
    entries = plistlib.loads(("<plist><array>" + result.stdout + "</array></plist>").encode())
    assert [(e["Hour"], e["Minute"], e["Weekday"]) for e in entries] == [
        (hour, minute, day) for hour, minute in expected_times for day in range(1, 6)]
    checks += 1
for value in ["08:99", "24:00", "99:99", "8:3", "-1:30", "aa:00"]:
    result = subprocess.run(["bash", "-c", parse], env=dict(os.environ, TIMES_INPUT=value),
                            text=True, capture_output=True)
    assert result.returncode == 1 and result.stderr, value
    checks += 1

installer = (ROOT / "install.sh").read_text()
function = installer[installer.index("install_tool() {"):installer.index('\nif [ ! -d "$TOOLS_DIR" ]; then')]
with tempfile.TemporaryDirectory(prefix="agcoco-shell-") as directory:
    work = Path(directory)
    source = work / "source"
    source.mkdir()
    destination = work / "target"
    destination.mkdir()
    (destination / "current").write_text("current data")
    old_backup = work / "target.bak"
    old_backup.mkdir()
    (old_backup / "original").write_text("older data")
    (work / "target.bak.1").symlink_to(work / "missing")
    tool = work / "test.sh"
    tool.write_text(f"TOOL_NAME=Test\nTOOL_CMD=true\nTOOL_DIR={shlex.quote(directory)}\nTOOL_SYMLINKS=('target=source')\n")
    script = f"set -e\nDOTFILES_DIR={shlex.quote(directory)}\nINSTALLED_TOOLS=()\nINSTALLED_SYMLINKS=()\n{function}\ninstall_tool {shlex.quote(str(tool))}\n"
    result = subprocess.run(["bash", "-c", script], text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    assert destination.is_symlink() and destination.resolve() == source.resolve(), result.stdout
    assert (old_backup / "original").read_text() == "older data"
    assert (work / "target.bak.1").is_symlink()
    assert (work / "target.bak.2/current").read_text() == "current data"
    checks += 1

    for language in ["Unknown", "PHP"]:
        project = work / language
        project.mkdir()
        if language == "PHP":
            (project / "composer.json").write_text("{}")
        result = subprocess.run(["bash", str(ROOT / "install.sh"), "init", str(project)],
                                text=True, capture_output=True)
        assert result.returncode == 0, result.stderr
        document = (project / "CLAUDE.md").read_text()
        assert f"**Language**: {language}" in document
        assert "├── (empty)" in document
        checks += 1

with tempfile.TemporaryDirectory(prefix="agcoco-pack-") as directory:
    work = Path(directory)
    for folder in ["scripts", "commands", "skills/engineering/sample", "agents/claude-code",
                   "plugins/demo/commands", "plugins/demo/skills/sample", "plugins/demo/agents"]:
        (work / folder).mkdir(parents=True)
    shutil.copyfile(ROOT / "scripts/check-plugin-sync.sh", work / "scripts/check-plugin-sync.sh")
    for source, target, data in [
        ("commands/check.md", "plugins/demo/commands/check.md", "Use `reviewer`.\n"),
        ("agents/claude-code/reviewer.md", "plugins/demo/agents/reviewer.md", "reviewer\n"),
        ("skills/engineering/sample/SKILL.md", "plugins/demo/skills/sample/SKILL.md", "sample\n"),
    ]:
        (work / source).write_text(data)
        (work / target).write_text(data)
    for scenario, expected in [("synced", 0), ("skill drift", 1), ("missing agent", 1)]:
        skill = work / "plugins/demo/skills/sample/SKILL.md"
        if scenario == "skill drift":
            skill.write_text("drift\n")
        elif scenario == "missing agent":
            skill.write_text("sample\n")
            (work / "plugins/demo/agents/reviewer.md").unlink()
        result = subprocess.run(["bash", str(work / "scripts/check-plugin-sync.sh")],
                                text=True, capture_output=True)
        assert result.returncode == expected, (scenario, result.stdout, result.stderr)
        checks += 1

print(f"PASS: {checks} shell/plugin regression checks")
