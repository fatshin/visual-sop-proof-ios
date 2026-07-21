from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import zipfile
from dataclasses import dataclass
from datetime import date
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


MAX_FILE_BYTES = 1_000_000
MAX_IMPORT_FILES = 500
MAX_ARCHIVE_BYTES = 25_000_000
MAX_RECORD_CHARS = 800

BIRTH_PRECISIONS = {"exact", "approximate", "unknown"}

THEME_TERMS = {
    "仕事": ("仕事", "転職", "職場", "career", "job", "role", "work", "product", "会社", "プロジェクト"),
    "関係": ("関係", "恋愛", "家族", "友人", "partner", "relationship", "人間関係"),
    "健康": ("健康", "体調", "食事", "睡眠", "運動", "health", "recovery"),
    "お金": ("お金", "投資", "支出", "収入", "money", "budget", "資産"),
    "学び": ("学び", "勉強", "研究", "資格", "learn", "study", "research"),
    "変化": ("変化", "迷い", "決断", "選択", "change", "decision", "move"),
}

SENSITIVE_PATTERN = re.compile(
    r"(?:\bpassword\b|\bpasswd\b|api[_ -]?key|apikey|\b(?:secret|token)\b\s*[:=]|authorization\s*:|"
    r"bearer\s+|パスワード|暗証番号|-----BEGIN [A-Z ]*PRIVATE KEY-----|"
    r"\bsk-[A-Za-z0-9_-]{16,}|\bAKIA[0-9A-Z]{16}\b|\bgh[pousr]_[A-Za-z0-9]{20,})",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class MemoryRecord:
    id: str
    source: str
    title: str
    text: str
    path: str = ""


@dataclass(frozen=True)
class BirthContext:
    birth_date: str
    birth_time: str
    birth_place: str
    time_precision: str = "approximate"
    place_precision: str = "approximate"


def validate_birth_context(context: BirthContext) -> date:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", context.birth_date):
        raise ValueError("Birth date must use YYYY-MM-DD")
    try:
        parsed = date.fromisoformat(context.birth_date)
    except ValueError as error:
        raise ValueError("Birth date must be a valid ISO date (YYYY-MM-DD)") from error
    if parsed > date.today():
        raise ValueError("Birth date cannot be in the future")
    if not context.birth_time.strip():
        raise ValueError("Birth time is required; use 'unknown' when necessary")
    if not context.birth_place.strip():
        raise ValueError("Birth place is required; use 'unknown' when necessary")
    if context.time_precision not in BIRTH_PRECISIONS:
        raise ValueError("Time precision must be exact, approximate, or unknown")
    if context.place_precision not in BIRTH_PRECISIONS:
        raise ValueError("Place precision must be exact, approximate, or unknown")
    return parsed


def _record(source: str, title: str, text: str, path: str = "") -> MemoryRecord | None:
    cleaned = re.sub(r"\s+", " ", text).strip()
    if not cleaned or _looks_sensitive(f"{title}\n{path}\n{cleaned}"):
        return None
    cleaned = cleaned[:MAX_RECORD_CHARS]
    digest_source = json.dumps(
        {"source": source, "path": path, "title": title, "text": cleaned},
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    digest = hashlib.sha256(digest_source.encode()).hexdigest()[:12]
    return MemoryRecord(digest, source, title[:120], cleaned, path)


def _looks_sensitive(text: str) -> bool:
    return SENSITIVE_PATTERN.search(text) is not None


def _safe_archive_name(name: str) -> bool:
    if "\\" in name:
        return False
    path = PurePosixPath(name)
    return not path.is_absolute() and ".." not in path.parts


def parse_memory_summary(text: str, source: str = "ChatGPT Memory") -> list[MemoryRecord]:
    records: list[MemoryRecord] = []
    for index, line in enumerate(text.splitlines(), 1):
        cleaned = re.sub(r"^\s*(?:[-*•]|\d+[.)])\s*", "", line).strip()
        if len(cleaned) < 8:
            continue
        item = _record(source, f"Memory {index}", cleaned)
        if item:
            records.append(item)
    return records[:MAX_IMPORT_FILES]


def import_obsidian_vault(root: str | Path) -> list[MemoryRecord]:
    base = Path(root).expanduser().resolve()
    if not base.is_dir():
        raise ValueError("Obsidian vault must be an existing folder")

    records: list[MemoryRecord] = []
    candidates = sorted(base.rglob("*.md"))
    for path in candidates:
        if len(records) >= MAX_IMPORT_FILES:
            break
        try:
            if path.is_symlink() or not path.is_file():
                continue
            relative = path.relative_to(base)
            if any(part.startswith(".") for part in relative.parts):
                continue
            resolved = path.resolve(strict=True)
            if not resolved.is_relative_to(base):
                continue
            resolved_relative = resolved.relative_to(base)
            if any(part.startswith(".") for part in resolved_relative.parts):
                continue
            if resolved.stat().st_size > MAX_FILE_BYTES:
                continue
            text = resolved.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        title = _markdown_title(text) or path.stem
        item = _record("Obsidian", title, _markdown_body(text), str(relative))
        if item:
            records.append(item)
    return records


def _markdown_title(text: str) -> str:
    match = re.search(r"(?m)^#\s+(.+?)\s*$", text)
    return match.group(1).strip() if match else ""


def _markdown_body(text: str) -> str:
    frontmatter = re.match(r"\A---\s*\n(.*?)\n---\s*(?:\n|\Z)", text, flags=re.DOTALL)
    if frontmatter and re.search(r"(?m)^[A-Za-z0-9_-]+\s*:", frontmatter.group(1)):
        text = text[frontmatter.end() :]
    text = re.sub(r"(?m)\A#\s+.+\n?", "", text, count=1)
    text = re.sub(r"(?m)^#{1,6}\s+", "", text)
    text = re.sub(r"!?\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", r"\1", text)
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    return text


def import_chatgpt_export(path: str | Path) -> list[MemoryRecord]:
    source = Path(path).expanduser().resolve()
    if not source.is_file():
        raise ValueError("ChatGPT export must be a JSON, text, Markdown, or ZIP file")
    if source.stat().st_size > MAX_ARCHIVE_BYTES:
        raise ValueError("ChatGPT export exceeds the 25 MB local import limit")

    suffix = source.suffix.lower()
    if suffix == ".zip":
        payloads: list[tuple[str, bytes]] = []
        with zipfile.ZipFile(source) as archive:
            total = 0
            for info in archive.infolist():
                name = info.filename
                if not _safe_archive_name(name):
                    raise ValueError("Unsafe path found in ChatGPT export")
                filename = PurePosixPath(name).name
                if not re.fullmatch(r"conversations(?:-\d+)?\.json", filename):
                    continue
                remaining = MAX_ARCHIVE_BYTES - total
                if info.file_size > remaining:
                    raise ValueError("Uncompressed conversation data exceeds 25 MB")
                with archive.open(info) as member:
                    payload = member.read(info.file_size + 1)
                if len(payload) != info.file_size:
                    raise ValueError("Invalid or oversized conversation data in ChatGPT export")
                total += len(payload)
                payloads.append((name, payload))
        if not payloads:
            raise ValueError("No conversations.json file found in ChatGPT export")
        records: list[MemoryRecord] = []
        for name, payload in payloads:
            records.extend(_parse_conversations_json(payload.decode("utf-8"), name))
        return records[:MAX_IMPORT_FILES]
    if suffix == ".json":
        return _parse_conversations_json(source.read_text(encoding="utf-8"), source.name)
    if suffix in {".txt", ".md", ".markdown"}:
        return parse_memory_summary(source.read_text(encoding="utf-8"), "ChatGPT Memory")
    raise ValueError("Unsupported ChatGPT export type")


def _parse_conversations_json(text: str, path: str = "conversations.json") -> list[MemoryRecord]:
    try:
        data = json.loads(text)
    except json.JSONDecodeError as error:
        raise ValueError("ChatGPT conversation JSON is invalid") from error
    if isinstance(data, dict):
        data = data.get("conversations", [data])
    if not isinstance(data, list):
        raise ValueError("ChatGPT conversation JSON must contain a list")

    records: list[MemoryRecord] = []
    for conversation in data:
        if not isinstance(conversation, dict):
            continue
        title = str(conversation.get("title") or "Untitled conversation")
        mapping = conversation.get("mapping")
        if not isinstance(mapping, dict):
            continue
        user_parts: list[str] = []
        for node in mapping.values():
            if not isinstance(node, dict):
                continue
            message = node.get("message")
            if not isinstance(message, dict):
                continue
            author = message.get("author") or {}
            if author.get("role") != "user":
                continue
            content = message.get("content") or {}
            parts = content.get("parts") or []
            for part in parts:
                if isinstance(part, str) and part.strip():
                    user_parts.append(part)
        item = _record("ChatGPT conversation", title, "\n".join(user_parts), path)
        if item:
            records.append(item)
        if len(records) >= MAX_IMPORT_FILES:
            break
    return records


def detect_themes(records: Iterable[MemoryRecord]) -> list[dict[str, Any]]:
    combined = " ".join(record.text.lower() for record in records)
    results = []
    for theme, terms in THEME_TERMS.items():
        hits = sum(combined.count(term.lower()) for term in terms)
        if hits:
            results.append({"theme": theme, "mentions": hits})
    return sorted(results, key=lambda item: (-item["mentions"], item["theme"]))


def _run_shared_engine(payload: dict[str, Any]) -> Any:
    bridge = Path(__file__).resolve().parent / "site" / "cli_bridge.mjs"
    if not bridge.is_file():
        raise RuntimeError(f"Shared reading engine is missing: {bridge}")
    try:
        result = subprocess.run(
            ["node", str(bridge)],
            input=json.dumps(payload, ensure_ascii=False),
            text=True,
            capture_output=True,
            check=False,
            timeout=30,
        )
    except FileNotFoundError as error:
        raise RuntimeError("Node.js 22.13 or newer is required for the shared reading engine") from error
    except subprocess.TimeoutExpired as error:
        raise RuntimeError("Shared reading engine timed out after 30 seconds") from error
    if result.returncode != 0:
        detail = result.stderr.strip().splitlines()[-1] if result.stderr.strip() else "unknown error"
        raise RuntimeError(f"Shared reading engine failed: {detail}")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise RuntimeError("Shared reading engine returned invalid JSON") from error


def create_reading(
    question: str,
    records: list[MemoryRecord],
    birth: BirthContext,
    language: str = "en",
) -> dict[str, Any]:
    if language not in {"en", "ja"}:
        raise ValueError("Language must be en or ja")
    validate_birth_context(birth)
    question = re.sub(r"\s+", " ", question).strip()
    if len(question) < 4:
        raise ValueError("Question must contain at least 4 characters")
    if not records:
        raise ValueError("Select at least one memory before creating a reading")
    if len(records) > MAX_IMPORT_FILES:
        raise ValueError("Too many memories selected")

    return _run_shared_engine(
        {
            "operation": "reading",
            "question": question,
            "memories": [
                {
                    "id": record.id,
                    "source": record.source,
                    "title": record.title,
                    "text": record.text,
                    "path": record.path,
                }
                for record in records
            ],
            "themes": detect_themes(records),
            "birth": {
                "date": birth.birth_date,
                "time": birth.birth_time.strip(),
                "place": birth.birth_place.strip(),
                "timePrecision": birth.time_precision,
                "placePrecision": birth.place_precision,
            },
            "lang": language,
        }
    )


def export_obsidian_markdown(reading: dict[str, Any], records: list[MemoryRecord]) -> str:
    del records  # Kept for backward compatibility; reading already contains its cited memories.
    markdown = _run_shared_engine({"operation": "markdown", "reading": reading})
    if not isinstance(markdown, str):
        raise RuntimeError("Shared reading engine returned invalid Markdown")
    return markdown


def sample_records(language: str = "ja") -> list[MemoryRecord]:
    samples_ja = [
        ("Obsidian", "転職について考えた日", "今の仕事を続ける安心と、新しい役割へ挑戦したい気持ちの間で迷っている。", "Daily/2026-07-12.md"),
        ("Obsidian", "半年後にしたいこと", "研究だけでなく、利用者へ届くプロダクトを自分の責任で育てたい。", "Career/半年後.md"),
        ("ChatGPT Memory", "Memory 1", "大きな決断では、選択肢を比較できる表と撤退条件があると安心して進められる。", ""),
        ("ChatGPT conversation", "働き方の相談", "転職する前に、小さな社内プロジェクトで自分の仮説を試せないだろうか。", "conversations.json"),
    ]
    samples_en = [
        ("Obsidian", "The day I considered changing roles", "I feel torn between the safety of continuing my current work and the desire to take responsibility for a new role.", "Daily/2026-07-12.md"),
        ("Obsidian", "What I want six months from now", "I want to do more than research. I want to own and grow a product that reaches real users.", "Career/six-months.md"),
        ("ChatGPT Memory", "Decision style", "I move with more confidence when a major decision has comparison criteria and a clear exit condition.", ""),
        ("ChatGPT conversation", "A conversation about how I work", "Before changing jobs, could I test my hypothesis through a small internal project?", "conversations.json"),
    ]
    samples = samples_ja if language == "ja" else samples_en
    return [
        item
        for source, title, text, path in samples
        if (item := _record(source, title, text, path))
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Local-first memory-assisted reflection")
    parser.add_argument("--obsidian", help="Path to an Obsidian vault")
    parser.add_argument("--chatgpt", help="Path to ChatGPT JSON, ZIP, Markdown, or text export")
    parser.add_argument("--memory-text", help="Plain-text ChatGPT memory summary")
    parser.add_argument("--birth-date", required=True, help="Birth date in YYYY-MM-DD format")
    parser.add_argument("--birth-time", required=True, help="Birth time, approximate time, or 'unknown'")
    parser.add_argument("--birth-place", required=True, help="Birth place, approximate area, or 'unknown'")
    parser.add_argument("--time-precision", choices=sorted(BIRTH_PRECISIONS), default="approximate")
    parser.add_argument("--place-precision", choices=sorted(BIRTH_PRECISIONS), default="approximate")
    parser.add_argument("--language", choices=("en", "ja"), default="en")
    parser.add_argument("--question")
    parser.add_argument("--output", help="Write an Obsidian Markdown note")
    parser.add_argument("--demo", action="store_true")
    args = parser.parse_args()

    records: list[MemoryRecord] = []
    if args.demo:
        records.extend(sample_records(args.language))
    if args.obsidian:
        records.extend(import_obsidian_vault(args.obsidian))
    if args.chatgpt:
        records.extend(import_chatgpt_export(args.chatgpt))
    if args.memory_text:
        records.extend(parse_memory_summary(args.memory_text))
    if not records:
        parser.error("provide --demo, --obsidian, --chatgpt, or --memory-text")

    birth = BirthContext(
        birth_date=args.birth_date,
        birth_time=args.birth_time,
        birth_place=args.birth_place,
        time_precision=args.time_precision,
        place_precision=args.place_precision,
    )
    question = args.question or (
        "次の役割へ進む前に、どのような証拠を作るべきですか。"
        if args.language == "ja"
        else "What evidence should I create before moving into my next role?"
    )
    reading = create_reading(question, records, birth, args.language)
    if args.output:
        Path(args.output).write_text(export_obsidian_markdown(reading, records), encoding="utf-8")
    print(json.dumps(reading, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
