from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from dataclasses import dataclass
from datetime import date
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


MAX_FILE_BYTES = 1_000_000
MAX_IMPORT_FILES = 500
MAX_ARCHIVE_BYTES = 25_000_000
MAX_RECORD_CHARS = 800

DIVINATIONS = (
    ("易経", "水雷屯", "動き出す前に、足場と助けを整える"),
    ("四柱推命に着想を得た均衡の視点", "調候を先に見る", "強みを押し通すより、環境との釣り合いを取る"),
    ("九星気学に着想を得た時機の視点", "準備・行動・見直し", "見えない準備を重ね、焦って結論を急がない"),
    ("宿曜に着想を得た関係の視点", "支援関係", "関係を断つ前に、育てられる縁を見分ける"),
    ("西洋占星術に着想を得た自己像の視点", "太陽星座の季節", "考えを言葉と期限に変えて、現実に照らす"),
    ("タロット", "隠者", "外の正解より、過去の自分が残した手掛かりを読む"),
    ("数秘術", "7", "情報を集める時間と、決める時間を分ける"),
    ("ルーン", "Jera", "結果を急がず、積み重ねが実る周期を尊重する"),
    ("ジオマンシー", "Conjunctio", "一人で閉じず、異なる情報を接続する"),
    ("月相・暦に着想を得た歩調の視点", "開始・育成・手放し", "小さく試し、次の節目で見直す"),
)

DIVINATIONS_EN = (
    ("I Ching", "Difficulty at the Beginning", "Stabilize the conditions that make the first move safe."),
    ("Four Pillars-inspired balance lens", "Climate before force", "Check whether the environment supports the effort the goal demands."),
    ("Nine Star Ki-inspired timing lens", "Prepare, move, review", "Give preparation, movement, and review different jobs."),
    ("Sukuyō-inspired relationship lens", "Supportive orbit", "Choose people who challenge the plan without taking away your agency."),
    ("Western astrology-inspired identity lens", "Sun-sign season", "Turn the identity you want into one visible behavior."),
    ("Tarot", "The Hermit", "Name what you fear losing if you act and if you do not."),
    ("Numerology", "Life Path", "Test a symbolic pattern against your actual decision history."),
    ("Runes", "Jera — harvest", "Notice which repeated effort is already producing a signal."),
    ("Geomancy", "Conjunctio — connection", "Connect small facts instead of waiting for one decisive feeling."),
    ("Lunar-calendar-inspired cadence lens", "Start, build, release", "Match the next action to the current phase of evidence."),
)

ACTIONS_EN = (
    ("Name the one condition that could make this move unsafe.", "Ask one experienced person what usually fails first.", "Run a 48-hour test without making the full commitment."),
    ("Separate the goal from its current environment.", "Remove one recurring drain for seven days.", "Define the minimum support required before taking more responsibility."),
    ("Label the current phase as prepare, move, or review.", "Choose one observable result for a nine-day experiment.", "Schedule the review before the experiment begins."),
    ("Name one supporter, one useful critic, and one clouding influence.", "Ask the critic to challenge one assumption.", "State a boundary that keeps final ownership with you."),
    ("Finish the sentence: I am becoming someone who…", "Make that identity visible through one behavior this week.", "Define evidence that would make you revise the identity."),
    ("Write the feared loss of acting and the cost of doing nothing.", "Find evidence for and against each fear.", "Choose the downside that can be detected and corrected earliest."),
    ("List three times this pattern helped you.", "Name one time the strength became an excess.", "Use the strength once with a clear limit."),
    ("Name an effort repeated at least three times.", "Stop adding inputs for seven days and measure its return.", "Set an observable continue, change, or stop rule."),
    ("Place two unrelated memories side by side.", "Collect one fact that connects or separates them.", "Make a table with evidence, interpretation, and next test."),
    ("Decide whether this is a start, build, review, or release decision.", "Take one phase-appropriate action within 24 hours.", "Review after seven days using a continue, change, or stop rule."),
)

ACTIONS_JA = (
    ("この動きを危険にする条件を一つ特定します。", "経験者一人に最初に失敗しやすい点を聞きます。", "本決定をせずに48時間の試行を行います。"),
    ("目標と現在の環境を分けて考えます。", "反復する消耗要因を一つ7日間だけ外します。", "責任を増やす前に必要な最低限の支援を定義します。"),
    ("現在を準備・行動・見直しのどれかに決めます。", "9日間で確認する結果を一つ選びます。", "実験開始前に見直し日を予定します。"),
    ("支援者・有益な批判者・判断を曇らせる人を挙げます。", "批判者には仮定を一つだけ反証してもらいます。", "最終判断を自分に残す境界線を言葉にします。"),
    ("『私は○○する人になりつつある』を完成させます。", "その自己像を今週一つの行動で見える形にします。", "自己像を修正するための証拠を決めます。"),
    ("動く場合の損失と動かない場合の代償を書きます。", "それぞれを支持する証拠と反証を探します。", "最も早く修正できる不利益を持つ案を選びます。"),
    ("同じ型が役立った出来事を三つ挙げます。", "強みが過剰になった出来事を一つ挙げます。", "明確な上限を付けて強みを一度使います。"),
    ("三回以上繰り返した努力を一つ挙げます。", "7日間は入力を増やさず成果を測ります。", "継続・変更・停止の観測条件を決めます。"),
    ("無関係に見える記憶を二つ並べます。", "二つを結ぶか分ける事実を一つ集めます。", "証拠・解釈・次の検証の三列表を作ります。"),
    ("開始・育成・見直し・手放しのどれかを決めます。", "24時間以内に段階に合う最小行動を取ります。", "7日後に継続・変更・停止を判断します。"),
)

BIRTH_PRECISIONS = {"exact", "approximate", "unknown"}

SUN_SIGNS = (
    (1, 20, "Aquarius", "水瓶座"),
    (2, 19, "Pisces", "魚座"),
    (3, 21, "Aries", "牡羊座"),
    (4, 20, "Taurus", "牡牛座"),
    (5, 21, "Gemini", "双子座"),
    (6, 22, "Cancer", "蟹座"),
    (7, 23, "Leo", "獅子座"),
    (8, 23, "Virgo", "乙女座"),
    (9, 23, "Libra", "天秤座"),
    (10, 24, "Scorpio", "蠍座"),
    (11, 23, "Sagittarius", "射手座"),
    (12, 22, "Capricorn", "山羊座"),
)

THEME_TERMS = {
    "仕事": ("仕事", "転職", "職場", "career", "job", "会社", "プロジェクト"),
    "関係": ("関係", "恋愛", "家族", "友人", "partner", "relationship", "人間関係"),
    "健康": ("健康", "体調", "食事", "睡眠", "運動", "health"),
    "お金": ("お金", "投資", "支出", "収入", "money", "budget", "資産"),
    "学び": ("学び", "勉強", "研究", "資格", "learn", "study"),
    "変化": ("変化", "迷い", "決断", "選択", "change", "decision"),
}

THEME_LABELS_EN = {
    "仕事": "work",
    "関係": "relationships",
    "健康": "health",
    "お金": "money",
    "学び": "learning",
    "変化": "change",
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


@dataclass(frozen=True)
class BirthContext:
    birth_date: str
    birth_time: str
    birth_place: str
    time_precision: str = "approximate"
    place_precision: str = "approximate"


def validate_birth_context(context: BirthContext) -> date:
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


def _life_path(value: str) -> int:
    total = sum(int(character) for character in value if character.isdigit())
    while total > 9 and total not in {11, 22, 33}:
        total = sum(int(character) for character in str(total))
    return total


def _sun_sign(value: date, language: str) -> str:
    current = SUN_SIGNS[value.month - 1]
    sign = current if value.day >= current[1] else SUN_SIGNS[(value.month + 10) % 12]
    return sign[3] if language == "ja" else sign[2]


def _time_band(value: str, language: str) -> str:
    match = re.search(r"\b([01]?\d|2[0-3]):[0-5]\d\b", value)
    if not match:
        return value.strip()
    hour = int(match.group(1))
    labels = (
        ("深夜", "朝", "午前", "午後", "夕方", "夜")
        if language == "ja"
        else ("late night", "morning", "late morning", "afternoon", "evening", "night")
    )
    index = 0 if hour < 5 else 1 if hour < 9 else 2 if hour < 12 else 3 if hour < 17 else 4 if hour < 21 else 5
    return labels[index]


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


def create_reading(
    question: str,
    records: list[MemoryRecord],
    birth: BirthContext,
    language: str = "en",
) -> dict[str, Any]:
    if language not in {"en", "ja"}:
        raise ValueError("Language must be en or ja")
    parsed_birth_date = validate_birth_context(birth)
    question = re.sub(r"\s+", " ", question).strip()
    if len(question) < 4:
        raise ValueError("Question must contain at least 4 characters")
    if not records:
        raise ValueError("Select at least one memory before creating a reading")
    if len(records) > MAX_IMPORT_FILES:
        raise ValueError("Too many memories selected")

    themes = detect_themes(records)
    seed = int(
        hashlib.sha256(
            (
                question
                + "|"
                + birth.birth_date
                + "|"
                + birth.birth_time
                + "|"
                + birth.birth_place
                + "|"
                + "|".join(r.id for r in records)
            ).encode()
        ).hexdigest(),
        16,
    )
    selected = []
    divinations = DIVINATIONS if language == "ja" else DIVINATIONS_EN
    actions = ACTIONS_JA if language == "ja" else ACTIONS_EN
    leading_themes = [item["theme"] for item in themes[:3]] or ["変化"]
    for index, (method, symbol, guidance) in enumerate(divinations):
        memory = records[(seed + index * 7) % len(records)]
        if index == 4:
            symbol = f"{_sun_sign(parsed_birth_date, language)} Sun · {_time_band(birth.birth_time, language)}"
        elif index == 6:
            symbol = f"ライフパス {_life_path(birth.birth_date)}" if language == "ja" else f"Life Path {_life_path(birth.birth_date)}"
        connection = (
            f"記憶「{memory.title}」には「{memory.text[:120]}」とあります。"
            "象徴が腹落ちするかどうかは、この実際の選択履歴と一致するかで判断します。"
            if language == "ja"
            else f'The memory “{memory.title}” says: “{memory.text[:120]}” '
            "The symbol matters only where it matches this actual decision history."
        )
        selected.append(
            {
                "method": method,
                "symbol": symbol,
                "context": guidance,
                "interpretation": (
                    f"この視点では、問いを一文字や吉凶に縮めず、記憶に現れた「{leading_themes[0]}」の型と照合します。"
                    if language == "ja"
                    else "This lens does not reduce the question to a label or fortune. It tests the symbolic prompt against a repeated pattern in your own evidence."
                ),
                "memory_id": memory.id,
                "memory_title": memory.title,
                "connection": connection,
                "actions": list(actions[index]),
                "caveat": (
                    "これは生年月日を用いた象徴的な内省であり、完全な出生図・命式・宿・未来の事実を算出したものではありません。"
                    if language == "ja"
                    else "This is a date-based symbolic reflection, not a calculated natal chart, BaZi chart, lunar mansion, or factual prediction."
                ),
            }
        )

    synthesis = (
        f"出生情報は答えを決めません。腹落ちの根拠は、選んだ記憶に「{'・'.join(leading_themes)}」が繰り返し現れることです。"
        "確信を待つのではなく、後戻りできる小さな検証を作り、その結果で読みを更新します。"
        if language == "ja"
        else f"Birth context does not decide the answer. The grounding evidence is that your selected memories repeatedly contain {' / '.join(THEME_LABELS_EN[theme] for theme in leading_themes)}. "
        "Do not wait for certainty: build a small reversible test, then update the reading from what actually happens."
    )
    return {
        "status": "REFLECTION_READY",
        "question": question,
        "memory_count": len(records),
        "source_count": len({record.source for record in records}),
        "themes": themes,
        "language": language,
        "birth_context": {
            "date": parsed_birth_date.isoformat(),
            "time": birth.birth_time.strip(),
            "place": birth.birth_place.strip(),
            "time_precision": birth.time_precision,
            "place_precision": birth.place_precision,
            "life_path": _life_path(birth.birth_date),
        },
        "readings": selected,
        "synthesis": synthesis,
        "next_step": (
            "24時間以内に一つの行動案を試し、7日後に継続・変更・停止を判断してください。"
            if language == "ja"
            else "Try one action within 24 hours, then decide to continue, change, or stop after seven days."
        ),
        "disclaimer": (
            "娯楽と内省のための結果です。医療、法律、投資、安全に関する判断には使用しないでください。"
            if language == "ja"
            else "For entertainment and reflection only. Do not use this for medical, legal, financial, or safety decisions."
        ),
    }


def export_obsidian_markdown(reading: dict[str, Any], records: list[MemoryRecord]) -> str:
    is_ja = reading.get("language") == "ja"
    theme_names = [
        item["theme"] if is_ja else THEME_LABELS_EN[item["theme"]]
        for item in reading["themes"][:5]
    ]
    lines = [
        "---",
        "type: oracle-council-reading",
        f"status: {reading['status']}",
        f"language: {reading.get('language', 'en')}",
        f"birth_date: {reading['birth_context']['date']}",
        f"birth_time_precision: {reading['birth_context']['time_precision']}",
        f"birth_place_precision: {reading['birth_context']['place_precision']}",
        f"memory_count: {reading['memory_count']}",
        "themes:",
        *[f"  - {theme}" for theme in theme_names],
        "review_after_days: 7",
        "---",
        "",
        "# Oracle Council リーディング" if is_ja else "# Oracle Council Reading",
        "",
        "## 出生情報" if is_ja else "## Birth context",
        "",
        (
            f"{reading['birth_context']['date']} · {reading['birth_context']['time']} "
            f"[{reading['birth_context']['time_precision']}] · {reading['birth_context']['place']} "
            f"[{reading['birth_context']['place_precision']}]"
        ),
        "",
        "## 今回の問い" if is_ja else "## Question",
        "",
        reading["question"],
        "",
        "## 腹落ちする統合解釈" if is_ja else "## Grounded synthesis",
        "",
        reading["synthesis"],
        "",
        "## 10の占術による読み" if is_ja else "## Ten symbolic readings",
        "",
    ]
    for item in reading["readings"]:
        lines.extend(
            [
                f"### {item['method']} — {item['symbol']}",
                "",
                item["context"],
                "",
                item["interpretation"],
                "",
                item["connection"],
                "",
                "**行動に移す3案**" if is_ja else "**Three ways to act**",
                "",
                *[f"{index}. {action}" for index, action in enumerate(item["actions"], 1)],
                "",
                f"_{item['caveat']}_",
                "",
                f"参照した記憶: [[Oracle Memory/{item['memory_title']}]]",
                "",
            ]
        )
    lines.extend(
        [
            "## 次の一歩" if is_ja else "## Next step",
            "",
            reading["next_step"],
            "",
            "## 使用した記憶" if is_ja else "## Memories used",
            "",
        ]
    )
    for record in records:
        suffix = f" — `{record.path}`" if record.path else ""
        lines.append(f"- {record.source}: {record.title}{suffix}")
    lines.extend(
        [
            "",
            "## 注意" if is_ja else "## Notice",
            "",
            reading["disclaimer"],
            "",
            "## 7日後の振り返り" if is_ja else "## Seven-day review",
            "",
            "- 実際に確認した事実:" if is_ja else "- Fact checked:",
            "- 取った行動:" if is_ja else "- Action taken:",
            "- 今読むと違って見える部分:" if is_ja else "- Continue, change, or stop:",
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
    parser.add_argument("--birth-date", required=True, help="Birth date in YYYY-MM-DD format")
    parser.add_argument("--birth-time", required=True, help="Birth time, approximate time, or 'unknown'")
    parser.add_argument("--birth-place", required=True, help="Birth place, approximate area, or 'unknown'")
    parser.add_argument("--time-precision", choices=sorted(BIRTH_PRECISIONS), default="approximate")
    parser.add_argument("--place-precision", choices=sorted(BIRTH_PRECISIONS), default="approximate")
    parser.add_argument("--language", choices=("en", "ja"), default="en")
    parser.add_argument("--question", default="What evidence should I create before moving into my next role?")
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

    birth = BirthContext(
        birth_date=args.birth_date,
        birth_time=args.birth_time,
        birth_place=args.birth_place,
        time_precision=args.time_precision,
        place_precision=args.place_precision,
    )
    reading = create_reading(args.question, records, birth, args.language)
    if args.output:
        Path(args.output).write_text(export_obsidian_markdown(reading, records), encoding="utf-8")
    print(json.dumps(reading, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
