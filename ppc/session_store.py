"""
Session Store — persists SessionLog to disk (JSON / CSV).

Auto-creates sessions/ directory on first write.
"""

import json
import os
import csv
from datetime import datetime

from ppc.schemas.session_log import SessionLog


DEFAULT_SESSIONS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "sessions",
)


def _ensure_dir(path: str) -> str:
    os.makedirs(path, exist_ok=True)
    return path


def save_log(
    session_log: SessionLog,
    directory: str = DEFAULT_SESSIONS_DIR,
) -> str:
    _ensure_dir(directory)
    filename = (
        f"{session_log.session_id or datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        f".json"
    )
    filepath = os.path.join(directory, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(
            {
                "session_id": session_log.session_id,
                "original_prompt": session_log.original_prompt,
                "optimized_prompt_v1": session_log.optimized_prompt_v1,
                "llm_output_v1": session_log.llm_output_v1,
                "critic_score": {
                    "constraint_following": session_log.critic_score.constraint_following,
                    "clarity": session_log.critic_score.clarity,
                    "accuracy": session_log.critic_score.accuracy,
                    "efficiency": session_log.critic_score.efficiency,
                },
                "detected_failures": session_log.detected_failures,
                "optimized_prompt_v2": session_log.optimized_prompt_v2,
                "timestamp": session_log.timestamp,
                "mode_used": session_log.mode_used,
                "complexity_at_start": session_log.complexity_at_start,
            },
            f,
            indent=2,
            ensure_ascii=False,
            default=str,
        )
    return filepath


def load_logs(directory: str = DEFAULT_SESSIONS_DIR) -> list[SessionLog]:
    if not os.path.isdir(directory):
        return []
    logs: list[SessionLog] = []
    for filename in sorted(os.listdir(directory)):
        if not filename.endswith(".json"):
            continue
        filepath = os.path.join(directory, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            logs.append(_dict_to_session_log(data))
        except (json.JSONDecodeError, KeyError):
            continue
    return logs


def export_csv(
    logs: list[SessionLog],
    filepath: str,
) -> str:
    rows = []
    for log in logs:
        rows.append({
            "session_id": log.session_id,
            "timestamp": log.timestamp,
            "mode": log.mode_used,
            "complexity": log.complexity_at_start,
            "original_tokens": len(log.original_prompt.split()),
            "optimized_tokens": len(log.optimized_prompt_v1.split()),
            "constraint_following": log.critic_score.constraint_following,
            "clarity": log.critic_score.clarity,
            "accuracy": log.critic_score.accuracy,
            "efficiency": log.critic_score.efficiency,
            "avg_score": log.critic_score.average(),
            "failures": len(log.detected_failures),
            "regenerated": log.has_improvements(),
        })
    if not rows:
        return filepath

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return filepath


def _dict_to_session_log(data: dict) -> SessionLog:
    from ppc.schemas.session_log import CriticScore
    cs = data.get("critic_score", {})
    return SessionLog(
        session_id=data.get("session_id", ""),
        original_prompt=data.get("original_prompt", ""),
        optimized_prompt_v1=data.get("optimized_prompt_v1", ""),
        llm_output_v1=data.get("llm_output_v1", ""),
        critic_score=CriticScore(
            constraint_following=cs.get("constraint_following", 0),
            clarity=cs.get("clarity", 0),
            accuracy=cs.get("accuracy", 0),
            efficiency=cs.get("efficiency", 0),
        ),
        detected_failures=data.get("detected_failures", []),
        optimized_prompt_v2=data.get("optimized_prompt_v2", ""),
        timestamp=data.get("timestamp", ""),
        mode_used=data.get("mode_used", ""),
        complexity_at_start=data.get("complexity_at_start", 0),
    )
