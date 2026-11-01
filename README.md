# Workout Tracker

Log workout sets from the terminal.

Requires Python 3.12+.

## Run command

```sh
python -m workout_tracker
```

## Usage
```
bench press 135x8    # weight x reps
pull-up bwx10        # bodyweight reps
plank 60s            # duration
```

- Available commands: `/help`, `/undo`, `/show`, `/clear`, `/end` (save and exit), `/close` (exit without saving)
- `Tab` key: complete exercise names/sets based on input history
- `Ctrl`+`D`: finish and save workout to `logs/YYYYMMDD_HHMM.txt`
