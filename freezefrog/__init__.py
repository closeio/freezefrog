import datetime
from mock import patch
import time

__all__ = ['FreezeTime']


# From six
def with_metaclass(meta, *bases):
    """Create a base class with a metaclass."""
    return meta("NewBase", bases, {})

# Adapted from freezegun. This metaclass will make sure that calls to
# isinstance(real_datetime, FakeDateTime) are True.
real_datetime = datetime.datetime
class FakeDateTimeMeta(type):
    @classmethod
    def __instancecheck__(self, obj):
        return isinstance(obj, real_datetime)

class FakeDateTime(with_metaclass(FakeDateTimeMeta, real_datetime)):
    """
    A datetime replacement that lets you set utcnow() using set_utcnow().

    The clock starts ticking after calling set_utcnow().
    """

    @classmethod
    def utcnow(cls, *args, **kwargs):
        if not hasattr(cls, 'dt'):
            raise NotImplementedError('use {}.set_utcnow(datetime) first'.format(cls.__name__))
        return cls._utcnow()

    @classmethod
    def set_utcnow(cls, dt):
        cls.dt = dt

    @classmethod
    def _utcnow(cls):
        if not hasattr(cls, '_start'):
            cls._start = real_datetime.utcnow()
        return (real_datetime.utcnow() - cls._start) + cls.dt

class FakeFixedDateTime(FakeDateTime):
    @classmethod
    def _utcnow(cls):
        return cls.dt

def fake_time():
    now = datetime.datetime.utcnow()
    ts = time.mktime(now.timetuple())
    ts += now.microsecond / 1e6
    return ts

class FreezeTime(object):
    """
    A context manager that freezes the datetime to the given datetime object.

    If tick=True is passed, the clock will start ticking, otherwise the clock
    will remain at the given datetime.
    """
    def __init__(self, dt, tick=False):
        self.dt = dt
        self.tick = tick

    def __enter__(self):
        if self.tick:
            datetime_cls = FakeDateTime
        else:
            datetime_cls = FakeFixedDateTime

        self.p1 = patch('datetime.datetime', datetime_cls)
        self.p2 = patch('time.time', fake_time)

        self.p1.__enter__()
        self.p2.__enter__()

        datetime_cls.set_utcnow(self.dt)

    def __exit__(self, *args):
        self.p2.__exit__(*args)
        self.p1.__exit__(*args)
