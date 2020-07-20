import datetime
import time
from unittest.mock import patch

try:
    import pytz
except ImportError:
    pass

__all__ = ["FreezeTime"]


real_datetime = datetime.datetime


def is_pytz(tz):
    return hasattr(tz, "localize")


def get_pytz_dst_from_fold(dt, tz, fold):
    """
    The relationship between pytz's `is_dst` and datetime's `fold` is not
    obvious:

    datetime's `fold` lets you say you want either the earlier time
    (fold=0) or the later time (fold=1) during the DST transition period.

    pytz's `is_dst` lets you say whether you want to time that was inside the
    DST interval (the non-standard timezone offset for that region), or outside
    (the standard timezone offset for that region).

    Because the time can be rewinded when the DST kicks in, or when it's being
    rolled out:
    - `is_dst=False and fold=0`: Time rewinded when the DST kicked in, and you
        want the earliest.
    - `is_dst=True and fold=0`: Time rewinded when the DST rolled out, and you
        want the earliest.
    - `is_dst=False and fold=1`: Time rewinded when the DST rolled out, and you
        want the latest.
    - `is_dst=True and fold=1`: Time rewinded when the DST kicked in, and you
        want the latest.
    """
    non_dst_in_utc = pytz.UTC.normalize(tz.localize(dt, is_dst=False))
    dst_in_utc = pytz.UTC.normalize(tz.localize(dt, is_dst=True))
    if fold:
        return dst_in_utc > non_dst_in_utc
    return non_dst_in_utc > dst_in_utc


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
    def _initialize(cls, dt, tz, fold, tick):
        cls.dt = dt
        cls.tz = tz
        cls._start = time.monotonic() if tick else None

        if is_pytz(tz):
            cls.dt_in_utc = pytz.UTC.normalize(
                tz.localize(dt, is_dst=get_pytz_dst_from_fold(dt, tz, fold))
            )
        else:
            cls.dt_in_utc = dt.replace(tzinfo=tz, fold=fold).astimezone(
                datetime.timezone.utc
            )

    @classmethod
    def _time_since_start(cls):
        if cls._start is None:
            return datetime.timedelta(seconds=0)
        return datetime.timedelta(seconds=time.monotonic() - cls._start)

    @classmethod
    def now(cls, tz=None):
        if tz is None:
            return cls.dt + cls._time_since_start()
        if is_pytz(tz):
            return tz.normalize(cls.dt_in_utc + cls._time_since_start())
        return (cls.dt_in_utc + cls._time_since_start()).astimezone(tz)

    @classmethod
    def today(cls):
        return cls.now()

    @classmethod
    def utcnow(cls):
        return cls.now(tz=datetime.timezone.utc).replace(tzinfo=None)


def fake_time():
    return FakeDateTime.now(FakeDateTime.tz).timestamp()


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
        self,
        dt,
        tz,
        fold=0,
        tick=False,
        extra_patch_datetime=(),
        extra_patch_time=(),
    ):
        datetime_targets = ("datetime.datetime",) + tuple(extra_patch_datetime)
        time_targets = ("time.time",) + tuple(extra_patch_time)

        self.patches = [
            patch(target, FakeDateTime) for target in datetime_targets
        ] + [patch(target, fake_time) for target in time_targets]

        self._dt = dt
        self._tz = tz
        self._fold = fold
        self._tick = tick

    def __enter__(self):
        FakeDateTime._initialize(
            self._dt, self._tz, fold=self._fold, tick=self._tick
        )

        for p in self.patches:
            p.__enter__()

    def __exit__(self, *args):
        for p in reversed(self.patches):
            p.__exit__(*args)
