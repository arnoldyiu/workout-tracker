"""Exercise history (up/down keys) with partial completion via the Tab key."""

import atexit
import os
import readline
import sys

from .parsing import parse_workout_input

HISTORY_FILE = os.path.expanduser("~/.workout_history")

_completion_matches: list[str] = []
_prompt = ""


def setup_input_history(prompt: str) -> None:
    """Load up/down arrow history from disk and save it on exit."""
    global _prompt
    _prompt = prompt  # needed to redraw the line after listing matches

    try:
        readline.read_history_file(HISTORY_FILE)
    except OSError:
        pass

    def save_history() -> None:
        try:
            readline.write_history_file(HISTORY_FILE)
        except OSError:
            pass

    atexit.register(save_history)

    # Complete against the whole line, not single words
    readline.set_completer_delims("")
    readline.set_completer(complete_last_set)
    if "libedit" in (readline.__doc__ or ""):
        readline.parse_and_bind("bind ^I rl_complete")  # macOS
    else:
        readline.parse_and_bind("tab: complete")


def clear_input_history() -> None:
    """Wipe history; the file is emptied on exit when the empty history is saved."""
    readline.clear_history()


def remove_from_input_history(line: str) -> None:
    """Drop the most recent occurrence of line, so undone typos don't show up in Tab."""
    for i in range(readline.get_current_history_length() - 1, -1, -1):
        if (readline.get_history_item(i + 1) or "").strip() == line:
            readline.remove_history_item(i)
            return


def past_sets_per_exercise() -> dict[str, list[str]]:
    """Distinct history lines for each exercise (lowercased name), newest first."""
    sets: dict[str, list[str]] = {}
    for i in range(readline.get_current_history_length(), 0, -1):
        line = (readline.get_history_item(i) or "").strip()
        try:
            name, _ = parse_workout_input(line)
        except ValueError:
            continue
        lines = sets.setdefault(name.lower(), [])
        if line not in lines:
            lines.append(line)
    return sets


def find_completions(typed: str, past_sets: dict[str, list[str]]) -> list[str]:
    """
    "bench pr"      -> ["bench press"]                (finish the name)
    "bench press"   -> every past bench press set     (pick a set)
    "bench press 8" -> past bench press sets starting with "8"
    """
    typed = typed.strip()
    key = typed.lower()

    # Full name typed: offer all its past sets
    if key in past_sets:
        return past_sets[key]

    # Name plus part of a set: filter that exercise's sets.
    # Longest name first, so "bench press 8" isn't treated as "bench".
    for name in sorted(past_sets, key=len, reverse=True):
        if key.startswith(name + " "):
            matches = [line for line in past_sets[name] if line.lower().startswith(key)]
            if matches:
                return matches

    # Partial name: complete just the name, keeping its original casing
    return [
        lines[0].rsplit(" ", 1)[0]
        for name, lines in past_sets.items()
        if name.startswith(key)
    ]


def show_matches(matches: list[str]) -> None:
    """Print matches in our order (readline would sort them alphabetically),
    then redraw the prompt and what's been typed so far."""
    sys.stdout.write("\nHistory: " + ", ".join(matches) + "\n")
    sys.stdout.write(_prompt + readline.get_line_buffer())
    sys.stdout.flush()


def complete_last_set(text: str, state: int) -> str | None:
    """readline completer: returns the state-th completion for the typed line."""
    global _completion_matches
    if state == 0:
        _completion_matches = find_completions(text, past_sets_per_exercise())
        # Several matches: list them newest first ourselves and leave the
        # line alone, instead of letting readline show a sorted list.
        if len(_completion_matches) > 1:
            show_matches(_completion_matches)
            _completion_matches = []
    if state < len(_completion_matches):
        return _completion_matches[state]
    return None
