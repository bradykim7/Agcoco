"""Inspect shell command text without executing it. Exit 2 for blocked Git operations."""

import json
import os
import re
import subprocess
import sys


def nodes(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from nodes(child)


def literal(word, quoted=False):
    # Quote removal only; variables, substitutions and dollar-quotes stay unknown.
    values = []
    for part in word.get("Parts", []):
        kind = part["Type"]
        if part.get("Dollar") is True:
            return None
        if kind == "Lit":
            value = part["Value"].replace("\\\n", "")
            value = re.sub(r'\\([$`"\\])' if quoted else r"\\(.)", r"\1", value)
        elif kind == "SglQuoted":
            value = part.get("Value", "")
        elif kind == "DblQuoted":
            value = literal(part, quoted=True)
        else:
            return None
        if value is None:
            return None
        values.append(value)
    return "".join(values)


def commands(text):
    # ponytail: inspect syntax, not execution; aliases and external script bodies
    # still require execution-level controls. shfmt parses without running code.
    try:
        parsed = subprocess.run(["shfmt", "-ln=bash", "-to-json"], input=text,
                                encoding="utf-8", capture_output=True, timeout=5)
    except FileNotFoundError:
        raise ValueError("shfmt is required; install shfmt 3 (macOS: brew install shfmt)") from None
    if parsed.returncode:
        raise ValueError(parsed.stderr.strip() or "shfmt could not parse the command")
    tree = json.loads(parsed.stdout)
    if tree.get("Type") != "File":
        raise ValueError("unexpected shfmt syntax tree")
    for node in nodes(tree):
        if node.get("Type") == "CallExpr" and node.get("Args"):
            yield [literal(word) for word in node["Args"]]


def check(text, protected_branches):
    for words in commands(text):
        reason = check_words(words, protected_branches)
        if reason:
            return reason
    return None


def check_words(words, protected_branches):
    if not words:
        return None
    if words[0] is None:
        raise ValueError("dynamic executable or Git operation; use a literal command")
    executable = os.path.basename(words.pop(0))
    if executable in {"command", "builtin", "exec", "env", "sudo"}:
        while words and words[0] is not None and (words[0].startswith("-") or "=" in words[0]):
            option = words.pop(0)
            if executable == "command" and option in {"-v", "-V"}:
                return None
            if option in {"-u", "-g", "-h", "-p", "-C", "-a", "--unset", "--chdir", "--user", "--group", "--host", "--prompt"} and executable != "command" and words:
                words.pop(0)
        return check_words(words, protected_branches)
    if executable in {"sh", "bash", "zsh", "dash"}:
        for index, option in enumerate(words):
            if option is None:
                raise ValueError("dynamic shell argument; use a literal command")
            if not option.startswith("-") or option == "--":
                break
            if not option.startswith("--") and "c" in option and index + 1 < len(words):
                script = words[index + 1]
                if script is None:
                    raise ValueError("dynamic shell script; use a literal command")
                return check(script, protected_branches)
        return None
    if executable != "git":
        return None
    while words and words[0] is not None and words[0].startswith("-"):
        option = words.pop(0)
        if option in {"--help", "--version", "-h"}:
            return None
        if option in {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--config-env"}:
            if not words:
                raise ValueError(f"missing value for git {option}")
            words.pop(0)
    if not words:
        return None
    operation, *args = words
    if operation is None:
        raise ValueError("dynamic Git operation; use a literal command")
    options = args[:args.index("--")] if "--" in args else args
    if operation in {"commit", "push"}:
        return f"git {operation} is reserved for the user; run it manually."
    if operation in {"filter-branch", "filter-repo"}:
        return "Git history rewriting is blocked."
    if operation in {"rebase", "reset", "clean", "checkout", "restore", "branch"} and None in args:
        raise ValueError("dynamic arguments to a destructive Git operation; use literal arguments")
    if operation == "rebase" and any(arg.rsplit("/", 1)[-1] in {"main", "master"} for arg in args):
        return "Rebasing onto main/master is blocked."
    if operation == "reset" and "--hard" in options:
        return "git reset --hard discards uncommitted work."
    if operation == "clean" and any(arg == "--force" or re.fullmatch(r"-[A-Za-z]*f[A-Za-z]*", arg) for arg in options):
        return "Forced git clean removes untracked files."
    if operation in {"checkout", "restore"} and "." in args:
        return "git checkout/restore . discards uncommitted changes."
    force_delete = "-D" in options or ("--delete" in options and "--force" in options)
    if operation == "branch" and force_delete and (protected_branches == "*" or set(args) & {"main", "master"}):
        return "Force-deleting a protected branch is blocked."
    return None


if __name__ == "__main__":
    try:
        reason = check(sys.argv[1], sys.argv[2])
    except (ValueError, OSError, RecursionError, subprocess.TimeoutExpired) as error:
        reason = f"Cannot safely inspect shell command: {error}"
    if reason:
        print(f"BLOCKED: {reason}", file=sys.stderr)
        sys.exit(2)
