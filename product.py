from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


MAX_FILE_BYTES = 1_000_000
MAX_IMPORT_FILES = 500
MAX_ARCHIVE_BYTES = 25_000_000
MAX_RECORD_CHARS = 800

DIVINATIONS = (
    ("易経", "水雷屯", "動き出す前に、足場と助けを整える"),
    ("四柱推命", "調候", "強みを押し通すより、環境との釣り合いを取る"),
    ("九星気学", "坎宮", "見えない準備を重ね、焦って結論を急がない"),
    ("宿曜占星術", "栄親", "関係を断つ前に、育てられる縁を見分ける"),
    ("西洋占星術", "土星と水星", "考えを言葉と期限に変えて、現実に照らす"),
    ("タロット", "隠者", "外の正解より、過去の自分が残した手掛かりを読む"),
    ("数秘術", "7", "情報を集める時間と、決める時間を分ける"),
    ("ルーン", "Jera", "結果を急がず、積み重ねが実る周期を尊重する"),
    ("ジオマンシー", "Conjunctio", "一人で閉じず、異なる情報を接続する"),
    ("月相・暦", "上弦", "小さく試し、次の節目で見直す"),
)

THEME_TERMS = {
    "仕事": ("仕事", "転職", "職場", "career", "job", "会社", "プロジェクト"),
    "関係": ("関係", "恋愛", "家族", "友人", "partner", "relationship", "人間関係"),
    "健康": ("健康", "体調", "食事", "睡眠", "運動", "health"),
    "お金": ("お金", "投資", "支出", "収入", "money", "budget", "資産"),
    "学び": ("学び", "勉強", "研究", "資格", "learn", "study"),
    "変化": ("変化", "迷い", "決断", "選択", "change", "decision"),
}

SENSITIVE_PATTERN = re.compile(
    r"(?:password|passwd|api[_ -]?key|apikey|secret|token|authorization\s*:|"
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


def _record(source: str, title: str, text: str, path: str = "") -> MemoryRecord | None:
    cleaned = re.sub(r"\s+", " ", text).strip()
    if not cleaned or _looks_sensitive(f"{title}\n{path}\n{cleaned}"):
        return None
    cleaned = cleaned[:MAX_RECORD_CHARS]
    digest = hashlib.sha256(f"{source}\0{path}\0{title}\0{cleaned}".encode()).hexdigest()[:12]
    return MemoryRecord(digest, source, title[:120], cleaned, path)


def _looks_sensitive(text: str) -> bool:
    return SENSITIVE_PATTERN.search(text) is not None


def _safe_archive_name(name: str) -> bool:
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
        relative = path.relative_to(base)
        if any(part.startswith(".") for part in relative.parts):
            continue
        resolved = path.resolve()
        if not resolved.is_relative_to(base):
            continue
        resolved_relative = resolved.relative_to(base)
        if any(part.startswith(".") for part in resolved_relative.parts):
            continue
        if len(records) >= MAX_IMPORT_FILES:
            break
        if resolved.stat().st_size > MAX_FILE_BYTES:
            continue
        text = resolved.read_text(encoding="utf-8", errors="replace")
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
                total += info.file_size
                if total > MAX_ARCHIVE_BYTES:
                    raise ValueError("Uncompressed conversation data exceeds 25 MB")
                payloads.append((name, archive.read(info)))
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


def create_reading(question: str, records: list[MemoryRecord]) -> dict[str, Any]:
    question = re.sub(r"\s+", " ", question).strip()
    if len(question) < 4:
        raise ValueError("Question must contain at least 4 characters")
    if not records:
        raise ValueError("Select at least one memory before creating a reading")
    if len(records) > MAX_IMPORT_FILES:
        raise ValueError("Too many memories selected")

    themes = detect_themes(records)
    seed = int(hashlib.sha256((question + "|" + "|".join(r.id for r in records)).encode()).hexdigest(), 16)
    selected = []
    for index, (method, symbol, guidance) in enumerate(DIVINATIONS):
        memory = records[(seed + index * 7) % len(records)]
        selected.append(
            {
                "method": method,
                "symbol": symbol,
                "guidance": guidance,
                "memory_id": memory.id,
                "memory_title": memory.title,
                "connection": f"「{memory.text[:90]}」という過去の記録と照らして読みます。",
            }
        )

    leading_themes = [item["theme"] for item in themes[:3]] or ["変化"]
    return {
        "status": "REFLECTION_READY",
        "question": question,
        "memory_count": len(records),
        "source_count": len({record.source for record in records}),
        "themes": themes,
        "readings": selected,
        "synthesis": (
            f"記録には「{'・'.join(leading_themes)}」が繰り返し現れています。"
            "今回の象徴は結論を断定するものではありません。"
            "過去に同じ問いへどう向き合ったかを確認し、次の小さな行動を選ぶための材料です。"
        ),
        "next_step": "24時間以内に確認できる事実を一つ調べ、7日後にこの読みを振り返ってください。",
        "disclaimer": "娯楽と内省のための結果です。医療、法律、投資、安全に関する判断には使用しないでください。",
    }


def export_obsidian_markdown(reading: dict[str, Any], records: list[MemoryRecord]) -> str:
    theme_names = [item["theme"] for item in reading["themes"][:5]]
    lines = [
        "---",
        "type: oracle-council-reading",
        f"status: {reading['status']}",
        f"memory_count: {reading['memory_count']}",
        "themes:",
        *[f"  - {theme}" for theme in theme_names],
        "review_after_days: 7",
        "---",
        "",
        "# Oracle Council リーディング",
        "",
        "## 今回の問い",
        "",
        reading["question"],
        "",
        "## 記憶から見えたテーマ",
        "",
        reading["synthesis"],
        "",
        "## 10の占術による読み",
        "",
    ]
    for item in reading["readings"]:
        lines.extend(
            [
                f"### {item['method']} — {item['symbol']}",
                "",
                item["guidance"] + "。",
                "",
                f"参照した記憶: [[Oracle Memory/{item['memory_title']}]]",
                "",
            ]
        )
    lines.extend(
        [
            "## 次の一歩",
            "",
            reading["next_step"],
            "",
            "## 使用した記憶",
            "",
        ]
    )
    for record in records:
        suffix = f" — `{record.path}`" if record.path else ""
        lines.append(f"- {record.source}: {record.title}{suffix}")
    lines.extend(
        [
            "",
            "## 注意",
            "",
            reading["disclaimer"],
            "",
            "## 7日後の振り返り",
            "",
            "- 実際に確認した事実:",
            "- 取った行動:",
            "- 今読むと違って見える部分:",
            "",
        ]
    )
    return "\n".join(lines)


def sample_records() -> list[MemoryRecord]:
    samples = [
        ("Obsidian", "転職について考えた日", "今の仕事を続ける安心と、新しい役割へ挑戦したい気持ちの間で迷っている。", "Daily/2026-07-12.md"),
        ("Obsidian", "半年後にしたいこと", "研究だけでなく、利用者へ届くプロダクトを自分の責任で育てたい。", "Career/半年後.md"),
        ("ChatGPT Memory", "Memory 1", "大きな決断では、選択肢を比較できる表と撤退条件があると安心して進められる。", ""),
        ("ChatGPT conversation", "働き方の相談", "転職する前に、小さな社内プロジェクトで自分の仮説を試せないだろうか。", "conversations.json"),
    ]
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
    parser.add_argument("--question", default="次の仕事へ進むために、今どの準備を始めるべきですか")
    parser.add_argument("--output", help="Write an Obsidian Markdown note")
    parser.add_argument("--demo", action="store_true")
    args = parser.parse_args()

    records: list[MemoryRecord] = []
    if args.demo:
        records.extend(sample_records())
    if args.obsidian:
        records.extend(import_obsidian_vault(args.obsidian))
    if args.chatgpt:
        records.extend(import_chatgpt_export(args.chatgpt))
    if args.memory_text:
        records.extend(parse_memory_summary(args.memory_text))
    if not records:
        parser.error("provide --demo, --obsidian, --chatgpt, or --memory-text")

    reading = create_reading(args.question, records)
    if args.output:
        Path(args.output).write_text(export_obsidian_markdown(reading, records), encoding="utf-8")
    print(json.dumps(reading, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
