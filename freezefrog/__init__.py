import datetime
import time

import pytz

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

__all__ = ["FreezeTime"]


real_datetime = datetime.datetime


# From six
def with_metaclass(meta, *bases):
    """Create a base class with a metaclass."""
    return meta("NewBase", bases, {})


# Adapted from freezegun. This metaclass will make sure that calls to
# isinstance(real_datetime, FakeDateTime) are True.
class FakeDateTimeMeta(type):
    @classmethod
    def __instancecheck__(self, obj):
        return isinstance(obj, real_datetime)


class FakeDateTime(with_metaclass(FakeDateTimeMeta, real_datetime)):
    """
    A `datetime` mock class.

    Set the start datetime and the system timezone with `start(dt, tz)`. The
    clock starts ticking after calling `start`.
    """

    dt = None
    tz = None
    _start = None

    @classmethod
    def start(cls, dt, tz, tick):
        cls.dt = dt
        cls.tz = tz
        cls._start = time.monotonic() if tick else None

    @classmethod
    def time_since_start(cls):
        if cls._start is None:
            return datetime.timedelta(seconds=0)
        return datetime.timedelta(seconds=time.monotonic() - cls._start)

    @classmethod
    def now(cls, tz=None):
        if tz is None:
            return cls.dt + cls.time_since_start()
        return tz.normalize(cls.tz.localize(cls.dt) + cls.time_since_start())

    @classmethod
    def today(cls):
        return cls.now()

    @classmethod
    def utcnow(cls):
        return cls.now(tz=pytz.UTC)


def fake_time():
    return FakeDateTime.tz.localize(datetime.datetime.now()).timestamp()


class FreezeTime(object):
    """
    A context manager that freezes the datetime to the given datetime object.

    It simulates that the system timezone is the passed timezone.

    If `tick=True` is passed, the clock will tick, otherwise the clock will
    remain at the given datetime.

    Additional patch targets can be passed via `extra_patch_datetime` and
    `extra_patch_time` to patch the `datetime` class or `time` function if it
    was already imported in a different module. For example, if module `x`
    contains `from datetime import datetime` (as opposed to `import datetime`),
    it needs to be patched separately (`extra_patch_datetime=['x.datetime']`).
    """

    def __init__(
        self, dt, tz, tick=False, extra_patch_datetime=(), extra_patch_time=()
    ):
        datetime_targets = ("datetime.datetime",) + tuple(extra_patch_datetime)
        time_targets = ("time.time",) + tuple(extra_patch_time)

        self.patches = [
            patch(target, FakeDateTime) for target in datetime_targets
        ] + [patch(target, fake_time) for target in time_targets]

        self._dt = dt
        self._tz = tz
        self._tick = tick

    def __enter__(self):
        FakeDateTime.start(self._dt, self._tz, tick=self._tick)

        for p in self.patches:
            p.__enter__()

    def __exit__(self, *args):
        for p in reversed(self.patches):
            p.__exit__(*args)
