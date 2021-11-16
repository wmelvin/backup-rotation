#!/usr/bin/env python3

import sys

from datetime import datetime
from pathlib import Path


class Plogger:
    def __init__(
        self,
        log_file_name: str,
        log_immediate: bool,
        log_timestamp: bool,
        steps_file_name: str,
        steps_immediate: bool
    ):
        self.log_file_name = log_file_name
        self.log_immediate = log_immediate
        self.log_timestamp = log_timestamp
        self.steps_file_name = steps_file_name
        self.steps_immediate = steps_immediate
        self.entries = []
        self.steps = []

        if 0 < len(self.log_file_name):
            p = Path(self.log_file_name).parent
            if not p.exists() and p.is_dir():
                sys.stderr.write(f"ERROR: Folder not found: '{p}'\n")
                sys.exit(1)

        if 0 < len(self.steps_file_name):
            p = Path(self.steps_file_name).parent
            if not p.exists() and p.is_dir():
                sys.stderr.write(f"ERROR: Folder not found: '{p}'\n")
                sys.exit(1)

    def _can_write_log(self):
        return 0 < len(self.log_file_name)

    def _can_write_steps(self):
        return 0 < len(self.steps_file_name)

    def log_msg(self, msg):
        if self.log_timestamp:
            # msg = f"[{datetime.now():%Y%m%d_%H%M%S}] {msg}"
            msg = f"[{datetime.now():%y%m%d_%H%M%S_%f}] {msg}"

        if self.log_immediate:
            if self._can_write_log():
                with open(self.log_file_name, "a") as f:
                    print(msg)
                    f.write(f"{msg}\n")
        else:
            self.entries.append(msg)

    def log_step(self, msg):
        if self.steps_immediate:
            if self._can_write_steps():
                with open(self.steps_file_name, "a") as f:
                    f.write(f"{msg}\n")
        else:
            self.steps.append(msg)

    def save_log(self):
        if self._can_write_log() and 0 < len(self.entries):
            with open(self.log_file_name, "a") as f:
                for s in self.entries:
                    f.write(f"{s}\n")
            self.entries.clear()

    def save_steps(self):
        if self._can_write_steps() and 0 < len(self.steps):
            with open(self.steps_file_name, "a") as f:
                for s in self.steps:
                    f.write(f"{s}\n")
            self.steps.clear()
