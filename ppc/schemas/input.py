from dataclasses import dataclass, field
from typing import Literal

Mode = Literal[
    "basic", "reflection", "code", "architect",
    "brutal", "focus", "teacher", "compress"
]

ReinforcementLevel = Literal["none", "low", "medium", "aggressive", "maximum"]
ReflectionDepth = Literal[0, 1, 2, 3, 4, 5]
Verbosity = Literal["short", "medium", "long"]
DeliveryMode = Literal["transparent", "hybrid", "verbose"]

VALID_MODES = frozenset(Mode.__args__)
VALID_REINFORCEMENT = frozenset(ReinforcementLevel.__args__)
VALID_VERBOSITY = frozenset(Verbosity.__args__)


@dataclass
class InputOptions:
    reinforcement_level: ReinforcementLevel = "medium"
    reflection_depth: int = 0
    compression: bool = False
    strict_constraints: bool = True
    verbosity: Verbosity = "medium"
    token_budget: int = 4000


@dataclass
class InputSchema:
    mode: Mode = "basic"
    prompt: str = ""
    options: InputOptions = field(default_factory=InputOptions)

    def validate(self) -> "InputSchema":
        if not self.prompt.strip():
            raise ValueError("prompt cannot be empty")
        if self.options.token_budget < 100:
            raise ValueError("token_budget must be >= 100")
        if self.options.token_budget > 32000:
            raise ValueError("token_budget must be <= 32000")
        if not (0 <= self.options.reflection_depth <= 5):
            raise ValueError("reflection_depth must be 0-5")
        if self.mode not in VALID_MODES:
            raise ValueError(
                f"mode '{self.mode}' is not valid. Must be one of: "
                f"{', '.join(sorted(VALID_MODES))}"
            )
        if self.options.reinforcement_level not in VALID_REINFORCEMENT:
            raise ValueError(
                f"reinforcement_level '{self.options.reinforcement_level}' "
                f"is not valid. Must be one of: {', '.join(sorted(VALID_REINFORCEMENT))}"
            )
        if self.options.verbosity not in VALID_VERBOSITY:
            raise ValueError(
                f"verbosity '{self.options.verbosity}' is not valid. "
                f"Must be one of: {', '.join(sorted(VALID_VERBOSITY))}"
            )
        return self

    def prompt_token_estimate(self) -> int:
        return len(self.prompt.split())
