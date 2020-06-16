import calendar
import datetime

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

__all__ = ['FreezeTime']


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
    A datetime replacement that lets you set utcnow() using set_utcnow().

    The clock starts ticking after calling set_utcnow().
    """
    tz_delta = None

    @classmethod
    def utcnow(cls, *args, **kwargs):
        if not hasattr(cls, 'dt'):
            raise NotImplementedError(
                'use {}.set_utcnow(datetime) first'.format(cls.__name__)
            )
        return cls._utcnow()

    @classmethod
    def set_utcnow(cls, dt):
        cls.dt = dt

    @classmethod
    def set_tz_delta(cls, tz_delta):
        cls.tz_delta = tz_delta

    @classmethod
    def _utcnow(cls):
        if not hasattr(cls, '_start'):
            cls._start = real_datetime.utcnow()
        return (real_datetime.utcnow() - cls._start) + cls.dt

    @classmethod
    def now(cls, *args, **kwargs):
        if cls.tz_delta is not None:
            return cls.utcnow() + cls.tz_delta
        else:
            raise Exception(
                '{}.now() requires setting tz_delta'.format(cls.__name__)
            )


class FakeFixedDateTime(FakeDateTime):
    @classmethod
    def _utcnow(cls):
        return cls.dt


def fake_time():
    now = datetime.datetime.utcnow()
    ts = calendar.timegm(now.timetuple())
    ts += now.microsecond / 1e6
    return ts


class FreezeTime(object):
    """
    A context manager that freezes the datetime to the given datetime object.

    If tick=True is passed, the clock will start ticking, otherwise the clock
    will remain at the given datetime.

    If `tz_delta` is passed, `datetime.datetime.now()` can be used with the
    given UTC delta which is added to the frozen datetime.

    Additional patch targets can be passed via `extra_patch_datetime` and
    `extra_patch_time` to patch the datetime class or time function if it was
    already imported in a different module. For example, if module `x` contains
    `from datetime import datetime` (as opposed to `import datetime`), it needs
    to be patched separately (`extra_patch_datetime=['x.datetime']`).
    """
    def __init__(self, dt, tick=False, extra_patch_datetime=[],
                 extra_patch_time=[], tz_delta=None):
        datetime_targets = ['datetime.datetime'] + extra_patch_datetime
        time_targets = ['time.time'] + extra_patch_time

        if tick:
            self.datetime_cls = FakeDateTime
        else:
            self.datetime_cls = FakeFixedDateTime

        self.patches = (
            [patch(target, self.datetime_cls) for target in datetime_targets] +
            [patch(target, fake_time) for target in time_targets]
        )

        self.datetime_cls.set_utcnow(dt)

        self.tz_delta = tz_delta

    def __enter__(self):
        self.datetime_cls.set_tz_delta(self.tz_delta)

        for p in self.patches:
            p.__enter__()

    def __exit__(self, *args):
        for p in reversed(self.patches):
            p.__exit__(*args)

        self.datetime_cls.set_tz_delta(None)
