# -*- coding: utf-8 -*-
from __future__ import annotations

import json

from codex_session_patcher.core.detector import RefusalDetector
from codex_session_patcher.core.formats import (
    OpenClawFormatStrategy,
    SessionFormat,
    _detect_format_from_path,
    detect_session_format,
    get_format_strategy,
)
from codex_session_patcher.core.patcher import clean_session_jsonl
from codex_session_patcher.core.parser import SessionParser


class TestOpenClawFormatStrategy:
    def test_get_format_strategy(self):
        strategy = get_format_strategy(SessionFormat.OPENCLAW)
        assert isinstance(strategy, OpenClawFormatStrategy)

    def test_extract_update_and_remove_thinking(self):
        strategy = OpenClawFormatStrategy()
        msg = {
            "type": "message",
            "message": {
                "role": "assistant",
                "content": [
                    {"type": "thinking", "thinking": "internal"},
                    {"type": "text", "text": "很抱歉，我不能帮助这个请求。"},
                ],
            },
        }

        assert "很抱歉" in strategy.extract_text_content(msg)
        updated = strategy.update_text_content(msg, "已替换")
        assert strategy.extract_text_content(updated) == "已替换"

        removed_msg, removed = strategy.remove_thinking_from_message(msg)
        assert removed == 1
        assert len(removed_msg["message"]["content"]) == 1
        assert removed_msg["message"]["content"][0]["type"] == "text"


class TestOpenClawCleaning:
    def test_clean_openclaw_messages(self):
        lines = [
            {"type": "session", "id": "sess-1"},
            {
                "type": "message",
                "message": {
                    "role": "assistant",
                    "content": [
                        {"type": "thinking", "thinking": "hidden"},
                        {"type": "text", "text": "很抱歉，我无法协助这个请求。"},
                    ],
                },
            },
        ]
        cleaned, modified, changes = clean_session_jsonl(
            lines,
            RefusalDetector(),
            mock_response="测试替换",
            session_format=SessionFormat.OPENCLAW,
        )

        assert modified is True
        assert any(c.change_type == 'replace' for c in changes)
        assert any(c.change_type == 'remove_thinking' for c in changes)

        assistant = cleaned[1]
        content = assistant["message"]["content"]
        assert len(content) == 1
        assert content[0]["type"] == "text"
        assert content[0]["text"] == "测试替换"


class TestOpenClawDetectionAndParser:
    def test_detect_from_path(self):
        fmt = _detect_format_from_path("~/.openclaw/agents/main/sessions/abc.jsonl")
        assert fmt == SessionFormat.OPENCLAW

    def test_detect_from_file_content(self, tmp_path):
        p = tmp_path / "sample.jsonl"
        p.write_text(
            json.dumps({
                "type": "message",
                "message": {"role": "assistant", "content": [{"type": "text", "text": "hello"}]},
            }, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        assert detect_session_format(str(p)) == SessionFormat.OPENCLAW

    def test_list_sessions_from_openclaw_dir(self, tmp_path):
        session_dir = tmp_path / ".openclaw" / "agents" / "main" / "sessions"
        session_dir.mkdir(parents=True)
        file_path = session_dir / "123e4567-e89b-12d3-a456-426614174000.jsonl"
        file_path.write_text(
            json.dumps({"type": "session", "id": "sess-1"}, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        parser = SessionParser(str(tmp_path / ".openclaw" / "agents"), session_format=SessionFormat.OPENCLAW)
        sessions = parser.list_sessions()
        assert len(sessions) == 1
        assert sessions[0].format == SessionFormat.OPENCLAW
        assert sessions[0].project_path == "agent:main"
