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
            print(f"drive_pool.get_next_drive()={n} new drive")
        else:
            n = self.drivepool.pop()
            print(f"drive_pool.get_next_drive()={n} from pool")
        return n
            
    def add_drive(self, drive_number):
        if 0 < drive_number:
            print(f"drive_pool.add_drive({drive_number})")
            self.drivepool.append(drive_number)


class rotation_level():
    def __init__(self, level, num_drives, usage_interval):
        self.level = level
        self.num_drives = num_drives
        self.usage_interval = usage_interval
        self.drives = []
        self.prevs = []
        self.cycle_num = -1
        self.cycle_date = -1
        self.cycle_index = -1
        self.drives = [[0,0] for x in range(num_drives)]
        self.prevs = []

        #print("Drives: ", self.drives)
        
    def start_cycle(self, cycle_num, cycle_date):
        self.cycle_num = cycle_num
        self.cycle_date = cycle_date

        self.prevs = [[self.drives[x][0], self.drives[x][1]] for x in range(self.num_drives)]

        self.cycle_index = (self.usage_cycle(cycle_num) % self.num_drives)           
        print(f"L{self.level} start_cycle {cycle_num}, date={cycle_date}, index={self.cycle_index}")
        
    def list_drives(self):
        for i in range(self.num_drives):
            print(f"level={self.level}, index={i}, drive={self.drives[i]}, previous={self.prevs[i]}")
            
    def usage_cycle(self, cycle):
        n =  (cycle // self.usage_interval)           
        return n
            
    #def cycle_index(self, cycle):
    #    n =  (self.usage_cycle(cycle) % self.num_drives)           
    #    return n
            
    def is_used(self, cycle):
        return ((cycle + 1) % self.usage_interval == 0)

    def pull_drive(self, pool, cycle):
        n = int(self.drives[self.cycle_index][0])                
        if 0 < n:      
            d = self.drives[self.cycle_index][1]      
            self.drives[self.cycle_index][0] = (n * -1)            
            print(f"pull_drive: level={self.level}, cycle={cycle}, index={self.cycle_index}, drive={n}, date={d}")
            return [n, d]
        else:
            print(f"pull_drive: level={self.level}, cycle={cycle}, index={self.cycle_index}, No drive to pull")
            return [0,0]
            
    def pull_from(self, other_level, pool, cycle):
        if self.is_used(cycle):
            print(f"pull_from: level={self.level}, cycle={cycle}, index={self.cycle_index}")            
            self.drives[self.cycle_index] = other_level.pull_drive(pool, cycle)
                                    
    def free_drive(self, pool, cycle):
        if self.is_used(cycle):
            self.cycle_index
            n = int(self.drives[self.cycle_index][0])
            if 0 < n:
                print(f"free_drive: level={self.level}, cycle={cycle}, index={self.cycle_index}")            
                pool.add_drive(self.drives[self.cycle_index][0])                        
                self.drives[self.cycle_index][0] = n * -1

    def next_drive(self, pool, cycle):
        if self.is_used(cycle):
            print(f"next_drive: level={self.level}, cycle={cycle}, index={self.cycle_index}")            
            self.drives[self.cycle_index][0] = pool.get_next_drive()
            self.drives[self.cycle_index][1] = self.cycle_date
            
            
    def csv_data(self):
        s = ''
        for i in range(self.num_drives):
            s +=  f",\"{str(self.drives[i][0])} ({self.drives[i][1]})\""
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
            if self.drives[i] != self.prevs[i]:
              s +=  f"\"{str(self.drives[i][0])} ({self.drives[i][1]})\""
        return s


dp = drive_pool()

l1 = rotation_level(1, 4, 1)
l2 = rotation_level(2, 3, 2)
l3 = rotation_level(3, 2, 4)

if False:
    l1.list_drives()
    l2.list_drives()
    l3.list_drives()

n_weeks = 10

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

if True:
    out_list = []
    s = f"iter,date{l1.csv_head()},.{l2.csv_head()},.{l3.csv_head()},notes"
    out_list += f"{s}\n"
    out_list2 = out_list.copy()
    
    start_date = date(2020,7,4)
    
    for w in range(n_weeks):
        d = start_date + timedelta(weeks=w)
        
        l1.start_cycle(w, d)
        l2.start_cycle(w, d)
        l3.start_cycle(w, d)
        
        l3.pull_from(l2, dp, w)
        
        l2.pull_from(l1, dp, w)
        
        l1.free_drive(dp, w)
        
        s = f"{w},{d}{l1.csv_data()},{l2.csv_data()},{l3.csv_data()},before next drive"
        out_list2 += f"{s}\n"
        
        l1.next_drive(dp, w)
        
        s = f"{w},{d}{l1.csv_data()},{l2.csv_data()},{l3.csv_data()},after next drive"
        out_list2 += f"{s}\n"

        s = f"{w},{d}{l1.csv_diff()},{l2.csv_diff()},{l3.csv_diff()}"
        out_list += f"{s}\n"

    with open('bakrot_output.csv', 'w') as out_file:
        out_file.writelines(out_list)

    with open('bakrot_output_data.csv', 'w') as out_file:
        out_file.writelines(out_list2)

if False:
    l1.list_drives()
    l2.list_drives()
    l3.list_drives()
