from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class CriticScore:
    constraint_following: int = 0
    clarity: int = 0
    accuracy: int = 0
    efficiency: int = 0

    def total(self) -> int:
        return self.constraint_following + self.clarity + self.accuracy + self.efficiency

    def average(self) -> float:
        return self.total() / 4.0

    def is_critical_failure(self) -> bool:
        return self.constraint_following <= 3 or self.accuracy <= 3


@dataclass
class SessionLog:
    session_id: str = ""
    original_prompt: str = ""
    optimized_prompt_v1: str = ""
    llm_output_v1: str = ""
    critic_score: CriticScore = field(default_factory=CriticScore)
    detected_failures: list[str] = field(default_factory=list)
    optimized_prompt_v2: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    mode_used: str = ""
    complexity_at_start: int = 0

    def has_improvements(self) -> bool:
        return bool(self.optimized_prompt_v2)

    def failure_count(self) -> int:
        return len(self.detected_failures)
