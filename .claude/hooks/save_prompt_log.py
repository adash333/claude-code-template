#!/usr/bin/env python3
"""Stop フックから呼び出され、直近のユーザープロンプトとアシスタント応答を
docs/prompt/YYYY-MM-DD.md に追記する。

入力: stdin に Claude Code から JSON が渡される。
  { "session_id": "...", "transcript_path": "...", "hook_event_name": "Stop", ... }

出力: 標準出力には何も出さない(エラー時も exit 0 で抜けて Claude を妨げない)。
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    transcript_path = payload.get("transcript_path")
    if not transcript_path:
        return 0

    transcript = Path(transcript_path)
    if not transcript.exists():
        return 0

    messages = _read_jsonl(transcript)
    if not messages:
        return 0

    user_text, assistant_text = _extract_last_exchange(messages)
    if not user_text:
        return 0

    # システムリマインダー / フック出力だけのプロンプトは記録しない
    if _is_only_system_noise(user_text):
        return 0

    project_root = _find_project_root()
    log_dir = project_root / "docs" / "prompt"
    log_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now()
    log_file = log_dir / f"{now:%Y-%m-%d}.md"

    parts: list[str] = []
    if not log_file.exists():
        parts.append(f"# プロンプトログ - {now:%Y-%m-%d}\n")

    parts.append(f"\n## {now:%H:%M:%S}\n")
    parts.append("\n### ユーザー\n\n")
    parts.append(_blockquote(user_text.strip()))
    parts.append("\n\n### アシスタント\n\n")
    parts.append((assistant_text or "_(テキスト応答なし)_").strip())
    parts.append("\n\n---\n")

    try:
        with log_file.open("a", encoding="utf-8") as f:
            f.write("".join(parts))
    except Exception:
        return 0

    return 0


def _read_jsonl(path: Path) -> list[dict]:
    out: list[dict] = []
    try:
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    except Exception:
        return []
    return out


def _extract_last_exchange(messages: list[dict]) -> tuple[str, str]:
    """末尾から遡り、最後の user メッセージ以降を assistant 応答としてまとめる。"""
    last_user_idx = -1
    for i in range(len(messages) - 1, -1, -1):
        if _role_of(messages[i]) == "user":
            last_user_idx = i
            break

    if last_user_idx < 0:
        return "", ""

    user_text = _extract_text(messages[last_user_idx])
    assistant_pieces: list[str] = []
    for msg in messages[last_user_idx + 1:]:
        if _role_of(msg) == "assistant":
            text = _extract_text(msg)
            if text:
                assistant_pieces.append(text)
    return user_text, "\n\n".join(assistant_pieces)


def _role_of(msg: dict) -> str:
    if msg.get("type") in ("user", "assistant"):
        return msg["type"]
    inner = msg.get("message")
    if isinstance(inner, dict):
        role = inner.get("role")
        if isinstance(role, str):
            return role
    return ""


def _extract_text(msg: dict) -> str:
    inner = msg.get("message", msg)
    content = inner.get("content", "")

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        out: list[str] = []
        for item in content:
            if not isinstance(item, dict):
                continue
            t = item.get("type")
            if t == "text":
                txt = item.get("text", "")
                if txt:
                    out.append(txt)
            elif t == "tool_use":
                name = item.get("name", "tool")
                out.append(f"_[ツール呼び出し: {name}]_")
            elif t == "tool_result":
                # tool_result はノイズが多いので省略
                continue
        return "\n\n".join(out)

    return ""


def _is_only_system_noise(text: str) -> bool:
    """system-reminder タグだけ・空白だけのプロンプトは記録対象外。"""
    cleaned = text
    while "<system-reminder>" in cleaned and "</system-reminder>" in cleaned:
        start = cleaned.index("<system-reminder>")
        end = cleaned.index("</system-reminder>") + len("</system-reminder>")
        cleaned = cleaned[:start] + cleaned[end:]
    return not cleaned.strip()


def _blockquote(text: str) -> str:
    return "\n".join(("> " + line) if line else ">" for line in text.split("\n"))


def _find_project_root() -> Path:
    cwd = Path.cwd()
    for d in [cwd, *cwd.parents]:
        if (d / "CLAUDE.md").exists():
            return d
    return cwd


if __name__ == "__main__":
    sys.exit(main())
