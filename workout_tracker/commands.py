"""Slash commands (/show, /undo, ...)."""

from collections.abc import Callable
from dataclasses import dataclass, field

from .formatting import format_summary
from .input_history import clear_input_history, remove_from_input_history
from .schemas import ExerciseRecord


@dataclass
class Session:
    """State of the current workout session."""

    interactive: bool
    exercise_history: list[ExerciseRecord] = field(default_factory=list)
    entered_lines: list[str] = field(default_factory=list)  # valid set lines, for /undo


@dataclass
class Command:
    handler: Callable[[Session], None]
    description: str


def undo_last_set(exercise_history: list[ExerciseRecord]) -> None:
    """Pop the most recent set."""
    if not exercise_history:
        return
    last_exercise = exercise_history[-1]
    last_exercise.sets.pop()
    if not last_exercise.sets:
        exercise_history.pop()


def show(session: Session) -> None:
    print("\n".join(format_summary(session.exercise_history)) or "Nothing logged yet.")


def undo(session: Session) -> None:
    if not session.entered_lines:
        print("There's nothing to undo!")
        return
    undo_last_set(session.exercise_history)
    undone = session.entered_lines.pop()
    if session.interactive:
        remove_from_input_history(undone)
    print(f"Removed: {undone}")


def clear(session: Session) -> None:
    clear_input_history()
    print("History cleared.")


def show_help(session: Session) -> None:
    print(help_text())


def end(session: Session) -> None:
    raise NotImplementedError


def close(session: Session) -> None:
    raise NotImplementedError


COMMANDS: dict[str, Command] = {
    "/help": Command(show_help, "Show this menu"),
    "/show": Command(show, "Show the current workout history"),
    "/undo": Command(undo, "Undo the last set"),
    "/clear": Command(clear, "Clear exercise history"),
    # "/end": Command(end, "Save the current workout and close the program"),
    # "/close": Command(close, "Close the program without saving"),
}


USAGE = """\
Log a set:  bench press 135x8
            crunches 8
            plank 60s
            bar hang 5x60s
            pull-up bwx10 (bodyweight)
Tab:        Look up an exercise name/weights/reps in history
Ctrl+D:     Finish and save the current workout"""


def help_text() -> str:
    command_lines = [
        f"  {name:<9} {command.description}" for name, command in COMMANDS.items()
    ]
    return USAGE + "\n\nCommands:\n" + "\n".join(command_lines)


def run_command(session: Session, text: str) -> None:
    command = COMMANDS.get(text)
    if command is None:
        print(f"Unknown command {text!r}. Type /help for commands.")
        return
    command.handler(session)
