import datetime
from freezefrog import FreezeTime
import time
import unittest


class FreezeFrogTestCase(unittest.TestCase):
    def test_freeze(self):
        dt = datetime.datetime.utcnow()
        self.assertTrue(dt > datetime.datetime(2016, 1, 1))

        with FreezeTime(datetime.datetime(2014, 1, 1)):
            time.sleep(0.001)
            dt = datetime.datetime.utcnow()
            self.assertEqual(dt, datetime.datetime(2014, 1, 1))
            self.assertTrue(isinstance(dt, datetime.datetime))
            self.assertEqual(time.time(), 1388534400)

        dt = datetime.datetime.utcnow()
        self.assertTrue(dt > datetime.datetime(2016, 1, 1))

    def test_freeze_tick(self):
        with FreezeTime(datetime.datetime(2014, 1, 1), tick=True):
            time.sleep(0.001)
            dt = datetime.datetime.utcnow()
            start = datetime.datetime(2014, 1, 1)
            end = datetime.datetime(2014, 1, 1, 0, 0, 1)
            self.assertTrue(start < dt < end)
            self.assertTrue(1388534400 < time.time() < 1388534401)

    def test_now(self):
        regular_now = datetime.datetime.now()
        self.assertTrue(regular_now)
        with FreezeTime(datetime.datetime(2014, 1, 1)):
            self.assertRaises(NotImplementedError, datetime.datetime.now)
