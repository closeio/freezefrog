import datetime
import time
import unittest

import pytz

from freezefrog import FreezeTime

PAST_DATETIME = datetime.datetime(2014, 1, 1)
PAST_TIME_UTC_TIMESTAMP = 1388534400
PAST_TIME_NEW_YORK_TIMESTAMP = 1388552400
TEN_SEC_DELTA = datetime.timedelta(seconds=10)


class FreezeFrogTestCase(unittest.TestCase):
    def test_freeze_no_tick_utc(self):
        utc_naive_past_datetime = pytz.UTC.localize(PAST_DATETIME).replace(
            tzinfo=None
        )

        dt = datetime.datetime.now()
        self.assertTrue(dt > datetime.datetime(2016, 1, 1))

        with FreezeTime(PAST_DATETIME, pytz.UTC):
            self.assertTrue(
                isinstance(datetime.datetime.now(), datetime.datetime)
            )

            time.sleep(0.001)
            self.assertEqual(datetime.datetime.now(), PAST_DATETIME)
            self.assertEqual(datetime.datetime.today(), PAST_DATETIME)
            self.assertEqual(
                datetime.datetime.utcnow(), utc_naive_past_datetime
            )

            self.assertEqual(
                datetime.datetime.now(pytz.UTC),
                pytz.UTC.localize(PAST_DATETIME),
            )

            self.assertEqual(time.time(), PAST_TIME_UTC_TIMESTAMP)

        dt = datetime.datetime.now()
        self.assertTrue(dt > datetime.datetime(2016, 1, 1))

    def test_freeze_tick_utc(self):
        utc_naive_past_datetime = pytz.UTC.localize(PAST_DATETIME).replace(
            tzinfo=None
        )

        dt = datetime.datetime.now()
        self.assertTrue(dt > datetime.datetime(2016, 1, 1))

        with FreezeTime(PAST_DATETIME, pytz.UTC, tick=True):
            self.assertTrue(
                isinstance(datetime.datetime.now(), datetime.datetime)
            )

            time.sleep(0.001)
            self.assertTrue(
                PAST_DATETIME
                < datetime.datetime.now()
                < PAST_DATETIME + TEN_SEC_DELTA
            )
            self.assertTrue(
                PAST_DATETIME
                < datetime.datetime.today()
                < PAST_DATETIME + TEN_SEC_DELTA
            )
            self.assertTrue(
                utc_naive_past_datetime
                < datetime.datetime.utcnow()
                < utc_naive_past_datetime + TEN_SEC_DELTA
            )

            self.assertTrue(
                PAST_TIME_UTC_TIMESTAMP
                < time.time()
                < PAST_TIME_UTC_TIMESTAMP + 1
            )

        dt = datetime.datetime.now()
        self.assertTrue(dt > datetime.datetime(2016, 1, 1))

    def test_freeze_new_york(self):
        ny_to_utc_naive_past_datetime = pytz.UTC.normalize(
            pytz.timezone("America/New_York").localize(PAST_DATETIME)
        ).replace(tzinfo=None)
        with FreezeTime(PAST_DATETIME, pytz.timezone("America/New_York")):
            self.assertEqual(
                datetime.datetime.utcnow(), ny_to_utc_naive_past_datetime
            )

    def test_freeze_extra(self):
        from . import module

        # Doesn't work since we've imported the sample module already.
        with FreezeTime(PAST_DATETIME, pytz.UTC):
            t, dt = module.get_info()
            self.assertNotEqual(t, PAST_TIME_UTC_TIMESTAMP)
            self.assertNotEqual(dt, PAST_DATETIME)

        # Works as expected.
        with FreezeTime(
            PAST_DATETIME,
            pytz.UTC,
            extra_patch_time=["tests.module.time"],
            extra_patch_datetime=["tests.module.datetime"],
        ):
            t, dt = module.get_info()
            self.assertEqual(t, PAST_TIME_UTC_TIMESTAMP)
            self.assertEqual(dt, PAST_DATETIME)
