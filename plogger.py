#!/usr/bin/env python3

# 2020-08-26 


from datetime import datetime

class Plogger():
    def __init__(self, filename):
        self.filename = filename

    def log(self, msg):
        # Print and log.
        with open(self.filename,  'a') as log_file:
            print(msg)
            log_file.write(f"[{datetime.now():%Y%m%d_%H%M%S}] {msg}\n")
