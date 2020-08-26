#!/usr/bin/env python3

# 2020-08-26 

from datetime import datetime
from datetime import date
from datetime import timedelta
from bakrotate import DrivePool
from bakrotate import RotationLevel
from bakrotate import to_alpha_label


#logfilename = 'bakrot_log.txt'


# DriveSlot = collections.namedtuple('DriveSlot', 'slot_num, use_count, backup_date')


# def to_alpha_label(n):
#     # Convert a number to an Excel-style base-26 alphabet label.
#     a = []
#     while n > 0:
#         q, r = divmod(n, 26)
#         if r == 0:
#             q = q - 1
#             r = 26
#         n = q
#         a.append(string.ascii_uppercase[r-1])
#     return ''.join(reversed(a))


class Plogger():
    def __init__(self, filename):
        self.filename = filename

    def log(self, msg):
        # Print and log.
        with open(self.filename,  'a') as log_file:
            print(msg)
            log_file.write(f"[{datetime.now():%Y%m%d_%H%M%S}] {msg}\n")




# def plog(msg):
#     # Print and log.
#     with open(logfilename,  'a') as log_file:
#         print(msg)
#         log_file.write(f"[{datetime.now():%Y%m%d_%H%M%S}] {msg}\n")


# class DrivePool():
#     def __init__(self):
#         self.drivepool = []
#         self.lastdrive = 0

#     def get_next_drive(self):        
#         if len(self.drivepool) == 0:
#             self.lastdrive = self.lastdrive + 1
#             n = self.lastdrive
#             plog(f"DrivePool.get_next_drive: {n} new")
#             return DriveSlot(n, 0, 0)
#         else:
#             ds = self.drivepool.pop()
#             plog(f"DrivePool.get_next_drive: {ds.slot_num} from pool")
#         return DriveSlot(ds.slot_num, ds.use_count, 0)

#     def add_drive(self, drive_slot):
#         if 0 < drive_slot.slot_num:
#             plog(f"DrivePool.add_drive: {drive_slot.slot_num} added to pool")
#             self.drivepool.append(drive_slot)


# class RotationLevel():
#     def __init__(self, level, num_drives, usage_interval, drive_pool, rotation_level_below):
#         self.level = level
#         self.num_drives = num_drives
#         self.usage_interval = usage_interval
#         self.drive_pool = drive_pool
#         self.level_below = rotation_level_below
#         self.cycle_num = -1
#         self.cycle_date = -1
#         self.cycle_index = -1
#         #self.last_index = -1
#         self.in_cycle = False
#         self.drives = [DriveSlot(0, 0, 0) for x in range(num_drives)]
#         self.prevs =  [DriveSlot(0, 0, 0) for x in range(num_drives)]        

#     def start_cycle(self, cycle_num, cycle_date):
#         self.cycle_num = cycle_num
#         self.cycle_date = cycle_date
#         self.in_cycle = ((cycle_num + 1) % self.usage_interval == 0)
        
#         self.cycle_index = (self.usage_cycle(cycle_num) % self.num_drives)
#         # self.cycle_index = self.last_index + 1
#         # if self.cycle_index == self.num_drives:
#         #     self.cycle_index = 0
        
#         self.prevs = [self.drives[x] for x in range(self.num_drives)]

#         plog(f"L{self.level} start_cycle {cycle_num}, date={cycle_date}, index={self.cycle_index}, in_cycle={self.in_cycle}")

#     # def is_full(self):
#     #     for ds in self.drives:
#     #         if ds.slot_num <= 0:
#     #             return False
#     #     return True

#     def list_drives(self):
#         plog(f"L{self.level} list_drives:")
#         for i in range(self.num_drives):
#             plog(f"  index={i}, drive={self.drives[i]}, previous={self.prevs[i]}")

#     def usage_cycle(self, cycle):
#         #n =  ((cycle + 1) // self.usage_interval)
#         n =  (cycle // self.usage_interval)
#         return n

#     def mark_free(self, index):
#         ds = self.drives[index]
#         self.drives[index] = DriveSlot(ds.slot_num * -1, ds.use_count, ds.backup_date)


#     def pull_drive(self):
#         # if not self.is_full:
#         #     return DriveSlot(0, 0, 0)

#         ds = self.drives[self.cycle_index]
#         if 0 < ds.slot_num:
#             self.mark_free(self.cycle_index)

#             plog(f"L{self.level} pull_drive: cycle={self.cycle_num}, index={self.cycle_index}, drive={ds.slot_num}, date={ds.backup_date}")
#             return ds
#         else:
#             if not self.level_below is None:
#                 return self.level_below.pull_drive()
#             else:
#                 plog(f"L{self.level} pull_drive: cycle={self.cycle_num}, index={self.cycle_index}, No drive to pull")
#                 return DriveSlot(0, 0, 0)


#     def pull_from_lower_level(self):
#         if self.in_cycle:
#             plog(f"L{self.level} pull_from_lower_level:  cycle={self.cycle_num}, index={self.cycle_index}")
#             pulled = self.level_below.pull_drive()
#             if 0 < pulled.slot_num:
#                 self.free_drive()
#                 self.drives[self.cycle_index] = pulled

#     def free_drive(self):
#         if self.in_cycle:
#             ds = self.drives[self.cycle_index] 
#             if 0 < ds.slot_num:
#                 plog(f"L{self.level} free_drive: cycle={self.cycle_num}, index={self.cycle_index}")
#                 self.drive_pool.add_drive(ds)
#                 self.mark_free(self.cycle_index)

#     def next_drive(self):
#         if self.in_cycle:
#             plog(f"L{self.level} next_drive: cycle={self.cycle_num}, index={self.cycle_index}")
#             ds = self.drive_pool.get_next_drive()
#             self.drives[self.cycle_index] = DriveSlot(ds.slot_num, ds.use_count + 1, self.cycle_date)
#             #self.last_index = self.cycle_index

#     def csv_head(self):
#         s = ''
#         for i in range(self.num_drives):
#             s += f",L{self.level}-D{i}"
#         return s

#     def csv_data(self):
#         s = ''
#         for i in range(self.num_drives):
#             s +=  f",\"{to_alpha_label(self.drives[i].slot_num)} ({self.drives[i].backup_date})\""
#         return s

#     def csv_diff(self):
#         s = ''
#         for i in range(self.num_drives):
#             s += ","
#             if self.drives[i] != self.prevs[i]:
#                 s +=  f"\"{to_alpha_label(self.drives[i].slot_num)} ({self.drives[i].backup_date})\""
#         return s

#     def get_drives_in_use(self):
#         drives_list = []
#         for x in range(self.num_drives):
#             if 0 < self.drives[x].slot_num:
#                 #t = (self.drv_date(x).strftime('%Y-%m-%d'), to_alpha_label(self.drv_num(x)))
#                 t = (self.drives[x].backup_date, self.drives[x].slot_num, self.drives[x].use_count, self.level)
#                 drives_list.append(t)
#         if not self.level_below is None:
#             drvs = self.level_below.get_drives_in_use()
#             for x in range(len(drvs)):
#                 drives_list.append(drvs[x])
#         return sorted(drives_list)



#----------------------------------------------------------------------
# Main script:

plog = Plogger('bakrot_log.txt')

start_date = date(2020,7,4)
n_weeks = 104


dp = DrivePool(plog)

# l1 = RotationLevel(1, 5, 1, dp, None)
# l2 = RotationLevel(2, 4, 2, dp, l1)
# l3 = RotationLevel(3, 6, 4, dp, l2)

l1 = RotationLevel(1, 7, 1, dp, None, plog)
l2 = RotationLevel(2, 4, 2, dp, l1, plog)
l3 = RotationLevel(3, 4, 4, dp, l2, plog)
l4 = RotationLevel(4, 4, 8, dp, l3, plog)

# *!* NEXT: Put levels in list.

if False:
    l1.list_drives()
    l2.list_drives()
    l3.list_drives()


if False:
    s = ",level-1,level-1,level-1,level-2,level-2,level-2,level-3,level-3,level-3"
    plog.log(s)
    s = "i,usage_cycle,cycle_index,is_used,usage_cycle,cycle_index,is_used,usage_cycle,cycle_index,is_used"
    plog.log(s)

    for w in range(n_weeks):
        d = start_date + timedelta(weeks=w)
        l1.start_cycle(w, d)
        l2.start_cycle(w, d)
        l3.start_cycle(w, d)
        s = f"{w},{l1.cycle_num},{l1.cycle_index},{l1.in_cycle:1}"
        s += f",{l2.cycle_num},{l2.cycle_index},{l2.in_cycle:1}"
        s += f",{l3.cycle_num},{l3.cycle_index},{l3.in_cycle:1}"
        plog.log(s)


if True:
    all_cycles = []
    out_list = []
    s = f"iter,date{l1.csv_head()},.{l2.csv_head()},.{l3.csv_head()},notes"
    out_list += f"{s}\n"
    out_list2 = out_list.copy()

    for week_num in range(n_weeks):
        week_date = start_date + timedelta(weeks=week_num)

        l1.start_cycle(week_num, week_date)
        l2.start_cycle(week_num, week_date)
        l3.start_cycle(week_num, week_date)
        l4.start_cycle(week_num, week_date)

        l4.pull_from_lower_level()

        l3.pull_from_lower_level()

        l2.pull_from_lower_level()

        l1.free_drive()

        s = f"{week_num},{week_date}{l1.csv_data()},{l2.csv_data()},{l3.csv_data()},before next drive"
        out_list2 += f"{s}\n"

        l1.next_drive()

        all_cycles.append(l4.get_drives_in_use())

        s = f"{week_num},{week_date}{l1.csv_data()},{l2.csv_data()},{l3.csv_data()},after next drive"
        out_list2 += f"{s}\n"

        s = f"{week_num},{week_date}{l1.csv_diff()},{l2.csv_diff()},{l3.csv_diff()}"
        out_list += f"{s}\n"

    with open('bakrot_output.csv', 'w') as out_file:
        out_file.writelines(out_list)

    with open('bakrot_output_data.csv', 'w') as out_file:
        out_file.writelines(out_list2)

    all_dates = []
    for cycle in all_cycles:
        for item in cycle:
            item_date = item[0].strftime('%Y-%m-%d')
            if not item_date in all_dates:
                all_dates.append(item_date)

    all_dates.sort()

    with open('bakrot_output_cycles.csv', 'w') as out_file:
        for d in all_dates:
            s = d
            for cycle in all_cycles:
                slot = ','
                for item in cycle:
                    item_date = item[0].strftime('%Y-%m-%d')
                    if item_date == d:
                        slot = to_alpha_label(item[1])
                        slot = f",\"{slot} U{item[2]} L{item[3]}\""
                        break
                s += slot
            out_file.write(f"{s}\n")


if False:
    l1.list_drives()
    l2.list_drives()
    l3.list_drives()
