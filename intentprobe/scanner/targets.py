"""Filesystem target collection for scanner CLI paths."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


DEFAULT_MAX_FILES = 40
DEFAULT_MAX_FILE_BYTES = 200_000
DEFAULT_MAX_TEXT_CHARS = 16_000

SKIP_DIRS = {
    ".git",
    ".hg",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "venv",
}

JSON_CONFIG_NAMES = {
    ".mcp.json",
    "claude_desktop_config.json",
    "mcp-config.json",
    "mcp.json",
}
PACKAGE_NAMES = {"package.json"}
SKILL_NAMES = {"SKILL.md", "skill.md"}
README_NAMES = {"README", "README.md", "readme.md", "Readme.md"}
TEXT_SUFFIXES = {".md", ".txt", ".json"}


def safe_subject_id(prefix: str, path: Path) -> str:
    raw = f"{prefix}-{path.as_posix()}"
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", raw).strip("-") or prefix


def trim_text(text: str, max_chars: int = DEFAULT_MAX_TEXT_CHARS) -> str:
    if len(text) <= max_chars:
        return text
    head = max_chars // 2
    tail = max_chars - head
    return (
        text[:head]
        + f"\n\n[INTENTPROBE_TRUNCATED {len(text) - max_chars} CHARS]\n\n"
        + text[-tail:]
    )


def read_limited_text(path: Path, max_file_bytes: int, max_text_chars: int = DEFAULT_MAX_TEXT_CHARS) -> str:
    raw = path.read_bytes()
    if len(raw) > max_file_bytes:
        half = max_file_bytes // 2
        raw = raw[:half] + b"\n\n[INTENTPROBE_FILE_TRUNCATED]\n\n" + raw[-half:]
    text = raw.decode("utf-8", errors="replace")
    return trim_text(text, max_text_chars)


def load_json(path: Path, max_file_bytes: int) -> Any | None:
    try:
        return json.loads(read_limited_text(path, max_file_bytes, max_file_bytes))
    except json.JSONDecodeError:
        return None


def interesting_package_fields(data: dict[str, Any]) -> dict[str, Any]:
    fields = (
        "name",
        "version",
        "description",
        "keywords",
        "type",
        "main",
        "module",
        "bin",
        "scripts",
        "exports",
        "dependencies",
        "optionalDependencies",
        "peerDependencies",
        "mcp",
    )
    return {key: data[key] for key in fields if key in data}


def json_payload_for_path(path: Path, data: Any) -> Any:
    if not isinstance(data, dict):
        return data

    lower_name = path.name.lower()
    payload = dict(data)
    payload.setdefault("source", "filesystem")
    payload.setdefault("path", str(path))

    if lower_name == "package.json":
        selected = interesting_package_fields(data)
        return {
            "kind": "package_manifest",
            "name": data.get("name"),
            "description": data.get("description"),
            "source": "filesystem",
            "path": str(path),
            "package_json": selected,
        }

    return payload


def is_candidate_file(path: Path, include_readme: bool) -> bool:
    name = path.name
    lower_name = name.lower()
    if name in SKILL_NAMES:
        return True
    if lower_name in PACKAGE_NAMES or lower_name in JSON_CONFIG_NAMES:
        return True
    if include_readme and name in README_NAMES:
        return True
    if path.suffix.lower() == ".json" and any(part in lower_name for part in ("mcp", "tool", "skill")):
        return True
    return False


def sort_key_for_candidate(path: Path) -> tuple[int, str]:
    name = path.name
    lower_name = name.lower()
    if lower_name in JSON_CONFIG_NAMES:
        priority = 0
    elif lower_name == "package.json":
        priority = 1
    elif name in SKILL_NAMES:
        priority = 2
    elif name in README_NAMES:
        priority = 3
    else:
        priority = 4
    return (priority, path.as_posix())


def walk_candidate_files(root: Path, *, include_readme: bool, max_files: int) -> list[Path]:
    candidates: list[Path] = []
    for path in root.rglob("*"):
        if len(candidates) >= max_files * 4:
            break
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if not path.is_file():
            continue
        if is_candidate_file(path, include_readme):
            candidates.append(path)
    return sorted(candidates, key=sort_key_for_candidate)[:max_files]


def subjects_from_json_file(path: Path, data: Any, subject_id: str):
    from .hook import normalize_payload

    return normalize_payload(json_payload_for_path(path, data), subject_id=subject_id)


def subject_from_text_file(path: Path, root: Path, *, kind: str, max_file_bytes: int):
    from .hook import ScanSubject

    try:
        rel = path.relative_to(root)
    except ValueError:
        rel = path
    text = read_limited_text(path, max_file_bytes)
    return ScanSubject(
        subject_id=safe_subject_id(kind, rel),
        kind=kind,
        name=path.name,
        source="filesystem",
        path=str(path),
        text=text,
    )


def subjects_from_file(path: Path, root: Path, *, max_file_bytes: int):
    name = path.name
    lower_name = name.lower()
    subject_id = safe_subject_id("file", path.relative_to(root) if path.is_relative_to(root) else path)

    if path.suffix.lower() == ".json" or lower_name in PACKAGE_NAMES or lower_name in JSON_CONFIG_NAMES:
        data = load_json(path, max_file_bytes)
        if data is not None:
            return subjects_from_json_file(path, data, subject_id)

    if name in SKILL_NAMES:
        return [subject_from_text_file(path, root, kind="skill_markdown", max_file_bytes=max_file_bytes)]
    if name in README_NAMES:
        return [subject_from_text_file(path, root, kind="readme", max_file_bytes=max_file_bytes)]
    if path.suffix.lower() in TEXT_SUFFIXES:
        return [subject_from_text_file(path, root, kind="file_text", max_file_bytes=max_file_bytes)]

    raise SystemExit(f"Unsupported target file type: {path}")


def collect_subjects_from_path(
    path: Path,
    *,
    max_files: int = DEFAULT_MAX_FILES,
    max_file_bytes: int = DEFAULT_MAX_FILE_BYTES,
    include_readme: bool = True,
):
    target = path.expanduser().resolve()
    if not target.exists():
        raise SystemExit(f"Target path does not exist: {path}")

    subjects = []
    if target.is_file():
        subjects.extend(subjects_from_file(target, target.parent, max_file_bytes=max_file_bytes))
    else:
        candidates = walk_candidate_files(target, include_readme=include_readme, max_files=max_files)
        for candidate in candidates:
            subjects.extend(subjects_from_file(candidate, target, max_file_bytes=max_file_bytes))

    if not subjects:
        raise SystemExit(
            f"No scannable package, MCP, skill, README, or JSON files found under {target}"
        )
    return subjects
