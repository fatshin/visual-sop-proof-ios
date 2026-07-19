from __future__ import annotations

import json
import tempfile
import unittest
import zipfile
from pathlib import Path

import product


class OracleCouncilTests(unittest.TestCase):
    def test_sample_reading_uses_all_ten_methods(self) -> None:
        records = product.sample_records()
        reading = product.create_reading("次の仕事に向けて何を準備するべきですか", records)
        self.assertEqual(reading["status"], "REFLECTION_READY")
        self.assertEqual(len(reading["readings"]), 10)
        self.assertEqual(reading["memory_count"], 4)
        self.assertIn("娯楽と内省", reading["disclaimer"])

    def test_chatgpt_parser_uses_user_messages_only(self) -> None:
        fixture = [
            {
                "title": "Career",
                "mapping": {
                    "u": {
                        "message": {
                            "author": {"role": "user"},
                            "content": {"parts": ["転職前に小さく試したい"]},
                        }
                    },
                    "a": {
                        "message": {
                            "author": {"role": "assistant"},
                            "content": {"parts": ["あなたは必ず成功します"]},
                        }
                    },
                },
            }
        ]
        records = product._parse_conversations_json(json.dumps(fixture))
        self.assertEqual(len(records), 1)
        self.assertIn("小さく試したい", records[0].text)
        self.assertNotIn("必ず成功", records[0].text)

    def test_chatgpt_zip_is_read_without_extracting_files(self) -> None:
        fixture = [
            {
                "title": "Budget",
                "mapping": {
                    "u": {
                        "message": {
                            "author": {"role": "user"},
                            "content": {"parts": ["支出を見直してから決めたい"]},
                        }
                    }
                },
            }
        ]
        with tempfile.TemporaryDirectory() as directory:
            archive_path = Path(directory) / "export.zip"
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr("account/conversations.json", json.dumps(fixture))
            records = product.import_chatgpt_export(archive_path)
        self.assertEqual(records[0].source, "ChatGPT conversation")

    def test_unsafe_archive_path_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            archive_path = Path(directory) / "bad.zip"
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr("../conversations.json", "[]")
            with self.assertRaisesRegex(ValueError, "Unsafe path"):
                product.import_chatgpt_export(archive_path)

    def test_obsidian_skips_hidden_config_and_secret_notes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory)
            (vault / "Daily").mkdir()
            (vault / ".obsidian").mkdir()
            (vault / "Daily" / "note.md").write_text(
                "# 今日の記録\n\n仕事について落ち着いて考える。", encoding="utf-8"
            )
            (vault / ".obsidian" / "config.md").write_text("internal", encoding="utf-8")
            (vault / "secret.md").write_text("api_key: should-not-import", encoding="utf-8")
            records = product.import_obsidian_vault(vault)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].title, "今日の記録")
        self.assertNotIn("今日の記録", records[0].text)

    def test_obsidian_skips_file_symlinks_outside_vault(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            vault = root / "vault"
            vault.mkdir()
            outside = root / "outside.md"
            outside.write_text("# Outside\n読み込んではいけない記録です。", encoding="utf-8")
            (vault / "linked.md").symlink_to(outside)
            records = product.import_obsidian_vault(vault)
        self.assertEqual(records, [])

    def test_obsidian_skips_symlinks_into_hidden_vault_folders(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory)
            hidden = vault / ".private"
            hidden.mkdir()
            (hidden / "note.md").write_text(
                "# Hidden\n読み込んではいけない記録です。",
                encoding="utf-8",
            )
            (vault / "visible-link.md").symlink_to(hidden / "note.md")
            records = product.import_obsidian_vault(vault)
        self.assertEqual(records, [])

    def test_obsidian_skips_broken_symlinks_and_markdown_directories(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory)
            (vault / "broken.md").symlink_to(vault / "missing.md")
            (vault / "folder.md").mkdir()
            records = product.import_obsidian_vault(vault)
        self.assertEqual(records, [])

    def test_sensitive_title_and_common_key_shapes_are_rejected(self) -> None:
        self.assertIsNone(product._record("Obsidian", "password list", "十分に長い本文です"))
        self.assertIsNone(
            product._record(
                "ChatGPT Memory",
                "Memory",
                "key sk-1234567890abcdefghijkl",
            )
        )

    def test_markdown_horizontal_rule_is_not_mistaken_for_frontmatter(self) -> None:
        body = product._markdown_body(
            "---\n最初の段落です。\n---\n# 見出し\n本文です。"
        )
        self.assertIn("最初の段落", body)

    def test_memory_summary_accepts_bullets_and_rejects_secrets(self) -> None:
        records = product.parse_memory_summary(
            "- 重要な決断では比較表を作る\n"
            "- password: never-import-this-value\n"
            "3. 一週間後に振り返る習慣がある"
        )
        self.assertEqual(len(records), 2)

    def test_question_and_selection_are_validated(self) -> None:
        with self.assertRaisesRegex(ValueError, "at least 4"):
            product.create_reading("今?", product.sample_records())
        with self.assertRaisesRegex(ValueError, "Select at least one"):
            product.create_reading("今後どうするべきですか", [])

    def test_obsidian_export_contains_sources_and_review_boundary(self) -> None:
        records = product.sample_records()
        reading = product.create_reading("今後どうするべきですか", records)
        note = product.export_obsidian_markdown(reading, records)
        self.assertIn("type: oracle-council-reading", note)
        self.assertIn("## 使用した記憶", note)
        self.assertIn("## 7日後の振り返り", note)
        self.assertIn("娯楽と内省", note)

    def test_reading_is_deterministic_for_same_inputs(self) -> None:
        records = product.sample_records()
        first = product.create_reading("今後どうするべきですか", records)
        second = product.create_reading("今後どうするべきですか", records)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
