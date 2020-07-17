import datetime
import time
import unittest

import pytz
import dateutil.tz

from freezefrog import FreezeTime

PAST_DATETIME = datetime.datetime(2014, 1, 1)
PAST_TIME_UTC_TIMESTAMP = 1388534400
PAST_TIME_NEW_YORK_TIMESTAMP = 1388552400
TEN_SEC_DELTA = datetime.timedelta(seconds=10)


class FreezeFrogTestCase(unittest.TestCase):
    def test_isinstance(self):
        with FreezeTime(PAST_DATETIME, pytz.UTC):
            self.assertTrue(
                isinstance(datetime.datetime.now(), datetime.datetime)
            )

    def test_freeze_no_tick(self):
        dt = datetime.datetime.now()
        self.assertTrue(dt > datetime.datetime(2016, 1, 1))

        with FreezeTime(PAST_DATETIME, pytz.UTC):
            time.sleep(0.001)
            self.assertEqual(datetime.datetime.now(), PAST_DATETIME)
            self.assertEqual(datetime.datetime.today(), PAST_DATETIME)
            self.assertEqual(datetime.datetime.utcnow(), PAST_DATETIME)
            self.assertEqual(
                datetime.datetime.now(pytz.UTC),
                pytz.UTC.localize(PAST_DATETIME),
            )
            self.assertEqual(time.time(), PAST_TIME_UTC_TIMESTAMP)

        dt = datetime.datetime.now()
        self.assertTrue(dt > datetime.datetime(2016, 1, 1))

    def test_freeze_tick(self):
        dt = datetime.datetime.now()
        self.assertTrue(dt > datetime.datetime(2016, 1, 1))

        with FreezeTime(PAST_DATETIME, pytz.UTC, tick=True):
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
                PAST_DATETIME
                < datetime.datetime.utcnow()
                < PAST_DATETIME + TEN_SEC_DELTA
            )
            self.assertTrue(
                PAST_TIME_UTC_TIMESTAMP
                < time.time()
                < PAST_TIME_UTC_TIMESTAMP + 1
            )

        dt = datetime.datetime.now()
        self.assertTrue(dt > datetime.datetime(2016, 1, 1))

    def test_freeze_new_york_pytz_interface(self):
        ny_to_utc_past_datetime = pytz.UTC.normalize(
            pytz.timezone("America/New_York").localize(PAST_DATETIME)
        )
        ny_to_utc_naive_past_datetime = ny_to_utc_past_datetime.replace(
            tzinfo=None
        )
        with FreezeTime(PAST_DATETIME, pytz.timezone("America/New_York")):
            self.assertEqual(datetime.datetime.now(), PAST_DATETIME)
            self.assertEqual(datetime.datetime.today(), PAST_DATETIME)
            self.assertEqual(
                datetime.datetime.utcnow(), ny_to_utc_naive_past_datetime
            )
            self.assertEqual(
                datetime.datetime.now(pytz.UTC), ny_to_utc_past_datetime,
            )
            self.assertEqual(time.time(), PAST_TIME_NEW_YORK_TIMESTAMP)

    def test_freeze_new_york_default_datetime_tz_interface(self):
        past_datetime_in_utc = PAST_DATETIME.replace(
            tzinfo=dateutil.tz.gettz("America/New_York")
        ).astimezone(datetime.timezone.utc)
        with FreezeTime(PAST_DATETIME, dateutil.tz.gettz("America/New_York")):
            self.assertEqual(datetime.datetime.now(), PAST_DATETIME)
            self.assertEqual(datetime.datetime.today(), PAST_DATETIME)
            self.assertEqual(
                datetime.datetime.utcnow(),
                past_datetime_in_utc.replace(tzinfo=None),
            )
            self.assertEqual(
                datetime.datetime.now(datetime.timezone.utc),
                past_datetime_in_utc,
            )
            self.assertEqual(time.time(), PAST_TIME_NEW_YORK_TIMESTAMP)

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
