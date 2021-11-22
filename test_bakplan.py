#  test_bakplan.py
#  Adding some tests after the fact. Better late than never?

from datetime import date
from importlib import reload
from textwrap import dedent

import backup_retention
import bakplan


def test_get_cycle_first_last_date():
    #  The date being accessed is the first item in the list.
    fake_cycle = [
        [date(2021, 8, 31), "x"],
        [date(2021, 11, 16), "x"],
        [date(2021, 7, 31), "x"],
        [date(2021, 8, 1), "x"],
    ]
    first_date, last_date = bakplan.get_cycle_first_last_date(fake_cycle)
    assert date(2021, 7, 31) == first_date
    assert date(2021, 11, 16) == last_date


class FakeLogger:
    def __init__(self):
        self.entries = []
        self.steps = []

    def log_msg(self, msg):
        self.entries.append(msg)

    def log_step(self, msg):
        self.steps.append(msg)


def get_rotation_scheme_json():
    return dedent(
        """
        {
            "rotation_scheme": {
                "name": "Test1",
                "startdate": "2021-01-01",
                "cycles": "12",
                "period": "weeks",
                "levels": [
                    {"level": 1, "slots": 2, "interval": 1},
                    {"level": 2, "slots": 2, "interval": 2},
                    {"level": 3, "slots": 2, "interval": 4}
                ]
            }
        }
        """
    )


def test_run_cycles():
    reload(bakplan)

    flog = FakeLogger()
    config = get_rotation_scheme_json()
    scheme = bakplan.get_scheme_from_json(config, "test_run_cycles")
    pool = backup_retention.SlotPool(flog)
    levels = bakplan.create_retention_levels(scheme, pool, flog)

    bakplan.run_cycles(scheme, levels, flog)

    #  For starters, just check that it did "something."
    assert 0 < len(bakplan.outlist_main)

    #  To cause the test to fail, and show the contents of a list in the
    #  terminal for review, uncomment a line to assign print_a_list.
    #
    print_a_list = []
    # print_a_list = flog.steps
    # print_a_list = flog.entries
    # print_a_list = bakplan.outlist_main
    # print_a_list = bakplan.outlist_wdates
    # print_a_list = bakplan.outlist_detail
    # print_a_list = bakplan.all_cycles
    for item in print_a_list:
        print(item)
    assert 0 == len(print_a_list)
