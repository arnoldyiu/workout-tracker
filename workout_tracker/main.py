import sys
from datetime import datetime
from pathlib import Path

from .commands import Session, run_command
from .formatting import format_summary
from .input_history import setup_input_history
from .parsing import parse_workout_input
from .schemas import ExerciseRecord

# Saved workouts go in <repo>/logs
LOGS_DIR = Path(__file__).resolve().parent.parent / "logs"


def log_set(session: Session, user_input: str) -> None:
    """Parse a set line and add it to the workout."""
    try:
        exercise_name, exercise_set = parse_workout_input(user_input)
    except ValueError:
        print(f"Invalid input ({user_input!r}). Type /help for examples.")
        return

    session.entered_lines.append(user_input)
    history = session.exercise_history

    # Consecutive sets of the same exercise share one record
    if history and history[-1].name == exercise_name:
        history[-1].sets.append(exercise_set)
    else:
        history.append(ExerciseRecord(exercise_name, [exercise_set]))


def save_workout(summary: list[str]) -> None:
    """Write the workout summary to logs/YYYYMMDD_HHMM.txt."""
    now = datetime.now()
    LOGS_DIR.mkdir(exist_ok=True)
    with open(LOGS_DIR / f"{now.strftime('%Y%m%d_%H%M')}.txt", "w") as f:
        f.write(f"{now.strftime('%B %d, %Y %H:%M')}\n")
        f.write("\n".join(summary) + "\n")


def main() -> int:
    # Only show the prompt when typing interactively
    is_user_input = sys.stdin.isatty()
    prompt = (
        "Enter an exercise (e.g. benchpress 8x3, bar hang 60s): "
        if is_user_input
        else ""
    )
    if is_user_input:
        setup_input_history(prompt)

    session = Session(interactive=is_user_input)

    while True:
        try:
            line = input(prompt).strip()
        except EOFError:
            if is_user_input:
                print()
            break

        if line.startswith("/"):
            run_command(session, line)
        else:
            log_set(session, line)

    summary = format_summary(session.exercise_history)
    print("\n".join(summary))
    if summary:
        save_workout(summary)

    return 0


if __name__ == "__main__":
    sys.exit(main())
