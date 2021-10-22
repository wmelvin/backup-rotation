#!/usr/bin/env python3


from datetime import datetime


class Plogger:
    def __init__(self, filename1, filename2):
        self.filename1 = filename1
        self.filename2 = filename2

    def log(self, msg):
        if len(self.filename1) == 0:
            return
        #  Print and log.
        with open(self.filename1, "a") as log_file:
            print(msg)
            log_file.write(f"[{datetime.now():%Y%m%d_%H%M%S}] {msg}\n")

    def log2(self, msg):
        if len(self.filename2) == 0:
            return
        #  Write to second log.
        #  Second log does not add a time stamp.
        with open(self.filename2, "a") as log_file:
            # print(msg)
            log_file.write(f"{msg}\n")
