from .schemas import ExerciseRecord


def parse_workout_sets(exercise: ExerciseRecord) -> str:
    res = ""
    previous_key = None
    for exercise_set in exercise.sets:
        # Group consecutive sets with the same type and weight
        current_key = (type(exercise_set), exercise_set.weight)
        amount = exercise_set.format_amount()
        if current_key == previous_key:
            formatted_set = f",{amount}"
        else:
            if exercise_set.show_weight:
                formatted_set = f"{exercise_set.weight}x{amount}"
            else:
                formatted_set = amount
            if previous_key is not None:
                formatted_set = f"; {formatted_set}"
        res += formatted_set
        previous_key = current_key

    return res


def format_summary(exercise_history: list[ExerciseRecord]) -> list[str]:
    return [
        f"{i}. {exercise.name}: {parse_workout_sets(exercise)}"
        for i, exercise in enumerate(exercise_history, start=1)
    ]
