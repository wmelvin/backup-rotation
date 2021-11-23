# Backup Rotation Plan Generator

## Purpose

This command-line tool, writen in Python, calculates a plan for rotating backup media with different levels of retention.

It was built with two purposes in mind:
- Explore different schemes for rotating my personal backup media.
- Gain experience programming in Python.

This is a one-off utility program. It is **not a finished product.** Initially the parameters for different backup schemes were hard-coded. Later, those parameters were moved to JSON files, selected by passing the file name on the command line.

The primary output is a set of *.csv* files. I used *LibreOffice Calc* to view the files and compare different backup rotation schemes.

## Command-Line Arguments

Help text:
```
usage: bakplan.py [-h] [--debug-level DEBUG_LEVEL] scheme_file

Calculates a backup media rotation plan given a rotation scheme.

positional arguments:
  scheme_file           Path to the JSON file that defines the backup rotation
                        scheme.

optional arguments:
  -h, --help            show this help message and exit
  --debug-level DEBUG_LEVEL
                        Write extra debug information. Level: 0=none, 1=all.
                        Default is 0.
```

## Scheme File Example

```json
{
    "rotation_scheme": {
        "name": "Test1",
        "startdate": "2021-01-01",
        "cycles": "12",
        "period": "weeks",
        "levels": [
            {"level": 1, "slots": 2, "interval": 1},
            {"level": 2, "slots": 2, "interval": 2},
            {"level": 3, "slots": 2, "interval": 4}
        ]
    }
}
```

## Actual Use

I did settle on a scheme to use, and copied the rotation plan from the main output file (`bakrot-*-1.csv`) to a spreadsheet where I track the actual backups (the script was originally named "bakrot.py" - short for "backup rotation").

My initial plan was to rotate a set of external hard drives at a *weekly* backup interval, and keep a given number of backups at different (increasingly longer) retention intervals. In practice, I have not always done the backups weekly. That renders the *dates* in the output obsolete beyond the initial assessment of the scheme. The important output is the *rotation plan*, which may be followed regardless of the original schedule.
