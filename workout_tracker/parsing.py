from .schemas import DurationTypeSet, ExerciseSet, RepTypeSet, Weight


def parse_workout_input(user_input: str) -> tuple[str, ExerciseSet]:
    exercise_name, set_text = user_input.rsplit(" ", 1)

    # "30s" or "20x30s" -> duration set (no weight means bodyweight)
    if set_text.endswith("s"):
        weight, _, seconds = set_text[:-1].rpartition("x")
        return exercise_name, DurationTypeSet(Weight.parse(weight), int(seconds))

    # "135x8", "0x10", "BWx10" or just "8" -> rep set (no weight means bodyweight)
    weight, _, reps = set_text.rpartition("x")
    return exercise_name, RepTypeSet(Weight.parse(weight), int(reps))
