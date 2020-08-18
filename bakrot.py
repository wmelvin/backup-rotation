#!/usr/bin/env python3

from datetime import date
from datetime import timedelta

class DrivePool():
    def __init__(self):
        self.drivepool = []
        self.lastdrive = 0

    def get_next_drive(self):
        #print("len(self.drivepool)=%d" % len(self.drivepool))
        if len(self.drivepool) == 0:
            self.lastdrive = self.lastdrive + 1
            n = self.lastdrive
            print(f"DrivePool.get_next_drive: {n} new")
        else:
            n = self.drivepool.pop()
            print(f"DrivePool.get_next_drive: {n} from pool")
        return n
            
    def add_drive(self, drive_number):
        if 0 < drive_number:
            print(f"DrivePool.add_drive: {drive_number} added to pool")
            self.drivepool.append(drive_number)


class RotationLevel():
    def __init__(self, level, num_drives, usage_interval, drive_pool, lower_level_obj):
        self.level = level
        self.num_drives = num_drives
        self.usage_interval = usage_interval
        self.drive_pool = drive_pool
        self.next_level_down = lower_level_obj
        self.cycle_num = -1
        self.cycle_date = -1
        self.cycle_index = -1
        self.drives = [[0,0] for x in range(num_drives)]
        self.prevs =  [[0,0] for x in range(num_drives)]
        self.in_cycle = False
        
    def start_cycle(self, cycle_num, cycle_date):
        self.cycle_num = cycle_num
        self.cycle_date = cycle_date
        self.prevs = [[self.drives[x][0], self.drives[x][1]] for x in range(self.num_drives)]
        self.cycle_index = (self.usage_cycle(cycle_num) % self.num_drives)           
        self.in_cycle = ((cycle_num + 1) % self.usage_interval == 0)
        print(f"L{self.level} start_cycle {cycle_num}, date={cycle_date}, index={self.cycle_index}, in_cycle={self.in_cycle}")

        
    def list_drives(self):
        for i in range(self.num_drives):
            print(f"level={self.level}, index={i}, drive={self.drives[i]}, previous={self.prevs[i]}")
            
    def usage_cycle(self, cycle):
        n =  (cycle // self.usage_interval)           
        return n
            
    #def cycle_index(self, cycle):
    #    n =  (self.usage_cycle(cycle) % self.num_drives)           
    #    return n
            
    # def is_used(self, cycle):
    #     return ((cycle + 1) % self.usage_interval == 0)

    def pull_drive(self):
        n = int(self.drives[self.cycle_index][0])                
        if 0 < n:      
            d = self.drives[self.cycle_index][1]      
            self.drives[self.cycle_index][0] = (n * -1)            
            print(f"L{self.level} pull_drive: cycle={self.cycle_num}, index={self.cycle_index}, drive={n}, date={d}")
            return [n, d]
        else:
            print(f"L{self.level} pull_drive: cycle={self.cycle_num}, index={self.cycle_index}, No drive to pull")
            return [0,0]
            
    def pull_from_lower_level(self):
        if self.in_cycle:
            print(f"L{self.level} pull_from:  cycle={self.cycle_num}, index={self.cycle_index}")            
            self.drives[self.cycle_index] = self.next_level_down.pull_drive()
                                    
    def free_drive(self):
        if self.in_cycle:
            n = int(self.drives[self.cycle_index][0])
            if 0 < n:
                print(f"L{self.level} free_drive: cycle={self.cycle_num}, index={self.cycle_index}")            
                self.drive_pool.add_drive(self.drives[self.cycle_index][0])                        
                self.drives[self.cycle_index][0] = n * -1

    def next_drive(self):
        if self.in_cycle:
            print(f"L{self.level} next_drive: cycle={self.cycle_num}, index={self.cycle_index}")            
            self.drives[self.cycle_index][0] = self.drive_pool.get_next_drive()
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


#----------------------------------------------------------------------
# Main script:

start_date = date(2020,7,4)
n_weeks = 10

dp = DrivePool()

l1 = RotationLevel(1, 4, 1, dp, None)
l2 = RotationLevel(2, 3, 2, dp, l1)
l3 = RotationLevel(3, 2, 4, dp, l2)


if False:
    l1.list_drives()
    l2.list_drives()
    l3.list_drives()


if False:
    s = ",level-1,level-1,level-1,level-2,level-2,level-2,level-3,level-3,level-3"
    print(s)
    s = "i,usage_cycle,cycle_index,is_used,usage_cycle,cycle_index,is_used,usage_cycle,cycle_index,is_used"
    print(s)
    
    for w in range(n_weeks):
        d = start_date + timedelta(weeks=w)
        l1.start_cycle(w, d)
        l2.start_cycle(w, d)
        l3.start_cycle(w, d)
        s = f"{w},{l1.cycle_num},{l1.cycle_index},{l1.in_cycle:1}"
        s += f",{l2.cycle_num},{l2.cycle_index},{l2.in_cycle:1}"
        s += f",{l3.cycle_num},{l3.cycle_index},{l3.in_cycle:1}"
        print(s)


if True:
    out_list = []
    s = f"iter,date{l1.csv_head()},.{l2.csv_head()},.{l3.csv_head()},notes"
    out_list += f"{s}\n"
    out_list2 = out_list.copy()
    
    for week_num in range(n_weeks):
        week_date = start_date + timedelta(weeks=week_num)
        
        l1.start_cycle(week_num, week_date)
        l2.start_cycle(week_num, week_date)
        l3.start_cycle(week_num, week_date)
        
        l3.pull_from_lower_level()        
        l2.pull_from_lower_level()
        
        l1.free_drive()
        
        s = f"{week_num},{week_date}{l1.csv_data()},{l2.csv_data()},{l3.csv_data()},before next drive"
        out_list2 += f"{s}\n"
        
        l1.next_drive()
        
        s = f"{week_num},{week_date}{l1.csv_data()},{l2.csv_data()},{l3.csv_data()},after next drive"
        out_list2 += f"{s}\n"

        s = f"{week_num},{week_date}{l1.csv_diff()},{l2.csv_diff()},{l3.csv_diff()}"
        out_list += f"{s}\n"

    with open('bakrot_output.csv', 'w') as out_file:
        out_file.writelines(out_list)

    with open('bakrot_output_data.csv', 'w') as out_file:
        out_file.writelines(out_list2)


if False:
    l1.list_drives()
    l2.list_drives()
    l3.list_drives()
