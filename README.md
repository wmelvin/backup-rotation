#Backup Rotation Scheme Generator

This command-line tool, writen in Python, calculates a scheme for rotating backup media with different levels of retention.

This is a one-off utility program with some hard-coded parameters. It is **not a finished product.**

It was built with two purposes in mind:
- Explore different schemes for rotating my personal backup media.
- Gain experience programming in Python by iterating on a solution to this problem.

The primary output is a set of *.csv* files. I used *LibreOffice Calc* to view the files and compare different backup rotation schemes.

I did settle on a scheme to use, and copied the rotation plan from the main output file (`output-bakrot-*-1.csv`) to a spreadsheet where I track the actual backups.

My initial plan was to rotate a set of external hard drives at a weekly backup interval, and keep a given number of backups at different (increasingly longer) retention intervals.

In practice, I have not always done the backups weekly. That renders the *dates* in the output obsolete beyond the initial assessment of the scheme. The important output is the rotation plan, which needs to be followed regardless of the schedule. The schedule has to be flexible to accomodate *reality*.
