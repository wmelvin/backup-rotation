#!/usr/bin/env python3

# 2020-08-26 

from datetime import datetime
from datetime import date
from datetime import timedelta
from bakrotate import DrivePool
from bakrotate import RotationLevel
from bakrotate import to_alpha_label


class Plogger():
    def __init__(self, filename):
        self.filename = filename

    def log(self, msg):
        # Print and log.
        with open(self.filename,  'a') as log_file:
            print(msg)
            log_file.write(f"[{datetime.now():%Y%m%d_%H%M%S}] {msg}\n")


def levels_info_str(prefix, levels_list, suffix, do_diff):
    s = f"{prefix}"
    for x in range(len(levels)):
        if do_diff:
            s += f"{levels_list[x].csv_diff()},"
        else:
            s += f"{levels_list[x].csv_data()},"
    s += suffix
    return s


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

levels = [l1, l2, l3, l4]

dbg_list_levels = False
dbg_list_cycles = False
do_run_main = True


if dbg_list_levels:
    for x in range(len(levels)):
        levels[x].list_drives()


if dbg_list_cycles:
    s = ",level-1,level-1,level-1,level-2,level-2,level-2,level-3,level-3,level-3"
    plog.log(s)
    s = "i,usage_cycle,cycle_index,is_used,usage_cycle,cycle_index,is_used,usage_cycle,cycle_index,is_used"
    plog.log(s)

    for w in range(n_weeks):
        d = start_date + timedelta(weeks=w)

        for x in range(len(levels)):
            levels[x].start_cycle(w, d)

        s = f"{w},"
        for x in range(len(levels)-1, -1 , -1):
            s += f",{levels[x].cycle_num},{levels[x].cycle_index},{levels[x].in_cycle:1}"

        plog.log(s)


if do_run_main:
    all_cycles = []
    out_list = []

    s = f"iter,date{l1.csv_head()},.{l2.csv_head()},.{l3.csv_head()},notes"
    
    out_list += f"{s}\n"

    out_list2 = out_list.copy()

    for week_num in range(n_weeks):
        week_date = start_date + timedelta(weeks=week_num)

        for x in range(len(levels)):
            levels[x].start_cycle(week_num, week_date)

        for x in range(len(levels)-1, 0, -1):
            levels[x].pull_from_lower_level()
        
        l1.free_drive()

        s = levels_info_str(f"{week_num},{week_date}", levels, "before next drive", False) 
        out_list2 += f"{s}\n"

        l1.next_drive()

        all_cycles.append(levels[len(levels)-1].get_drives_in_use())

        s = levels_info_str(f"{week_num},{week_date}", levels, "after next drive", False)         
        out_list2 += f"{s}\n"

        s = levels_info_str(f"{week_num},{week_date}", levels, "", True) 
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


if dbg_list_levels:
    for x in range(len(levels)):
        levels[x].list_drives()
