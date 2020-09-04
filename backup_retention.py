#!/usr/bin/env python3

#----------------------------------------------------------------------
# backup_retention.py
#
# 2020-09-04: Replaces bakrotate.py. Changed class and tuple names.
#   Using 'retention' instead of 'rotation', 'slot' instead of 'drive'.
#   
#
#----------------------------------------------------------------------


import collections
import string


#__all__ = ["to_alpha_label", "RetentionSlot", "SlotPool", "RetentionLevel"]


def to_alpha_label(n):
    # Convert a number to an Excel-style base-26 alphabet label.
    if n < 0:
        return '*'
    a = []
    while n > 0:
        q, r = divmod(n, 26)
        if r == 0:
            q = q - 1
            r = 26
        n = q
        a.append(string.ascii_uppercase[r-1])
    return ''.join(reversed(a))


# A RetentionSlot contains a set of one or more backup media (such 
# as an external hard drive).

RetentionSlot = collections.namedtuple('RetentionSlot', 'slot_num, use_count, backup_date')


class SlotPool():
    def __init__(self, logger):
        self.pool = []
        self.lastslot = 0
        self.logger = logger

    def get_next_slot(self):
        if len(self.pool) == 0:
            self.lastslot = self.lastslot + 1
            n = self.lastslot
            self.logger.log(f"SlotPool.get_next_slot: {n} new")
            self.logger.log2(f"    New slot {n}")
            return RetentionSlot(n, 0, 0)
        else:
            ds = self.pool.pop()
            self.logger.log(f"SlotPool.get_next_slot: {ds.slot_num} from pool")
            self.logger.log2(f"    Reuse slot {ds.slot_num}")
        return RetentionSlot(ds.slot_num, ds.use_count, 0)

    def add_slot(self, slot):
        if 0 < slot.slot_num:
            self.logger.log(f"SlotPool.add_slot: {slot.slot_num} added to pool")
            self.pool.append(slot)


class RetentionLevel():
    def __init__(self, level, num_slots, usage_interval, slot_pool, rotation_level_below, logger):
        self.level = level
        self.num_slots = num_slots
        self.usage_interval = usage_interval
        self.slot_pool = slot_pool
        self.level_below = rotation_level_below
        self.logger = logger
        self.cycle_num = -1
        self.cycle_date = -1
        self.cycle_index = -1
        self.in_cycle = False
        self.slots = [RetentionSlot(0, 0, 0) for x in range(num_slots)]
        self.prevs =  [RetentionSlot(0, 0, 0) for x in range(num_slots)]

    def start_cycle(self, cycle_num, cycle_date):
        self.cycle_num = cycle_num
        self.cycle_date = cycle_date
        self.in_cycle = ((cycle_num + 1) % self.usage_interval == 0)

        self.cycle_index = (self.usage_cycle(cycle_num) % self.num_slots)

        self.prevs = [self.slots[x] for x in range(self.num_slots)]

        self.logger.log(f"L{self.level} start_cycle {cycle_num}, date={cycle_date}, index={self.cycle_index}, in_cycle={self.in_cycle}")

    def list_slots(self):
        self.logger.log(f"L{self.level} list_slots:")
        for i in range(self.num_slots):
            self.logger.log(f"  index={i}, slot={self.slots[i]}, previous={self.prevs[i]}")

    def usage_cycle(self, cycle):
        n =  (cycle // self.usage_interval)
        return n

    def mark_free(self, index):
        ds = self.slots[index]
        self.logger.log2(f"  Free slot {ds.slot_num} in level {self.level}.")
        self.slots[index] = RetentionSlot(ds.slot_num * -1, ds.use_count, ds.backup_date)

    def pull_slot(self):
        ds = self.slots[self.cycle_index]
        if 0 < ds.slot_num:
            self.mark_free(self.cycle_index)
            self.logger.log(f"L{self.level} pull_slot: cycle={self.cycle_num}, index={self.cycle_index}, slot={ds.slot_num}, date={ds.backup_date}")
            return ds
        else:
            if not self.level_below is None:
                return self.level_below.pull_slot()
            else:
                self.logger.log(f"L{self.level} pull_slot: cycle={self.cycle_num}, index={self.cycle_index}, No slot to pull")
                return RetentionSlot(0, 0, 0)

    def pull_from_lower_level(self):
        if self.in_cycle:
            self.logger.log(f"L{self.level} pull_from_lower_level:  cycle={self.cycle_num}, index={self.cycle_index}")
            pulled = self.level_below.pull_slot()
            if 0 < pulled.slot_num:
                self.free_slot()
                self.logger.log2(f"  Move slot {pulled.slot_num} to level {self.level}.")
                self.slots[self.cycle_index] = pulled

    def free_slot(self):
        if self.in_cycle:
            ds = self.slots[self.cycle_index]
            if 0 < ds.slot_num:
                self.logger.log(f"L{self.level} free_slot: cycle={self.cycle_num}, index={self.cycle_index}")
                self.slot_pool.add_slot(ds)
                self.mark_free(self.cycle_index)

    def next_slot(self):
        if self.in_cycle:
            self.logger.log(f"L{self.level} next_slot: cycle={self.cycle_num}, index={self.cycle_index}")
            self.logger.log2(f"  Get next slot for level {self.level}.")
            ds = self.slot_pool.get_next_slot()
            self.slots[self.cycle_index] = RetentionSlot(ds.slot_num, ds.use_count + 1, self.cycle_date)
            #self.last_index = self.cycle_index

    def csv_head(self):
        s = ''
        for i in range(self.num_slots):
            s += f",L{self.level}-D{i}"
        return s

    def csv_data(self):
        s = ''
        for i in range(self.num_slots):
            if self.slots[i].slot_num == 0:
                s += ','
            else:
                s +=  f",\"{to_alpha_label(self.slots[i].slot_num)} ({self.slots[i].backup_date})\""
        return s

    def csv_diff(self):
        s = ''
        for i in range(self.num_slots):
            s += ","
            if self.slots[i] != self.prevs[i]:
                s +=  f"\"{to_alpha_label(self.slots[i].slot_num)} ({self.slots[i].backup_date})\""
        return s

    def get_slots_in_use(self):
        slots_list = []
        for x in range(self.num_slots):
            if 0 < self.slots[x].slot_num:
                t = (self.slots[x].backup_date, self.slots[x].slot_num, self.slots[x].use_count, self.level)
                slots_list.append(t)
        if not self.level_below is None:
            in_use_below = self.level_below.get_slots_in_use()
            for x in range(len(in_use_below)):
                slots_list.append(in_use_below[x])
        return sorted(slots_list)
