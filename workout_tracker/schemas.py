from dataclasses import dataclass
from typing import Protocol

BODYWEIGHT = "bw"


class Weight(float):
    """Exercise weight. 0 = bodyweight"""

    @classmethod
    def parse(cls, text: str) -> "Weight":
        if text.lower() in ("", BODYWEIGHT.lower()):
            return cls(0)
        return cls(text)

    @property
    def is_bodyweight(self) -> bool:
        return self == 0

    def __str__(self) -> str:
        return BODYWEIGHT if self.is_bodyweight else f"{self:g}"


class ExerciseSet(Protocol):
    weight: Weight

    def format_amount(self) -> str:
        """The reps/duration part, e.g. "8" or "60s"."""
        ...

    @property
    def show_weight(self) -> bool:
        """Whether the summary should print "<weight>x" before the amount."""
        ...


@dataclass
class RepTypeSet:
    weight: Weight
    reps: int

    def format_amount(self) -> str:
        return str(self.reps)

    @property
    def show_weight(self) -> bool:
        return True  # "bwx10", so bodyweight reps are clear


@dataclass
class DurationTypeSet:
    weight: Weight
    seconds: int

    def format_amount(self) -> str:
        return f"{self.seconds}s"

    @property
    def show_weight(self) -> bool:
        return not self.weight.is_bodyweight  # "60s" rather than "bwx60s"


@dataclass
class ExerciseRecord:
    name: str
    sets: list[ExerciseSet]
