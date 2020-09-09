#!/usr/bin/env python3

#----------------------------------------------------------------------
# bakrot.py
#
# Backup roation calculator.
#
# 2020-09-06 
#
#----------------------------------------------------------------------

from datetime import date, datetime, timedelta

from backup_retention import SlotPool, RetentionLevel, to_alpha_label

from plogger import Plogger


def get_levels_as_csv(prefix, levels_list, suffix, do_diff, do_dates):
    s = f"{prefix}"
    a = ''
    for x in range(len(levels)):
        if do_diff:
            s += f"{levels_list[x].csvfrag_changed_slots(do_dates)},"
            a += levels_list[x].cycle_actions
        else:
            s += f"{levels_list[x].csvfrag_all_slots(do_dates)},"
    s += f",\"{suffix}\",\"{a}\"\n"
    return s


#----------------------------------------------------------------------
# Main script:

run_at = datetime.now()

#-- Include date_time suffix, or not:
#output_suffix = f"-{run_at.strftime('%Y%m%d_%H%M%S')}"
output_suffix = ''


#-- Set scheme here:
backup_scheme = 4


filename_output_main = f"output-bakrot-{backup_scheme}{output_suffix}.csv"
filename_output_wdates = f"output-bakrot-{backup_scheme}{output_suffix}-wdates.csv"
filename_output_detail = f"output-bakrot-{backup_scheme}{output_suffix}-detail.csv"
filename_output_cycles = f"output-bakrot-{backup_scheme}{output_suffix}-cycles.csv"
filename_output_usage = f"output-bakrot-{backup_scheme}{output_suffix}-usage.csv"
filename_output_steps = f"output-bakrot-{backup_scheme}{output_suffix}-steps.txt"

plog = Plogger('bakrot_log.txt', filename_output_steps)

plog.log2(f"Run started at {run_at.strftime('%Y-%m-%d %H:%M:%S')}")

start_date = date(2020,7,4)

# Cycles are weeks in this insance.
#
n_weeks = 156
#n_weeks = 520

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
    l2 = RetentionLevel(2, 3,  2, pool, l1, plog)
    l3 = RetentionLevel(3, 4,  4, pool, l2, plog)
    l4 = RetentionLevel(4, 2,  8, pool, l3, plog)
    l5 = RetentionLevel(5, 2, 12, pool, l4, plog)
    # total slots         18
    levels = [l1, l2, l3, l4, l5]

else:
    #-- Scheme 4
    l1 = RetentionLevel(1, 7,  1, pool, None, plog)
    l2 = RetentionLevel(2, 5,  2, pool, l1, plog)
    l3 = RetentionLevel(3, 4,  4, pool, l2, plog)
    l4 = RetentionLevel(4, 3, 12, pool, l3, plog)
    # total slots         19
    levels = [l1, l2, l3, l4]

top_index = len(levels)-1

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
    outlist_main = []

    header_csv = '"cycle","date"'
    for x in range(len(levels)):
        header_csv += f"{levels[x].csvfrag_header()},."
    header_csv += f",\"Notes\"\n"

    outlist_main += header_csv

    outlist_wdates = outlist_main.copy()
    outlist_detail = outlist_main.copy()

    for week_num in range(n_weeks):
        week_date = start_date + timedelta(weeks=week_num)

        plog.log2(f"Week of {week_date:%Y-%m-%d}")

        info_prefix = f"{week_num},{week_date}"

        for x in range(len(levels)):
            levels[x].start_cycle(week_num, week_date)

        for x in range(top_index, 0, -1):
            levels[x].pull_from_lower_level()

        l1.free_slot()

        outlist_detail += get_levels_as_csv(info_prefix, levels, "before next slot", False, True)

        l1.next_slot()

        all_cycles.append(levels[top_index].get_slots_in_use())

        outlist_detail += get_levels_as_csv(info_prefix, levels, "after next slot", False, True)

        outlist_main += get_levels_as_csv(info_prefix, levels, "", True, False)
        
        outlist_wdates += get_levels_as_csv(info_prefix, levels, "", True, True)


    print(f"Writing {filename_output_main}")
    with open(filename_output_main, 'w') as out_file:
        out_file.writelines(outlist_main)

    print(f"Writing {filename_output_wdates}")
    with open(filename_output_wdates, 'w') as out_file:
        out_file.writelines(outlist_wdates)

    print(f"Writing {filename_output_detail}")
    with open(filename_output_detail, 'w') as out_file:
        out_file.writelines(outlist_detail)

    all_dates = []
    for cycle in all_cycles:
        for item in cycle:
            item_date = item[0].strftime('%Y-%m-%d')
            if not item_date in all_dates:
                all_dates.append(item_date)

    all_dates.sort()


    print(f"Writing {filename_output_cycles}")
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

print(f"Writing {filename_output_usage}")
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

print('Done.')
