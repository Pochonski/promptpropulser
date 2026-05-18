from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AnalyzedIntent:
    primary_goal: str = ""
    secondary_goals: list[str] = field(default_factory=list)
    complexity_score: int = 0


@dataclass
class DetectedConstraints:
    locked: list[str] = field(default_factory=list)
    soft: list[str] = field(default_factory=list)
    detected_types: list[str] = field(default_factory=list)


@dataclass
class AppliedReinforcement:
    level: str = ""
    applied_patterns: list[str] = field(default_factory=list)


@dataclass
class ReflectionResult:
    enabled: bool = False
    stage_results: list[str] = field(default_factory=list)
    critic_score: Optional[int] = None
    critic_notes: list[str] = field(default_factory=list)


@dataclass
class TokenUsage:
    input_tokens: int = 0
    optimization_tokens: int = 0
    final_prompt_tokens: int = 0


@dataclass
class OutputSchema:
    analyzed_intent: AnalyzedIntent = field(default_factory=AnalyzedIntent)
    constraints: DetectedConstraints = field(default_factory=DetectedConstraints)
    reinforcement: AppliedReinforcement = field(default_factory=AppliedReinforcement)
    semantic_echoes: list[str] = field(default_factory=list)
    optimized_prompt: str = ""
    system_instructions: str = ""
    reflection: ReflectionResult = field(default_factory=ReflectionResult)
    token_usage: TokenUsage = field(default_factory=TokenUsage)

    def to_dict(self) -> dict:
        return {
            "analyzed_intent": {
                "primary_goal": self.analyzed_intent.primary_goal,
                "secondary_goals": self.analyzed_intent.secondary_goals,
                "complexity_score": self.analyzed_intent.complexity_score,
            },
            "constraints": {
                "locked": self.constraints.locked,
                "soft": self.constraints.soft,
                "detected_types": self.constraints.detected_types,
            },
            "reinforcement": {
                "level": self.reinforcement.level,
                "applied_patterns": self.reinforcement.applied_patterns,
            },
            "semantic_echoes": self.semantic_echoes,
            "optimized_prompt": self.optimized_prompt,
            "system_instructions": self.system_instructions,
            "reflection": {
                "enabled": self.reflection.enabled,
                "checks": self.reflection.stage_results,
                "critic_notes": self.reflection.critic_notes,
            },
            "token_usage": {
                "input_tokens": self.token_usage.input_tokens,
                "optimization_tokens": self.token_usage.optimization_tokens,
                "final_prompt_tokens": self.token_usage.final_prompt_tokens,
            },
        }
