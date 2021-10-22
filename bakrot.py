#!/usr/bin/env python3

# ---------------------------------------------------------------------
# bakrot.py
#
# Backup roation calculator.
#
# ---------------------------------------------------------------------

from datetime import date, datetime, timedelta
from pathlib import Path

from backup_retention import SlotPool, RetentionLevel, to_alpha_label
from plogger import Plogger


app_version = "211022.1"

app_label = f"bakrot.py version {app_version}"


def get_levels_as_csv(prefix, levels_list, add_notes, do_diff, do_dates):
    s = f"{prefix}"

    actions_list = []

    for x in range(len(levels)):
        if do_diff:
            s += f"{levels_list[x].csvfrag_changed_slots(do_dates)},"
        else:
            s += f"{levels_list[x].csvfrag_all_slots(do_dates)},"

        for a in levels_list[x].cycle_actions:
            actions_list.append(a)

    actions_list.reverse()

    actions_str = ""
    for action in actions_list:
        actions_str += f"{action} "

    s += ',"{0}","{1}"{2}'.format(actions_str.strip(), add_notes, "\n")
    return s


def get_cycle_first_last_date(cycle):
    first_date = date.max
    last_date = date.min
    for item in cycle:
        item_backup_date = item[0]
        if item_backup_date < first_date:
            first_date = item_backup_date
        if item_backup_date > last_date:
            last_date = item_backup_date
    return first_date, last_date


# ---------------------------------------------------------------------
# Main script:

run_at = datetime.now()

#  Include date_time suffix, or not:
# output_suffix = f"-{run_at.strftime('%Y%m%d_%H%M%S')}"
output_suffix = ''


#  Set scheme here:
backup_scheme = 4

output_path = Path.cwd() / "output"
assert output_path.exists()

output_path = output_path / f"bakrot_{run_at.strftime('%Y%m%d_%H%M%S')}"
assert not output_path.exists()

output_path.mkdir()
assert output_path.exists()

filename_prefix = f"{str(output_path)}/bakrot-{backup_scheme}{output_suffix}"

filename_output_main = f"{filename_prefix}-1.csv"
filename_output_wdates = f"{filename_prefix}-2-wdates.csv"
filename_output_detail = f"{filename_prefix}-3-detail.csv"
filename_output_cycles = f"{filename_prefix}-4-cycles.csv"
filename_output_usage = f"{filename_prefix}-5-usage.csv"
filename_output_range = f"{filename_prefix}-6-range.csv"
filename_output_steps = f"{filename_prefix}-7-steps.txt"
filename_output_summary = f"{filename_prefix}-8-summary.txt"

plog = Plogger("bakrot_log.txt", filename_output_steps)

plog.log2(f"{app_label}\n")
plog.log2(f"Run started at {run_at.strftime('%Y-%m-%d %H:%M:%S')}")

start_date = date(2020, 7, 5)

#  Cycles are weeks in this insance.
n_years = 5
n_weeks = 52 * n_years

pool = SlotPool(plog)

if backup_scheme == 0:
    l1 = RetentionLevel(1, 5, 1, pool, None, plog)
    l2 = RetentionLevel(2, 4, 2, pool, l1, plog)
    l3 = RetentionLevel(3, 10, 4, pool, l2, plog)
    levels = [l1, l2, l3]

elif backup_scheme == 1:
    l1 = RetentionLevel(1, 7, 1, pool, None, plog)
    l2 = RetentionLevel(2, 4, 2, pool, l1, plog)
    l3 = RetentionLevel(3, 8, 6, pool, l2, plog)
    levels = [l1, l2, l3]

elif backup_scheme == 2:
    l1 = RetentionLevel(1, 7, 1, pool, None, plog)
    l2 = RetentionLevel(2, 4, 2, pool, l1, plog)
    l3 = RetentionLevel(3, 4, 4, pool, l2, plog)
    l4 = RetentionLevel(4, 2, 8, pool, l3, plog)
    l5 = RetentionLevel(5, 2, 16, pool, l4, plog)
    levels = [l1, l2, l3, l4, l5]

elif backup_scheme == 3:
    l1 = RetentionLevel(1, 7, 1, pool, None, plog)
    l2 = RetentionLevel(2, 4, 2, pool, l1, plog)
    l3 = RetentionLevel(3, 4, 4, pool, l2, plog)
    l4 = RetentionLevel(4, 2, 8, pool, l3, plog)
    l5 = RetentionLevel(5, 2, 12, pool, l4, plog)
    levels = [l1, l2, l3, l4, l5]

else:
    #  Scheme 4
    l1 = RetentionLevel(1, 7, 1, pool, None, plog)
    l2 = RetentionLevel(2, 4, 2, pool, l1, plog)
    l3 = RetentionLevel(3, 4, 4, pool, l2, plog)
    l4 = RetentionLevel(4, 4, 8, pool, l3, plog)
    levels = [l1, l2, l3, l4]

top_index = len(levels) - 1

total_slots = 0
for x in range(len(levels)):
    total_slots += levels[x].num_slots

plog.log2("\nLevels:\n")
for x in range(len(levels)):
    plog.log2(
        "Level {}: slots = {}, interval = {}.".format(
            levels[x].level,
            levels[x].num_slots,
            levels[x].usage_interval,
        )
    )

dbg_list_levels = False
dbg_list_cycles = False
do_run_main = True

if dbg_list_levels:
    for x in range(len(levels)):
        levels[x].list_slots()


if dbg_list_cycles:
    s = ",level-1,level-1,level-1,level-2,level-2,level-2,"
    +"level-3,level-3,level-3"
    plog.log(s)

    s = "i,usage_cycle,cycle_index,is_used,usage_cycle,cycle_index,is_used,"
    +"usage_cycle,cycle_index,is_used"
    plog.log(s)

    for w in range(n_weeks):
        d = start_date + timedelta(weeks=w)

        for x in range(len(levels)):
            levels[x].start_cycle(w, d)

        s = f"{w},"
        for x in range(len(levels) - 1, -1, -1):
            s += ",{0},{1},{2:1}".format(
                levels[x].cycle_num,
                levels[x].cycle_index,
                levels[x].in_cycle,
            )

        plog.log(s)

plog.log2(f"\nCycles ({n_weeks}):\n")

if do_run_main:
    all_cycles = []
    outlist_main = []

    header_csv = '"cycle","date"'
    for x in range(len(levels)):
        header_csv += f"{levels[x].csvfrag_header()},."
    header_csv += ',"Actions", "Notes"{0}'.format("\n")

    outlist_main += header_csv

    outlist_wdates = outlist_main.copy()
    outlist_detail = outlist_main.copy()

    for week_num in range(n_weeks):
        week_date = start_date + timedelta(weeks=week_num)

        plog.log2(f"Cycle {week_num} (week of {week_date:%Y-%m-%d}):")

        info_prefix = f"{week_num},{week_date}"

        for x in range(len(levels)):
            levels[x].start_cycle(week_num, week_date)

        for x in range(top_index, 0, -1):
            levels[x].pull_from_lower_level()

        l1.free_slot()

        outlist_detail += get_levels_as_csv(
            info_prefix, levels, "before next slot", False, True
        )

        l1.next_slot()

        all_cycles.append(levels[top_index].get_slots_in_use())

        outlist_detail += get_levels_as_csv(
            info_prefix, levels, "after next slot", False, True
        )

        outlist_main += get_levels_as_csv(info_prefix, levels, "", True, False)

        outlist_wdates += get_levels_as_csv(
            info_prefix, levels, "", True, True
        )

    print(f"Writing {filename_output_main}")
    with open(filename_output_main, "w") as out_file:
        out_file.writelines(outlist_main)

    print(f"Writing {filename_output_wdates}")
    with open(filename_output_wdates, "w") as out_file:
        out_file.writelines(outlist_wdates)

    print(f"Writing {filename_output_detail}")
    with open(filename_output_detail, "w") as out_file:
        out_file.writelines(outlist_detail)

    print(f"Writing {filename_output_range}")
    min_days = 0
    max_days = 0
    with open(filename_output_range, "w") as out_file:
        out_file.write("Cycle,FirstDate,LastDate,Days\n")
        n = 0
        for cycle in all_cycles:
            first_date, last_date = get_cycle_first_last_date(cycle)
            days_between = (last_date - first_date).days
            out_file.write(
                "{0},{1},{2},{3}{4}".format(
                    n,
                    first_date.strftime("%Y-%m-%d"),
                    last_date.strftime("%Y-%m-%d"),
                    days_between,
                    "\n",
                )
            )
            # If all slots were full then include this cycle for min
            # and max days range. This is reported in the summary file.
            if len(cycle) == total_slots:
                if (days_between < min_days) or (min_days == 0):
                    min_days = days_between
                if days_between > max_days:
                    max_days = days_between
            n += 1

    all_dates = []
    for cycle in all_cycles:
        for item in cycle:
            item_date = item[0].strftime("%Y-%m-%d")
            if item_date not in all_dates:
                all_dates.append(item_date)

    all_dates.sort()

    print(f"Writing {filename_output_cycles}")
    with open(filename_output_cycles, "w") as out_file:
        for d in all_dates:
            s = d
            for cycle in all_cycles:
                slot_str = ","
                for item in cycle:
                    item_date = item[0].strftime("%Y-%m-%d")
                    if item_date == d:
                        slot_str = ',"{0} U{1} L{2}.{3}"'.format(
                            to_alpha_label(item[1]), item[2], item[3], item[4]
                        )
                        break
                s += slot_str
            out_file.write(f"{s}\n")

print(f"Writing {filename_output_usage}")
with open(filename_output_usage, "w") as out_file:
    out_file.write("Level,Slot,UseCount\n")
    for x in range(len(levels)):
        for y in range(levels[x].num_slots):
            rs = levels[x].slots[y]
            a = to_alpha_label(rs.slot_num)
            n = rs.use_count
            s = f"{levels[x].level},{a},{n}\n"
            out_file.write(s)


print(f"Writing {filename_output_summary}")
with open(filename_output_summary, "w") as out_file:
    out_file.write(f"{app_label}\n")
    out_file.write(
        f"\nRun started at {run_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
    )
    out_file.write(f"\nBackup scheme: {backup_scheme}\n")
    out_file.write("\nLevels:\n")
    for x in range(len(levels)):
        out_file.write(
            "  Level {0}: slots = {1}, interval = {2}.{3}".format(
                levels[x].level,
                levels[x].num_slots,
                levels[x].usage_interval,
                "\n",
            )
        )
    out_file.write(f"\nTotal media slots: {total_slots}\n")
    out_file.write(
        "\nDays from oldest to newest backup (after all slots full):\n"
    )
    out_file.write(f"  Minimum days = {min_days}\n")
    out_file.write(f"  Maximum days = {max_days}\n")


if dbg_list_levels:
    for x in range(len(levels)):
        levels[x].list_slots()

print("Done.")
