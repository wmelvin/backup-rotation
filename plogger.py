#!/usr/bin/env python3


from datetime import datetime


class Plogger:
    def __init__(
        self, filename1: str, filename2: str, do_timestamp_log1: bool
    ):
        self.filename1 = filename1
        self.filename2 = filename2
        self.do_timestamp_log1 = do_timestamp_log1

    def log(self, msg):
        if len(self.filename1) == 0:
            return
        #  Print and log.
        with open(self.filename1, "a") as log_file:
            print(msg)
            if self.do_timestamp_log1:
                log_file.write(f"[{datetime.now():%Y%m%d_%H%M%S}] {msg}\n")
            else:
                log_file.write(f"{msg}\n")

    def log2(self, msg):
        if len(self.filename2) == 0:
            return
        #  Write to second log.
        #  Second log does not add a time stamp.
        with open(self.filename2, "a") as log_file:
            # print(msg)
            log_file.write(f"{msg}\n")
