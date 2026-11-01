# Workout Tracker

Log workout sets from the terminal.

Requires Python 3.12+.

## Run command

```sh
python -m workout_tracker [optional: <input file>.txt]
```

You will need to install `readline` if using Windows. Even then, stdout may not be displayed properly 100% of the time.

If importing a `.txt` file, make sure each line follows the sane format as you would type exercises in regularly.

## Usage
```
bench press 135x8    # weight x reps
pull-up bwx10        # bodyweight reps
plank 60s            # duration
```

- Available commands: `/help`, `/undo`, `/show`, `/clear`, `/finish` (save and exit), `/close` (exit without saving)
- `Tab` key: complete exercise names/sets based on input history
