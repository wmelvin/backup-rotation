#!/usr/bin/env python3

# ---------------------------------------------------------------------
# bakplan.py
#
# Backup rotation calculator.
# ---------------------------------------------------------------------

import argparse
import json
import sys

from collections import namedtuple
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import List

from backup_retention import SlotPool, RetentionLevel, to_alpha_label
from plogger import Plogger


AppOptions = namedtuple("AppOptions", "scheme_file, debug_level")


RotationScheme = namedtuple(
    "RotationScheme", "name, start_date, cycles, period, levels"
)


pub_version = "0.1.dev1"

app_version = "211220.1"

app_label = f"bakplan.py version {pub_version} (mod {app_version})"


all_cycles = []
outlist_main = []
outlist_wdates = []
outlist_detail = []


def date_fromisoformat(dts):
    """
    Take an ISO format date string and return a date type.
    The date.fromisoformat method was new in Python 3.7. This replacement
    works on 3.6.9, which the author is still has on some machines.
    It may work on older versions, but that is not the target.
    """
    #  ISO format: yyyy-mm-dd
    #              0....:....1
    try:
        assert len(dts) == 10
        y = int(dts[0:4])
        assert dts[4] == "-"
        m = int(dts[5:7])
        assert dts[7] == "-"
        d = int(dts[8:10])
        dt = date(y, m, d)
    except Exception:
        raise ValueError(f"Invalid date string: '{dts}'")
    return dt


def debug_log_levels(
    opts: AppOptions, levels_list: List[RetentionLevel], plog: Plogger
):
    if 0 < opts.debug_level:
        plog.log_msg("BEGIN debug_log_levels")
        for x in range(len(levels_list)):
            levels_list[x].debug_log_slots()
        plog.log_msg("END debug_log_levels")


def get_levels_as_csv(prefix, levels_list, add_notes, do_diff, do_dates):
    s = f"{prefix}"

    actions_list = []

    for x in range(len(levels_list)):
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

    s += ',"{0}","{1}"'.format(actions_str.strip(), add_notes)
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


def get_scheme_from_json(json_str: str, source_name: str) -> RotationScheme:
    try:
        data = json.loads(json_str)

        scheme_raw = data["rotation_scheme"]

        period = str(scheme_raw["period"]).strip().lower().rstrip("s")

        if period not in ["day", "week"]:
            sys.stderr.write(
                f"ERROR in rotation_scheme from '{source_name}'\n"
            )
            sys.stderr.write(
                'The value for "period" must be "day" or "week".\n'
            )
            sys.exit(1)

        scheme = RotationScheme(
            scheme_raw["name"],
            date_fromisoformat(scheme_raw["startdate"]),
            int(scheme_raw["cycles"]),
            period,
            scheme_raw["levels"],
        )
    except KeyError as e:
        sys.stderr.write(f"ERROR in rotation_scheme from '{source_name}'\n")
        sys.stderr.write(f"Missing key: {e}\n")
        sys.exit(1)

    return scheme


def get_scheme_from_file(file_name) -> RotationScheme:
    with open(file_name, "r") as f:
        s = f.read()

    return get_scheme_from_json(s, file_name)


def get_args(argv):
    ap = argparse.ArgumentParser(
        description="Calculates a backup media rotation plan given a rotation "
        + "scheme."
    )
    # TODO: Expand description.

    ap.add_argument(
        "scheme_file",
        action="store",
        help="Path to the JSON file that defines the backup rotation scheme.",
    )

    ap.add_argument(
        "--debug-level",
        dest="debug_level",
        type=int,
        action="store",
        help="Write extra debug information. Level: 0=none, 1=all. "
        + "Default is 0.",
    )

    return ap.parse_args(argv[1:])


def get_opts(argv) -> AppOptions:
    args = get_args(argv)

    scheme_path = Path(args.scheme_file)

    if not scheme_path.exists():
        sys.stderr.write(f"\nERROR: File not found: '{scheme_path}'\n")
        sys.exit(1)

    if args.debug_level is None:
        debug_level = 0
    else:
        debug_level = args.debug_level

    return AppOptions(str(scheme_path), debug_level)


def create_retention_levels(
    scheme: RotationScheme, pool: SlotPool, plog: Plogger
) -> List[RetentionLevel]:

    levels: List[RetentionLevel] = []

    for x in range(len(scheme.levels)):
        assert scheme.levels[x]["level"] == (x + 1)
        if x == 0:
            #  For first level, level_below is None.
            level = RetentionLevel(
                scheme.levels[x]["level"],
                scheme.levels[x]["slots"],
                scheme.levels[x]["interval"],
                pool,
                None,
                plog,
            )
            levels.append(level)
        else:
            level = RetentionLevel(
                scheme.levels[x]["level"],
                scheme.levels[x]["slots"],
                scheme.levels[x]["interval"],
                pool,
                levels[-1],
                plog,
            )
            levels.append(level)
    return levels


def run_cycles(
    scheme: RotationScheme, levels: List[RetentionLevel], plog: Plogger
):
    header_csv = '"cycle","date"'
    for x in range(len(levels)):
        header_csv += f"{levels[x].csvfrag_header()},."
    header_csv += ',"Actions", "Notes"'
    outlist_main.append(header_csv)
    outlist_wdates.append(header_csv)
    outlist_detail.append(header_csv)

    top_level_index = len(levels) - 1

    plog.log_step(f"\nCycles ({scheme.cycles}):\n")

    for cycle_num in range(scheme.cycles + 1):
        if scheme.period == "day":
            cycle_date = scheme.start_date + timedelta(days=cycle_num)
            plog.log_step(f"Cycle {cycle_num} ({cycle_date:%Y-%m-%d}):")
        else:
            cycle_date = scheme.start_date + timedelta(weeks=cycle_num)
            plog.log_step(
                f"Cycle {cycle_num} (week of {cycle_date:%Y-%m-%d}):"
            )

        info_prefix = f"{cycle_num},{cycle_date}"

        for x in range(len(levels)):
            levels[x].start_cycle(cycle_num, cycle_date)

        for x in range(top_level_index, 0, -1):
            levels[x].pull_from_lower_level()

        levels[0].free_slot()

        outlist_detail.append(
            get_levels_as_csv(
                info_prefix, levels, "before next slot", False, True
            )
        )

        levels[0].next_slot()

        all_cycles.append(levels[top_level_index].get_slots_in_use())

        outlist_detail.append(
            get_levels_as_csv(
                info_prefix, levels, "after next slot", False, True
            )
        )

        outlist_main.append(
            get_levels_as_csv(info_prefix, levels, "", True, False)
        )

        outlist_wdates.append(
            get_levels_as_csv(info_prefix, levels, "", True, True)
        )


def output_list_to_file(outlist, file_name):
    print(f"Writing {file_name}")
    with open(file_name, "w") as f:
        for s in outlist:
            f.write(f"{s}\n")


def main(argv):
    run_at = datetime.now()

    opts = get_opts(argv)

    scheme = get_scheme_from_file(opts.scheme_file)

    assert 0 < len(scheme.name)
    assert 0 < len(scheme.levels)

    output_home = Path.cwd() / "output"
    if not output_home.exists():
        output_home.mkdir()

    output_path = output_home / "bakplan_{0}_{1}".format(
        run_at.strftime("%Y%m%d_%H%M%S"), scheme.name
    )
    #  Per-run output directory should not exist at this point.
    assert not output_path.exists()

    output_path.mkdir()
    assert output_path.exists()

    outname_prefix = str(output_path / "bakplan")

    outname_main = f"{outname_prefix}-1.csv"
    outname_wdates = f"{outname_prefix}-2-wdates.csv"
    outname_detail = f"{outname_prefix}-3-detail.csv"
    outname_cycles = f"{outname_prefix}-4-cycles.csv"
    outname_usage = f"{outname_prefix}-5-usage.csv"
    outname_range = f"{outname_prefix}-6-range.csv"
    outname_steps = f"{outname_prefix}-7-steps.txt"
    outname_summary = f"{outname_prefix}-8-summary.txt"

    filename_log = str(output_path / "bakplan_log.txt")

    plog = Plogger(
        log_file_name=filename_log,
        log_immediate=False,
        log_timestamp=False,
        steps_file_name=outname_steps,
        steps_immediate=False,
    )

    plog.log_step(f"{app_label}\n")
    plog.log_step(f"Run started at {run_at.strftime('%Y-%m-%d %H:%M:%S')}")

    pool = SlotPool(plog)

    levels = create_retention_levels(scheme, pool, plog)

    total_slots = 0
    for x in range(len(levels)):
        total_slots += levels[x].num_slots

    plog.log_step("\nLevels:\n")
    for x in range(len(levels)):
        plog.log_step(
            "Level {}: slots = {}, interval = {}.".format(
                levels[x].level,
                levels[x].num_slots,
                levels[x].usage_interval,
            )
        )

    debug_log_levels(opts, levels, plog)

    run_cycles(scheme, levels, plog)

    output_list_to_file(outlist_main, outname_main)

    output_list_to_file(outlist_wdates, outname_wdates)

    output_list_to_file(outlist_detail, outname_detail)

    print(f"Writing {outname_range}")
    min_days = 0
    max_days = 0
    with open(outname_range, "w") as out_file:
        out_file.write("Cycle,FirstDate,LastDate,Days\n")
        n = 0
        for cycle in all_cycles:
            first_date, last_date = get_cycle_first_last_date(cycle)
            days_between = (last_date - first_date).days
            out_file.write(
                "{0},{1},{2},{3}\n".format(
                    n,
                    first_date.strftime("%Y-%m-%d"),
                    last_date.strftime("%Y-%m-%d"),
                    days_between,
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

    print(f"Writing {outname_cycles}")
    with open(outname_cycles, "w") as out_file:
        for d in all_dates:
            s = d
            for cycle in all_cycles:
                slot_str = ","
                for item in cycle:
                    item_date = item[0].strftime("%Y-%m-%d")
                    if item_date == d:
                        slot_str = ',"{0} U{1} L{2}.{3}"'.format(
                            to_alpha_label(item[1]),
                            item[2],
                            item[3],
                            item[4],
                        )
                        break
                s += slot_str
            out_file.write(f"{s}\n")

    print(f"Writing {outname_usage}")
    with open(outname_usage, "w") as out_file:
        out_file.write("Level,Slot,UseCount\n")
        for x in range(len(levels)):
            for y in range(levels[x].num_slots):
                rs = levels[x].slots[y]
                a = to_alpha_label(rs.slot_num)
                n = rs.use_count
                s = f"{levels[x].level},{a},{n}\n"
                out_file.write(s)

    print(f"Writing {outname_summary}")
    with open(outname_summary, "w") as out_file:
        out_file.write(f"{app_label}\n")
        out_file.write(
            f"\nRun started at {run_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        )
        out_file.write(f"\nBackup scheme: {scheme.name}\n")
        out_file.write("\nLevels:\n")
        for x in range(len(levels)):
            out_file.write(
                "  Level {0}: slots = {1}, interval = {2}.\n".format(
                    levels[x].level,
                    levels[x].num_slots,
                    levels[x].usage_interval,
                )
            )
        out_file.write(f"\nTotal media slots: {total_slots}\n")
        out_file.write("\nDays from oldest to newest backup:\n")
        if 0 < max_days:
            out_file.write(f"  Minimum days = {min_days}\n")
            out_file.write(f"  Maximum days = {max_days}\n")
        else:
            out_file.write(
                "  N/A (Not enough cycles to fill all rotation slots.)\n"
            )

    debug_log_levels(opts, levels, plog)

    print(f"Writing {outname_steps}")
    plog.save_steps()

    print(f"Writing {filename_log}")
    plog.save_log()

    print("Done.")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
