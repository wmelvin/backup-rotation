#  Adding some tests after the fact. Better late than never?

from datetime import date
from importlib import reload
from textwrap import dedent

import bakplan


class Flogger:
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
                "cycles": "10",
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


def test_get_cycle_first_last_date():

    #  TODO: Putting this here as an example. It is probably not necessary
    #  to reload for this test. Move to a test that needs it (to reset any
    #  module-level vars in bakplan) when such a test exists.
    #
    reload(bakplan)

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
