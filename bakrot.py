#!/usr/bin/env python3

# 2020-09-04 

from datetime import date, datetime, timedelta

#from bakrotate import DrivePool, RotationLevel, to_alpha_label
from backup_retention import SlotPool, RetentionLevel, to_alpha_label

from plogger import Plogger


def get_levels_info_str(prefix, levels_list, suffix, do_diff):
    s = f"{prefix}"
    for x in range(len(levels)):
        if do_diff:
            s += f"{levels_list[x].csv_diff()},"
        else:
            s += f"{levels_list[x].csv_data()},"
    s += f",\"{suffix}\"\n"
    #return f"{s}\n"
    return s


#----------------------------------------------------------------------
# Main script:

run_at = datetime.now()

now_stamp = run_at.strftime('%Y%m%d_%H%M%S')

# Set scheme here:
backup_scheme = 4


filename_output_main = f"output-bakrot-{backup_scheme}-{now_stamp}.csv"
filename_output_data = f"output-bakrot-{backup_scheme}-{now_stamp}-detail.csv"
filename_output_cycles = f"output-bakrot-{backup_scheme}-{now_stamp}-cycles.csv"
filename_output_usage = f"output-bakrot-{backup_scheme}-{now_stamp}-usage.csv"
filename_output_steps = f"output-bakrot-{backup_scheme}-{now_stamp}-steps.txt"

plog = Plogger('bakrot_log.txt', filename_output_steps)

plog.log2(f"Run started at {run_at.strftime('%Y-%m-%d %H:%M:%S')}")

start_date = date(2020,7,4)

n_weeks = 156

pool = SlotPool(plog)

if backup_scheme == 0:
    l1 = RetentionLevel(1, 5, 1, pool, None, plog)
    l2 = RetentionLevel(2, 3, 2, pool, l1, plog)
    l3 = RetentionLevel(3, 6, 4, pool, l2, plog)
    # total slots         14
    levels = [l1, l2, l3]

elif backup_scheme == 1:
    l1 = RetentionLevel(1, 7,  1, pool, None, plog)
    l2 = RetentionLevel(2, 5,  2, pool, l1, plog)
    l3 = RetentionLevel(3, 3,  4, pool, l2, plog)
    l4 = RetentionLevel(4, 4, 12, pool, l3, plog)    
    # total slots         19
    levels = [l1, l2, l3, l4]

elif backup_scheme == 2:
    l1 = RetentionLevel(1, 7,  1, pool, None, plog)
    l2 = RetentionLevel(2, 5,  2, pool, l1, plog)
    l3 = RetentionLevel(3, 4,  4, pool, l2, plog)
    l4 = RetentionLevel(4, 3,  8, pool, l3, plog)
    l5 = RetentionLevel(5, 2, 16, pool, l4, plog)
    # total slots         21
    levels = [l1, l2, l3, l4, l5]

elif backup_scheme == 3:
    l1 = RetentionLevel(1, 7,  1, pool, None, plog)
    l2 = RetentionLevel(2, 5,  2, pool, l1, plog)
    l3 = RetentionLevel(3, 3,  4, pool, l2, plog)
    l4 = RetentionLevel(4, 2,  9, pool, l3, plog)
    l5 = RetentionLevel(5, 1, 18, pool, l4, plog)
    # total slots         18
    levels = [l1, l2, l3, l4, l5]

else:
    #-- Scheme 4
    l1 = RetentionLevel(1, 3,  1, pool, None, plog)
    l2 = RetentionLevel(2, 4,  2, pool, l1, plog)
    l3 = RetentionLevel(3, 6,  4, pool, l2, plog)
    l4 = RetentionLevel(4, 8,  8, pool, l3, plog)
    l5 = RetentionLevel(5, 10, 16, pool, l4, plog)
    # total slots         30
    levels = [l1, l2, l3, l4, l5]

plog.log2(f"\nLevels:\n")
for x in range(len(levels)):
    plog.log2(f"Level {levels[x].level}: slots = {levels[x].num_slots}, interval = {levels[x].usage_interval}.")

dbg_list_levels = False
dbg_list_cycles = False
do_run_main = True

if dbg_list_levels:
    for x in range(len(levels)):
        levels[x].list_slots()


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

plog.log2(f"\nCycles ({n_weeks}):\n")

if do_run_main:
    all_cycles = []
    out_list = []

    header_csv = "iter,date"
    for x in range(len(levels)):
        header_csv += f"{levels[x].csv_head()},."
    header_csv += f",\"Notes\"\n"

    out_list += header_csv

    out_list2 = out_list.copy()

    for week_num in range(n_weeks):
        week_date = start_date + timedelta(weeks=week_num)

        plog.log2(f"Week of {week_date:%Y-%m-%d}")

        info_prefix = f"{week_num},{week_date}"

        for x in range(len(levels)):
            levels[x].start_cycle(week_num, week_date)

        for x in range(len(levels)-1, 0, -1):
            levels[x].pull_from_lower_level()

        l1.free_slot()

        out_list2 += get_levels_info_str(info_prefix, levels, "before next slot", False)

        l1.next_slot()

        all_cycles.append(levels[len(levels)-1].get_slots_in_use())

        out_list2 += get_levels_info_str(info_prefix, levels, "after next slot", False)

        out_list += get_levels_info_str(info_prefix, levels, "", True)


    with open(filename_output_main, 'w') as out_file:
        out_file.writelines(out_list)


    with open(filename_output_data, 'w') as out_file:
        out_file.writelines(out_list2)


    all_dates = []
    for cycle in all_cycles:
        for item in cycle:
            item_date = item[0].strftime('%Y-%m-%d')
            if not item_date in all_dates:
                all_dates.append(item_date)

    all_dates.sort()


    with open(filename_output_cycles, 'w') as out_file:
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


with open(filename_output_usage, 'w') as out_file:
    out_file.write(f"Level,Slot,UseCount\n")
    for x in range(len(levels)):
        for y in range(levels[x].num_slots):
            rs = levels[x].slots[y]
            a = to_alpha_label(rs.slot_num)
            n = rs.use_count
            s = f"{levels[x].level},{a},{n}\n"
            out_file.write(s)


if dbg_list_levels:
    for x in range(len(levels)):
        levels[x].list_slots()


