#!/usr/bin/env python3

# 2020-08-26 


import collections
import string


#__all__ = ["to_alpha_label", "DriveSlot", "DrivePool", "RotationLevel"]


def to_alpha_label(n):
    # Convert a number to an Excel-style base-26 alphabet label.
    a = []
    while n > 0:
        q, r = divmod(n, 26)
        if r == 0:
            q = q - 1
            r = 26
        n = q
        a.append(string.ascii_uppercase[r-1])
    return ''.join(reversed(a))


DriveSlot = collections.namedtuple('DriveSlot', 'slot_num, use_count, backup_date')


class DrivePool():
    def __init__(self, logger):
        self.drivepool = []
        self.lastdrive = 0
        self.logger = logger

    def get_next_drive(self):        
        if len(self.drivepool) == 0:
            self.lastdrive = self.lastdrive + 1
            n = self.lastdrive
            self.logger.log(f"DrivePool.get_next_drive: {n} new")
            return DriveSlot(n, 0, 0)
        else:
            ds = self.drivepool.pop()
            self.logger.log(f"DrivePool.get_next_drive: {ds.slot_num} from pool")
        return DriveSlot(ds.slot_num, ds.use_count, 0)

    def add_drive(self, drive_slot):
        if 0 < drive_slot.slot_num:
            self.logger.log(f"DrivePool.add_drive: {drive_slot.slot_num} added to pool")
            self.drivepool.append(drive_slot)


class RotationLevel():
    def __init__(self, level, num_drives, usage_interval, drive_pool, rotation_level_below, logger):
        self.level = level
        self.num_drives = num_drives
        self.usage_interval = usage_interval
        self.drive_pool = drive_pool
        self.level_below = rotation_level_below
        self.logger = logger
        self.cycle_num = -1
        self.cycle_date = -1
        self.cycle_index = -1
        #self.last_index = -1
        self.in_cycle = False
        self.drives = [DriveSlot(0, 0, 0) for x in range(num_drives)]
        self.prevs =  [DriveSlot(0, 0, 0) for x in range(num_drives)]        

    def start_cycle(self, cycle_num, cycle_date):
        self.cycle_num = cycle_num
        self.cycle_date = cycle_date
        self.in_cycle = ((cycle_num + 1) % self.usage_interval == 0)
        
        self.cycle_index = (self.usage_cycle(cycle_num) % self.num_drives)
        # self.cycle_index = self.last_index + 1
        # if self.cycle_index == self.num_drives:
        #     self.cycle_index = 0
        
        self.prevs = [self.drives[x] for x in range(self.num_drives)]

        self.logger.log(f"L{self.level} start_cycle {cycle_num}, date={cycle_date}, index={self.cycle_index}, in_cycle={self.in_cycle}")

    # def is_full(self):
    #     for ds in self.drives:
    #         if ds.slot_num <= 0:
    #             return False
    #     return True

    def list_drives(self):
        self.logger.log(f"L{self.level} list_drives:")
        for i in range(self.num_drives):
            self.logger.log(f"  index={i}, drive={self.drives[i]}, previous={self.prevs[i]}")

    def usage_cycle(self, cycle):
        #n =  ((cycle + 1) // self.usage_interval)
        n =  (cycle // self.usage_interval)
        return n

    def mark_free(self, index):
        ds = self.drives[index]
        self.drives[index] = DriveSlot(ds.slot_num * -1, ds.use_count, ds.backup_date)


    def pull_drive(self):
        # if not self.is_full:
        #     return DriveSlot(0, 0, 0)

        ds = self.drives[self.cycle_index]
        if 0 < ds.slot_num:
            self.mark_free(self.cycle_index)

            self.logger.log(f"L{self.level} pull_drive: cycle={self.cycle_num}, index={self.cycle_index}, drive={ds.slot_num}, date={ds.backup_date}")
            return ds
        else:
            if not self.level_below is None:
                return self.level_below.pull_drive()
            else:
                self.logger.log(f"L{self.level} pull_drive: cycle={self.cycle_num}, index={self.cycle_index}, No drive to pull")
                return DriveSlot(0, 0, 0)


    def pull_from_lower_level(self):
        if self.in_cycle:
            self.logger.log(f"L{self.level} pull_from_lower_level:  cycle={self.cycle_num}, index={self.cycle_index}")
            pulled = self.level_below.pull_drive()
            if 0 < pulled.slot_num:
                self.free_drive()
                self.drives[self.cycle_index] = pulled

    def free_drive(self):
        if self.in_cycle:
            ds = self.drives[self.cycle_index] 
            if 0 < ds.slot_num:
                self.logger.log(f"L{self.level} free_drive: cycle={self.cycle_num}, index={self.cycle_index}")
                self.drive_pool.add_drive(ds)
                self.mark_free(self.cycle_index)

    def next_drive(self):
        if self.in_cycle:
            self.logger.log(f"L{self.level} next_drive: cycle={self.cycle_num}, index={self.cycle_index}")
            ds = self.drive_pool.get_next_drive()
            self.drives[self.cycle_index] = DriveSlot(ds.slot_num, ds.use_count + 1, self.cycle_date)
            #self.last_index = self.cycle_index

    def csv_head(self):
        s = ''
        for i in range(self.num_drives):
            s += f",L{self.level}-D{i}"
        return s

    def csv_data(self):
        s = ''
        for i in range(self.num_drives):
            if self.drives[i].slot_num == 0:
                s += ','    
            else:
                s +=  f",\"{to_alpha_label(self.drives[i].slot_num)} ({self.drives[i].backup_date})\""
        return s

    def csv_diff(self):
        s = ''
        for i in range(self.num_drives):
            s += ","
            if self.drives[i] != self.prevs[i]:
                s +=  f"\"{to_alpha_label(self.drives[i].slot_num)} ({self.drives[i].backup_date})\""
        return s

    def get_drives_in_use(self):
        drives_list = []
        for x in range(self.num_drives):
            if 0 < self.drives[x].slot_num:
                #t = (self.drv_date(x).strftime('%Y-%m-%d'), to_alpha_label(self.drv_num(x)))
                t = (self.drives[x].backup_date, self.drives[x].slot_num, self.drives[x].use_count, self.level)
                drives_list.append(t)
        if not self.level_below is None:
            drvs = self.level_below.get_drives_in_use()
            for x in range(len(drvs)):
                drives_list.append(drvs[x])
        return sorted(drives_list)
