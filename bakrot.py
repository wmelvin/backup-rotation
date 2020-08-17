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
        #print("len(self.drivepool)=%d" % len(self.drivepool))
        if len(self.drivepool) == 0:
            self.lastdrive = self.lastdrive + 1
            n = self.lastdrive
        else:
            n = self.drivepool.pop()
        print("drive_pool.get_next_drive()=%d" % n)
        return n
            
    def add_drive(self, drive_number):
        if 0 < drive_number:
            print("drive_pool.add_drive(%d)" % drive_number)
            self.drivepool.append(drive_number)



class rotation_level():
    def __init__(self, level, num_drives, usage_interval):
        self.level = level
        self.num_drives = num_drives
        self.usage_interval = usage_interval
        self.drives = []
        for i in range(num_drives):
            self.drives.append(0)
        #print("Drives: ", self.drives)

    def list_drives(self):
        for i in range(self.num_drives):
            print(self.level, i, self.drives[i])
            
    def usage_iteration(self, iteration):
        n =  (iteration // self.usage_interval)           
        return n
            
    def iteration_index(self, iteration):
        n =  (self.usage_iteration(iteration) % self.num_drives)           
        return n
            
    def is_used(self, iteration):
        return ((iteration + 1) % self.usage_interval == 0)

    def pull_drive(self, pool, iteration):
        ix = self.iteration_index(iteration)
        
        #print(f"pull_drive: level={self.level}, iteration={iteration}, len(drives)={len(self.drives)}, drive_index={drive_index}")
        
        n = int(self.drives[ix])
        
        print(f"pull_drive: level={self.level}, iteration={iteration}, index={ix}, value={n}")
        
        if 0 < n:
            pool.add_drive(n)
            self.drives[ix] = (n * -1)
            return n        
            
    def pull_from(self, other_level, pool, iteration):
        if self.is_used(iteration):
            ix = self.iteration_index(iteration)
            
            print(f"pull_from: level={self.level}, iteration={iteration}, index={ix}")
            
            self.drives[ix] = other_level.pull_drive(pool, iteration)
                                    
    def free_drive(self, pool, iteration):
        if self.is_used(iteration):
            ix = self.iteration_index(iteration)
            
            print(f"free_drive: level={self.level}, iteration={iteration}, index={ix}")
            
            pool.add_drive(self.drives[ix])
            
            n = int(self.drives[ix])
            n = n * -1
            self.drives[ix] = n

    def next_drive(self, pool, iteration):
        if self.is_used(iteration):
            ix = self.iteration_index(iteration)
            
            print(f"next_drive: level={self.level}, iteration={iteration}, index={ix}")
            
            self.drives[ix] = pool.get_next_drive()

    def as_csv(self):
        s = ''
        for i in range(self.num_drives):
            s +=  "," + str(self.drives[i])
        return s


dp = drive_pool()

l1 = rotation_level(1, 7, 1)
l2 = rotation_level(2, 5, 2)
l3 = rotation_level(3, 4, 4)

#l1.list_drives()
#l2.list_drives()
#l3.list_drives()


#start_date = date(2020,7,4)
#
#for w in range(0,20):
#    d = start_date + timedelta(weeks=w)
#    
#    print("\n" + str(d))
#    
#    l3.pull_from(l2, dp, w)
#    
#    l2.pull_from(l1, dp, w)
#    
#    l1.free_drive(dp, w)
#    
#    print(w, l1.as_csv(), l2.as_csv(), l3.as_csv())
#    
#    l1.next_drive(dp, w)
#    
#    print(w, l1.as_csv(), l2.as_csv(), l3.as_csv())


s = ",level-1,level-1,level-1,level-2,level-2,level-2,level-3,level-3,level-3"
print(s)
s = "i,usage_iteration,iteration_index,is_used,usage_iteration,iteration_index,is_used,usage_iteration,iteration_index,is_used"
print(s)

for w in range(0,20):
    #print(w)


    s = f"{w},{l1.usage_iteration(w)},{l1.iteration_index(w)},{l1.is_used(w):1}"
    s += f",{l2.usage_iteration(w)},{l2.iteration_index(w)},{l2.is_used(w):1}"
    s += f",{l3.usage_iteration(w)},{l3.iteration_index(w)},{l3.is_used(w):1}"
    print(s)
    #print(l1.usage_iteration(w), l1.iteration_index(w), l1.is_used(w))
    #print(l2.usage_iteration(w), l2.iteration_index(w), l2.is_used(w))
    #print(l3.usage_iteration(w), l3.iteration_index(w), l3.is_used(w))

