#!/usr/bin/env python3

# 2020-08-17 

from datetime import datetime
from datetime import date
from datetime import timedelta
import string


logfilename = 'bakrot_log.txt'


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


def plog(msg):
    with open(logfilename,  'a') as log_file:        
        print(msg)
        log_file.write(f"[{datetime.now():%Y%m%d_%H%M%S}] {msg}\n")


class DrivePool():
    def __init__(self):
        self.drivepool = []
        self.lastdrive = 0

    def get_next_drive(self):
        if len(self.drivepool) == 0:
            self.lastdrive = self.lastdrive + 1
            n = self.lastdrive
            plog(f"DrivePool.get_next_drive: {n} new")
        else:
            n = self.drivepool.pop()
            plog(f"DrivePool.get_next_drive: {n} from pool")
        return n
            
    def add_drive(self, drive_number):
        if 0 < drive_number:
            plog(f"DrivePool.add_drive: {drive_number} added to pool")
            self.drivepool.append(drive_number)


# class DriveSlot():
#     def __init__(self, drive_num=0, backup_date=0):
#         self.__drive_num = drive_num
#         self.__backup_date = backup_date

#     @property
#     def drive_num(self):
#         return self.__drive_num
    
#     @drive_num.setter
#     def drive_num(self, drive_num):
#         __drive_num = drive_num

#     @property
#     def backup_date(self):
#         return self.__backup_date
    
#     @backup_date.setter
#     def backup_date(self, backup_date):
#         __backup_date = backup_date

#     def mark_free(self):
#         self.__drive_num *= -1

class DriveSlot():
    def __init__(self, drive_num=0, backup_date=0):
        self.drive_num = drive_num
        self.backup_date = backup_date

    def __repr__(self):
        return f"({self.drive_num}, {self.backup_date})"

    def __eq__(self, other) -> bool:
        if type(self) != type(other):
            return False
        else:
            return (
                self.drive_num == other.drive_num
                and self.backup_date == other.backup_date
            )

    def mark_free(self):
        self.drive_num *= -1



class RotationLevel():
    def __init__(self, level, num_drives, usage_interval, drive_pool, rotation_level_below):
        self.level = level
        self.num_drives = num_drives
        self.usage_interval = usage_interval
        self.drive_pool = drive_pool
        self.level_below = rotation_level_below
        self.cycle_num = -1
        self.cycle_date = -1
        self.cycle_index = -1
        
        #self.drives = [[0,0] for x in range(num_drives)]
        self.drives = [DriveSlot() for x in range(num_drives)]

        #self.prevs =  [[0,0] for x in range(num_drives)]
        self.prevs =  [DriveSlot() for x in range(num_drives)]

        self.in_cycle = False
        
    def start_cycle(self, cycle_num, cycle_date):
        self.cycle_num = cycle_num
        self.cycle_date = cycle_date
        
        #self.prevs = [[self.drives[x][0], self.drives[x][1]] for x in range(self.num_drives)]
        #self.prevs = [DriveSlot(self.drives[x].drive_num, self.drives[x].backup_date) for x in range(self.num_drives)]
        #self.prevs = [DriveSlot(self.drives[x]) for x in range(self.num_drives)]
        for x in range(self.num_drives):
            self.prevs[x] = copy(self.drives[x])
        
        self.cycle_index = (self.usage_cycle(cycle_num) % self.num_drives)           
        self.in_cycle = ((cycle_num + 1) % self.usage_interval == 0)
        plog(f"L{self.level} start_cycle {cycle_num}, date={cycle_date}, index={self.cycle_index}, in_cycle={self.in_cycle}")

        
    def list_drives(self):
        for i in range(self.num_drives):
            plog(f"level={self.level}, index={i}, drive={self.drives[i]}, previous={self.prevs[i]}")
            
    def usage_cycle(self, cycle):
        n =  (cycle // self.usage_interval)           
        return n
            
    def pull_drive(self):
        #n = int(self.drives[self.cycle_index][0])                
        n = self.drives[self.cycle_index].drive_num                
        if 0 < n:      
            # d = self.drives[self.cycle_index][1]      
            # self.drives[self.cycle_index][0] = (n * -1)            
            d = self.drives[self.cycle_index].backup_date      
            self.drives[self.cycle_index].mark_free

            plog(f"L{self.level} pull_drive: cycle={self.cycle_num}, index={self.cycle_index}, drive={n}, date={d}")
            return DriveSlot(n, d)
        else:
            if not self.level_below is None:
                return self.level_below.pull_drive()
            else:
                plog(f"L{self.level} pull_drive: cycle={self.cycle_num}, index={self.cycle_index}, No drive to pull")
                return DriveSlot(0,0)
            
    def pull_from_lower_level(self):
        if self.in_cycle:
            plog(f"L{self.level} pull_from_lower_level:  cycle={self.cycle_num}, index={self.cycle_index}")            

            pulled = self.level_below.pull_drive()
            if 0 < pulled.drive_num:
                self.free_drive()
                self.drives[self.cycle_index] = pulled


    def free_drive(self):
        if self.in_cycle:
            #n = int(self.drives[self.cycle_index][0])
            n = int(self.drives[self.cycle_index].drive_num)
            if 0 < n:
                plog(f"L{self.level} free_drive: cycle={self.cycle_num}, index={self.cycle_index}")            
                # self.drive_pool.add_drive(self.drives[self.cycle_index][0])                        
                # self.drives[self.cycle_index][0] = n * -1
                self.drive_pool.add_drive(self.drives[self.cycle_index].drive_num)                        
                self.drives[self.cycle_index].mark_free

    def next_drive(self):
        if self.in_cycle:
            plog(f"L{self.level} next_drive: cycle={self.cycle_num}, index={self.cycle_index}")            
            # self.drives[self.cycle_index][0] = self.drive_pool.get_next_drive()
            # self.drives[self.cycle_index][1] = self.cycle_date            
            self.drives[self.cycle_index].drive_num = self.drive_pool.get_next_drive()
            self.drives[self.cycle_index].backup_date = self.cycle_date            
            
    def csv_data(self):
        s = ''
        for i in range(self.num_drives):
            #s +=  f",\"{str(self.drives[i][0])} ({self.drives[i][1]})\""
            s +=  f",\"{str(self.drives[i].drive_num)} ({self.drives[i].backup_date})\""
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
                #s +=  f"\"{str(self.drives[i][0])} ({self.drives[i][1]})\""
                s +=  f"\"{str(self.drives[i].drive_num)} ({self.drives[i].backup_date})\""

        return s

    def get_drives_in_use(self):
        #drives_list = [[x[0], x[1]] for x in self.drives if 0 < x[0]]

        drives_list = []

        for x in range(self.num_drives):
            #if 0 < self.drives[x][0]:
            if 0 < self.drives[x].drive_num:
                
                #drives_list.append(self.drives[x])
                tmp = (self.drives[x].backup_date.strftime('%Y-%m-%d'), to_alpha_label(self.drives[x].drive_num))
                drives_list.append(tmp)

        if not self.level_below is None:
            drvs = self.level_below.get_drives_in_use()
            for x in range(len(drvs)):
                drives_list.append(drvs[x])
            #drives_list.append(self.level_below.get_drives_in_use())
        
        #drives_list.sort(key=lambda drive: drive[0])
        
        #return sorted(drives_list, key=lambda item: item.drive_num)
        #return sorted(drives_list, key=lambda item: item.backup_date)
        return sorted(drives_list)



#----------------------------------------------------------------------
# Main script:

start_date = date(2020,7,4)
#n_weeks = 104
n_weeks = 52

dp = DrivePool()

l1 = RotationLevel(1, 5, 1, dp, None)
l2 = RotationLevel(2, 3, 2, dp, l1)
l3 = RotationLevel(3, 2, 4, dp, l2)

#l1 = RotationLevel(1, 7, 1, dp, None)
#l2 = RotationLevel(2, 8, 2, dp, l1)
#l3 = RotationLevel(3, 6, 4, dp, l2)


if False:
    l1.list_drives()
    l2.list_drives()
    l3.list_drives()


if False:
    s = ",level-1,level-1,level-1,level-2,level-2,level-2,level-3,level-3,level-3"
    plog(s)
    s = "i,usage_cycle,cycle_index,is_used,usage_cycle,cycle_index,is_used,usage_cycle,cycle_index,is_used"
    plog(s)
    
    for w in range(n_weeks):
        d = start_date + timedelta(weeks=w)
        l1.start_cycle(w, d)
        l2.start_cycle(w, d)
        l3.start_cycle(w, d)
        s = f"{w},{l1.cycle_num},{l1.cycle_index},{l1.in_cycle:1}"
        s += f",{l2.cycle_num},{l2.cycle_index},{l2.in_cycle:1}"
        s += f",{l3.cycle_num},{l3.cycle_index},{l3.in_cycle:1}"
        plog(s)


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
        
        l3.pull_from_lower_level()        

        l2.pull_from_lower_level()
        
        l1.free_drive()
        
        s = f"{week_num},{week_date}{l1.csv_data()},{l2.csv_data()},{l3.csv_data()},before next drive"
        out_list2 += f"{s}\n"
        
        l1.next_drive()

        all_cycles.append(l3.get_drives_in_use())
        
        s = f"{week_num},{week_date}{l1.csv_data()},{l2.csv_data()},{l3.csv_data()},after next drive"
        out_list2 += f"{s}\n"

        s = f"{week_num},{week_date}{l1.csv_diff()},{l2.csv_diff()},{l3.csv_diff()}"
        out_list += f"{s}\n"

    #for x in range(len(all_cycles)):
    #    print(all_cycles[x])

    with open('bakrot_output.csv', 'w') as out_file:
        out_file.writelines(out_list)

    with open('bakrot_output_data.csv', 'w') as out_file:
        out_file.writelines(out_list2)

    with open('bakrot_output_cycles.csv', 'w') as out_file:
        for cycle in all_cycles:
            for item in cycle:
                out_file.write(f"\"{item}\",")
            out_file.write(f"\n")


if False:
    l1.list_drives()
    l2.list_drives()
    l3.list_drives()
