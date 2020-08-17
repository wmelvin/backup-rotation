#!/usr/bin/env python3

from datetime import date
from datetime import timedelta

class drive_pool():
    def __init__(self):
        self.drivepool = []
        self.lastdrive = 0

    def get_next_drive(self):
        #print("len(self.drivepool)=%d" % len(self.drivepool))
        if len(self.drivepool) == 0:
            self.lastdrive = self.lastdrive + 1
            n = self.lastdrive
        else:
            n = self.drivepool.pop()
        #print("drive_pool.get_next_drive()=%d" % n)
        return n
            
    def add_drive(self, drive_number):
        if 0 < drive_number:
            #print("drive_pool.add_drive(%d)" % drive_number)
            self.drivepool.append(drive_number)


class rotation_level():
    def __init__(self, level, num_drives, usage_interval):
        self.level = level
        self.num_drives = num_drives
        self.usage_interval = usage_interval
        self.drives = []
        self.prevs = []
        self.cycle_num = 0
        self.cycle_date = 0
        for i in range(num_drives):
            self.drives.append([0,0])
            self.prevs.append([0,0])
        #print("Drives: ", self.drives)
        
    def start_cycle(self, cycle_num, cycle_date):
        self.cycle_num = cycle_num
        self.cycle_date = cycle_date
        for i in range(self.num_drives):
            self.prevs[i] = self.drives[i]
        
    def list_drives(self):
        for i in range(self.num_drives):
            print(f"level={self.level}, index={i}, drive={self.drives[i][0]}, previous={self.prevs[i][0]}")
            
    def usage_cycle(self, cycle):
        n =  (cycle // self.usage_interval)           
        return n
            
    def cycle_index(self, cycle):
        n =  (self.usage_cycle(cycle) % self.num_drives)           
        return n
            
    def is_used(self, cycle):
        return ((cycle + 1) % self.usage_interval == 0)

    def pull_drive(self, pool, cycle):
        ix = self.cycle_index(cycle)
        
        #print(f"pull_drive: level={self.level}, cycle={cycle}, index={ix}")
        #self.list_drives()
        
        n = int(self.drives[ix][0])
        
        #print(f"pull_drive: level={self.level}, cycle={cycle}, index={ix}, value={n}")
        
        if 0 < n:      
            d = self.drives[ix][1]      
            self.drives[ix][0] = (n * -1)            
            return [n, d]
        else:
            return [0,0]
            
    def pull_from(self, other_level, pool, cycle):
        if self.is_used(cycle):
            ix = self.cycle_index(cycle)
            
            #print(f"pull_from: level={self.level}, cycle={cycle}, index={ix}")
            
            self.drives[ix] = other_level.pull_drive(pool, cycle)
                                    
    def free_drive(self, pool, cycle):
        if self.is_used(cycle):
            ix = self.cycle_index(cycle)
            
            #print(f"free_drive: level={self.level}, cycle={cycle}, index={ix}")
            
            pool.add_drive(self.drives[ix][0])
            
            n = int(self.drives[ix][0])
            
            self.drives[ix][0] = n * -1

    def next_drive(self, pool, cycle):
        if self.is_used(cycle):
            ix = self.cycle_index(cycle)
            
            #print(f"next_drive: level={self.level}, cycle={cycle}, index={ix}")
            
            #self.prevs[ix] = self.drives[ix]

            self.drives[ix][0] = pool.get_next_drive()
            self.drives[ix][1] = self.cycle_date

            #print("next_drive:", self.drives[ix])
            
            
    def csv_data(self):
        s = ''
        for i in range(self.num_drives):
            s +=  f",{str(self.drives[i][0])} ({self.drives[i][1]})"
        return s
        
    def csv_head(self):
        s = ''
        for i in range(self.num_drives):
            s += f",L{self.level}-D{i}"
        return s
        
    def csv_diff(self):
        s = ''
        for i in range(self.num_drives):
            s += ","
            if self.drives[i][0] != self.prevs[i][0]:
              s +=  f",{str(self.drives[i][0])} ({self.drives[i][1]})"
        return s


dp = drive_pool()

l1 = rotation_level(1, 7, 1)
l2 = rotation_level(2, 5, 2)
l3 = rotation_level(3, 4, 4)

l1.list_drives()
l2.list_drives()
l3.list_drives()

n_weeks = 20

if False:
    s = ",level-1,level-1,level-1,level-2,level-2,level-2,level-3,level-3,level-3"
    print(s)
    s = "i,usage_cycle,cycle_index,is_used,usage_cycle,cycle_index,is_used,usage_cycle,cycle_index,is_used"
    print(s)
    
    for w in range(n_weeks):
        s = f"{w},{l1.usage_cycle(w)},{l1.cycle_index(w)},{l1.is_used(w):1}"
        s += f",{l2.usage_cycle(w)},{l2.cycle_index(w)},{l2.is_used(w):1}"
        s += f",{l3.usage_cycle(w)},{l3.cycle_index(w)},{l3.is_used(w):1}"
        print(s)

if False:
    s = f"iter,date{l1.csv_head()},.{l2.csv_head()},.{l3.csv_head()},notes"
    print(s)
    
    start_date = date(2020,7,4)
    
    for w in range(n_weeks):
        d = start_date + timedelta(weeks=w)
        
        l1.start_cycle(w, d)
        l2.start_cycle(w, d)
        l3.start_cycle(w, d)
        
        l3.pull_from(l2, dp, w)
        
        l2.pull_from(l1, dp, w)
        
        l1.free_drive(dp, w)
        
        print(f"{w},{d}{l1.csv_data()},{l2.csv_data()},{l3.csv_data()},before next drive")
        
        l1.next_drive(dp, w)
        
        print(f"{w},{d}{l1.csv_diff()},{l2.csv_diff()},{l3.csv_diff()}")

