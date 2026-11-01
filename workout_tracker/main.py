import sys
from datetime import datetime
from pathlib import Path

from .commands import EndSession, Session, run_command
from .formatting import format_summary
from .input_history import setup_input_history
from .parsing import parse_workout_input
from .schemas import ExerciseRecord

# Saved workouts go in <repo>/logs
LOGS_DIR = Path(__file__).resolve().parent.parent / "logs"


def log_set(session: Session, input_line: str) -> None:
    """Parse a set line and add it to the workout."""
    try:
        exercise_name, exercise_set = parse_workout_input(input_line)
    except ValueError:
        print(f"Invalid input: {input_line!r}")
        return

    session.entered_lines.append(input_line)
    history = session.exercise_history

    # Consecutive sets of the same exercise should stay on the same line.
    if history and history[-1].name == exercise_name:
        history[-1].sets.append(exercise_set)
    else:
        history.append(ExerciseRecord(exercise_name, [exercise_set]))


def get_unique_log_path(now: datetime) -> Path:
    """Return the output path name. Handles duplicate file names using _2, _3..."""
    stem = now.strftime("%Y%m%d_%H%M%S")
    LOGS_DIR.mkdir(exist_ok=True)
    path = LOGS_DIR / f"{stem}.txt"
    duplicate_counter = 2
    while path.exists():
        path = LOGS_DIR / f"{stem}_{duplicate_counter}.txt"
        duplicate_counter += 1
    return path


def main(args: list[str] | None = None) -> int:
    if args is None:
        args = sys.argv[1:]
    if len(args) > 1:
        print("Only one file import is supported at a time.")
        return 2

    is_user_input: bool = len(args) == 0
    session = Session(interactive=is_user_input)
    if session.interactive and not sys.stdin.isatty():
        print(
            "Shell stdin redirection is not supported. Please pass the input file as an ordinary command-line argument."
        )
        return 2

    save_on_exit = True
    if not session.interactive:
        file_path = args[0]
        try:
            with open(file_path, "r") as f:
                imported_lines = f.read().splitlines()
            print(f"Successfully loaded workout data from {file_path}")
            for line in imported_lines:
                log_set(session, line)
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return 1
        except (OSError, UnicodeDecodeError) as e:
            print(f"Could not read file {file_path}: {e}")
            return 1

    else:
        user_prompt = "Enter an exercise (e.g. benchpress 8x3, bar hang 60s): "
        setup_input_history(user_prompt)
        while True:
            try:
                line = input(user_prompt).strip()
            except KeyboardInterrupt:
                print("\nKeyboardInterrupt detected, exiting program without saving.")
                return 0
            except EOFError:
                print("\nSaving workout and exiting program...")
                break

            try:
                if line.startswith("/"):
                    run_command(session, line)
                else:
                    log_set(session, line)
            except EndSession as e:  # /finish or /close
                save_on_exit = e.save
                break

        if not save_on_exit:
            print("Closed without saving.")
            return 0

    summary = format_summary(session.exercise_history)
    print("\n".join(summary))
    if summary:
        now = datetime.now()
        LOGS_DIR.mkdir(exist_ok=True)
        output_path = get_unique_log_path(now)
        with open(output_path, "w") as f:
            f.write(f"{now.strftime('%B %d, %Y %H:%M')}\n")
            f.write("\n".join(summary) + "\n")
        print(f"Saved workout to {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
