#!/usr/bin/env python3

# ---------------------------------------------------------------------
# backup_retention.py
#
# 2020-09-04: Replaces bakrotate.py. Changed class and tuple names.
#   Using 'retention' instead of 'rotation', 'slot' instead of 'drive'.
#
# 2020-09-06: Refactor logging.
#
# 2020-09-08: More tweaks and refactoring.
#
# 2020-09-11: Shorten csv header labels and action text.
#
# ---------------------------------------------------------------------


import collections
import string
from datetime import date


def to_alpha_label(n):
    """Convert a number to an Excel-style base-26 alphabet label."""
    if n < 0:
        return "*"
    a = []
    while n > 0:
        q, r = divmod(n, 26)
        if r == 0:
            q = q - 1
            r = 26
        n = q
        a.append(string.ascii_uppercase[r - 1])
    return "".join(reversed(a))


def slot_label(n, show_number=False):
    if show_number:
        return f"{to_alpha_label(n)}({n})"
    else:
        return f"{to_alpha_label(n)}"


#  A RetentionSlot refers to a set of one or more backup media,
#  such as external hard drives.
RetentionSlot = collections.namedtuple(
    "RetentionSlot", "slot_num, use_count, cycle_used, backup_date"
)


class SlotPool:
    def __init__(self, logger):
        self.pool = []
        self.lastslot = 0
        self.logger = logger

    def get_next_slot(self):
        if len(self.pool) == 0:
            self.lastslot = self.lastslot + 1
            n = self.lastslot
            self.logger.log(
                f"SlotPool.get_next_slot: {slot_label(n, True)} new"
            )
            self.logger.log2(f"    New slot {slot_label(n)}")
            return RetentionSlot(n, 0, 0, 0)
        else:
            ds = self.pool.pop()
            self.logger.log(
                "SlotPool.get_next_slot: {} from pool".format(
                    slot_label(ds.slot_num, True)
                )
            )
            self.logger.log2(f"    Reuse slot {slot_label(ds.slot_num)}")
        return RetentionSlot(ds.slot_num, ds.use_count, 0, 0)

    def add_slot(self, slot):
        if 0 < slot.slot_num:
            self.logger.log(
                "SlotPool.add_slot: {} added to pool".format(
                    slot_label(slot.slot_num, True)
                )
            )
            self.pool.append(slot)


class RetentionLevelInvalidInterval(Exception):
    pass


class RetentionLevel:
    def __init__(
        self, level, num_slots, usage_interval, slot_pool, level_below, logger
    ):
        self.level = level
        self.num_slots = num_slots
        self.usage_interval = usage_interval
        self.slot_pool = slot_pool
        self.level_below = level_below
        self.logger = logger
        self.cycle_num = -1
        self.cycle_date = -1
        self.cycle_index = -1
        self.free_index = -1
        self.in_cycle = False
        self.cycle_actions = []
        self.slots = [RetentionSlot(0, 0, 0, 0) for x in range(num_slots)]
        self.prevs = [RetentionSlot(0, 0, 0, 0) for x in range(num_slots)]

        #  Higher levels must have longer intervals.
        if self.level_below is not None:
            if self.usage_interval <= self.level_below.usage_interval:
                err_msg = "usage_interval ("
                err_msg += str(self.usage_interval)
                err_msg += ") must be greater than that of level_below ("
                err_msg += str(self.level_below.usage_interval)
                err_msg += ")."
                raise RetentionLevelInvalidInterval(err_msg)

    def start_cycle(self, cycle_num, cycle_date):
        self.cycle_num = cycle_num
        self.cycle_date = cycle_date
        self.in_cycle = (cycle_num + 1) % self.usage_interval == 0

        self.cycle_index = self.usage_cycle(cycle_num) % self.num_slots
        self.free_index = -1
        self.cycle_actions.clear()

        self.prevs = [self.slots[x] for x in range(self.num_slots)]

        self.logger.log(
            (
                "Cycle {0}, Level {1}, Index {2}: start_cycle, in_cycle={3}"
            ).format(
                self.cycle_num, self.level, self.cycle_index, self.in_cycle
            )
        )

    def level_is_full(self):
        for i in range(self.num_slots):
            if self.slots[i].slot_num == 0:
                return False
        return True

    def oldest_backup_index(self):
        x = -1
        oldest = date.max
        for i in range(self.num_slots):
            if (0 < self.slots[i].slot_num) and (
                self.slots[i].backup_date < oldest
            ):
                oldest = self.slots[i].backup_date
                x = i
        return x

    def list_slots(self):
        self.logger.log(f"L{self.level} list_slots:")
        for i in range(self.num_slots):
            self.logger.log(
                f"  index={i}, slot={self.slots[i]}, previous={self.prevs[i]}"
            )

    def usage_cycle(self, cycle):
        n = cycle // self.usage_interval
        return n

    def mark_free(self, index):
        ds = self.slots[index]
        self.logger.log2(
            "  Free slot {} in level {} (index {}).".format(
                slot_label(ds.slot_num),
                self.level,
                index,
            )
        )
        self.slots[index] = RetentionSlot(
            ds.slot_num * -1, ds.use_count, ds.cycle_used, ds.backup_date
        )
        self.free_index = index

    def pull_slot(self):
        if self.level_is_full():
            slot_index = self.oldest_backup_index()

            #  *!* Seems like getting the oldest backup index might not be
            #  necessary.  Is it always the same as cycle_index?
            assert self.cycle_index == slot_index

            ds = self.slots[slot_index]
            self.mark_free(slot_index)
            self.logger.log(
                (
                    "Cycle {0}, Level {1}, Index {2}: pull_slot, slot={3}, "
                    + "date={4}"
                ).format(
                    self.cycle_num,
                    self.level,
                    slot_index,
                    slot_label(ds.slot_num, True),
                    ds.backup_date,
                )
            )
            return ds
        else:
            self.logger.log(
                (
                    "Cycle {0}, Level {1}, Index {2}: pull_slot, No slot to "
                    + "pull (level not full)"
                ).format(
                    self.cycle_num,
                    self.level,
                    self.cycle_index
                )
            )
            return RetentionSlot(0, 0, 0, 0)

    def pull_from_lower_level(self):
        if self.in_cycle:
            self.logger.log(
                (
                    "Cycle {0}, Level {1}, Index {2}: pull_from_lower_level"
                ).format(
                    self.cycle_num,
                    self.level,
                    self.cycle_index
                )
            )
            pulled = self.level_below.pull_slot()
            if 0 < pulled.slot_num:
                self.free_slot()
                self.logger.log2(
                    "  Move slot {0} to level {1} (index {2}).".format(
                        slot_label(pulled.slot_num),
                        self.level,
                        self.cycle_index,
                    )
                )
                self.cycle_actions.append(
                    "Move {0} L{1}.{2} to L{3}.{4}.".format(
                        slot_label(pulled.slot_num),
                        self.level_below.level,
                        self.level_below.cycle_index,
                        self.level,
                        self.cycle_index,
                    )
                )
                self.slots[self.cycle_index] = pulled

    def free_slot(self):
        if self.in_cycle:
            ds = self.slots[self.cycle_index]
            if 0 < ds.slot_num:
                self.logger.log(
                    "Cycle {0}, Level {1}, Index {2}: free_slot".format(
                        self.cycle_num, self.level, self.cycle_index
                    )
                )
                self.slot_pool.add_slot(ds)
                self.mark_free(self.cycle_index)

    def next_slot(self):
        if self.in_cycle:
            if self.free_index < 0:
                next_index = self.cycle_index
            else:
                next_index = self.free_index

            self.logger.log(
                "Cycle {0}, Level {1}, Index {2}: next_slot".format(
                    self.cycle_num, self.level, next_index
                )
            )
            self.logger.log2(
                f"  Get next slot for level {self.level} (index {next_index})."
            )

            ds = self.slot_pool.get_next_slot()

            self.slots[next_index] = RetentionSlot(
                ds.slot_num, ds.use_count + 1, self.cycle_num, self.cycle_date
            )

            if self.slots[next_index].use_count == 1:
                act = "New"
            else:
                act = "Reuse"
            self.cycle_actions.append(
                "{0} {1} in L{2}.{3}.".format(
                    act,
                    slot_label(self.slots[next_index].slot_num),
                    self.level,
                    next_index,
                )
            )

    def csvfrag_header(self):
        """CSV header row fragment for this level."""
        s = ""
        for i in range(self.num_slots):
            s += f',"L{self.level}.{i}"'
        return s

    def csvfrag_all_slots(self, include_date=False):
        """CSV fragment with data from all slots."""
        s = ""
        for i in range(self.num_slots):
            if self.slots[i].slot_num == 0:
                s += ","
            else:
                if include_date:
                    s += ',"{0}-{1} ({2})"'.format(
                        to_alpha_label(self.slots[i].slot_num),
                        self.slots[i].use_count,
                        self.slots[i].backup_date,
                    )
                else:
                    s += ',"{0}-{1}"'.format(
                        to_alpha_label(self.slots[i].slot_num),
                        self.slots[i].use_count,
                    )
        return s

    def csvfrag_changed_slots(self, include_date=False):
        """
        CSV fragment with data from only slots that changed from the
        previous cycle.
        """
        s = ""
        for i in range(self.num_slots):
            s += ","
            if self.slots[i] != self.prevs[i]:
                if include_date:
                    s += '"{0}-{1} ({2})"'.format(
                        to_alpha_label(self.slots[i].slot_num),
                        self.slots[i].use_count,
                        self.slots[i].backup_date,
                    )
                else:
                    s += '"{0}-{1}"'.format(
                        to_alpha_label(self.slots[i].slot_num),
                        self.slots[i].use_count,
                    )
        return s

    def get_slots_in_use(self):
        """
        Returns a list of tuples with data from all slots currently in use.
        The list is sorted by backup_date.

        Call on highest level to return the list including all lower levels.

        Each tuple contains:
          0: backup_date
          1: slot_num
          2: use_count
          3: level
          4: slot index
        """
        slots_list = []

        for x in range(self.num_slots):
            if 0 < self.slots[x].slot_num:
                t = (
                    self.slots[x].backup_date,
                    self.slots[x].slot_num,
                    self.slots[x].use_count,
                    self.level,
                    x,
                )
                slots_list.append(t)

        if self.level_below is not None:
            in_use_below = self.level_below.get_slots_in_use()
            for x in range(len(in_use_below)):
                slots_list.append(in_use_below[x])

        return sorted(slots_list)
