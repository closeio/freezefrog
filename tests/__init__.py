import datetime
from freezefrog import FreezeTime
import time
import unittest

PAST_DATETIME = datetime.datetime(2014, 1, 1)
PAST_TIME = 1388534400

class FreezeFrogTestCase(unittest.TestCase):
    def test_freeze(self):
        dt = datetime.datetime.utcnow()
        self.assertTrue(dt > datetime.datetime(2016, 1, 1))

        with FreezeTime(PAST_DATETIME):
            time.sleep(0.001)
            dt = datetime.datetime.utcnow()
            self.assertEqual(dt, PAST_DATETIME)
            self.assertTrue(isinstance(dt, datetime.datetime))
            self.assertEqual(time.time(), PAST_TIME)

        dt = datetime.datetime.utcnow()
        self.assertTrue(dt > datetime.datetime(2016, 1, 1))

    def test_freeze_extra(self):
        from . import module

        # Doesn't work since we've imported the sample module already.
        with FreezeTime(PAST_DATETIME):
            t, dt = module.get_info()
            self.assertNotEqual(t, PAST_TIME)
            self.assertNotEqual(dt, PAST_DATETIME)

        # Works as expected.
        with FreezeTime(PAST_DATETIME,
                        extra_patch_time=['tests.module.time'],
                        extra_patch_datetime=['tests.module.datetime']):
            t, dt = module.get_info()
            self.assertEqual(t, PAST_TIME)
            self.assertEqual(dt, PAST_DATETIME)

    def test_freeze_tick(self):
        with FreezeTime(PAST_DATETIME, tick=True):
            time.sleep(0.001)
            dt = datetime.datetime.utcnow()
            start = PAST_DATETIME
            end = PAST_DATETIME + datetime.timedelta(seconds=1)
            self.assertTrue(start < dt < end)
            self.assertTrue(PAST_TIME < time.time() < PAST_TIME+1)

    def test_now(self):
        regular_now = datetime.datetime.now()
        self.assertTrue(regular_now)
        with FreezeTime(datetime.datetime(2014, 1, 1)):
            self.assertRaises(NotImplementedError, datetime.datetime.now)
