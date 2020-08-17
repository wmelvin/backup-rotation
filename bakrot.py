#!/usr/bin/env python3

from datetime import date
from datetime import timedelta


#start_date = date(2020,7,4)
#end_date = date(2022,1,1)
#for w in range(0,100):
#    d = start_date + timedelta(weeks=w)
#    print(d)


#level_1_set = ['','','','','','','']

#level_1_size = 7
#level_1_set = [''] * level_1_size
#print(level_1_set)
#
#for i in range(level_1_size):
#  print(i, level_1_set[i])

#drive_pool = []
#last_drive = 0


class drive_pool():
    def __init__(self):
        self.drivepool = []
        self.lastdrive = 0

    def get_next_drive(self):
        if len(self.drivepool) == 0:
            self.lastdrive += 1
            return self.lastdrive
        else:
            return self.drivepool.pop()


class rotation_level():
    def __init__(self, num_drives, usage_interval):
        self.num_drives = num_drives
        self.usage_interval = usage_interval
        self.drives = [0] * num_drives

    def list_drives(self):
        for i in range(self.num_drives):
            print(i, self.drives[i])

    def pull_from(self, other_level, pool, iteration):
        pass

    def free_drive(self, pool, iteration):
        pass

    def next_drive(self, pool):
        pass

    def as_csv(self):
        s = ''
        for i in range(self.num_drives):
            s +=  "," + str(self.drives[i])
        return s


dp = drive_pool()

l1 = rotation_level(7, 1)
l2 = rotation_level(5, 2)
l3 = rotation_level(4, 4)

l1.list_drives
l2.list_drives
l3.list_drives


start_date = date(2020,7,4)
for w in range(0,10):
    d = start_date + timedelta(weeks=w)
    print(d)
    l3.pull_from(l2, dp, w)
    l2.pull_from(l1, dp, w)
    l1.free_drive(dp, w)
    print(w, l1.as_csv(), l2.as_csv(), l3.as_csv())
    l1.next_drive(dp)
    print(w, l1.as_csv(), l2.as_csv(), l3.as_csv())

