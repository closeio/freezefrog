==========
FreezeFrog
==========
.. image:: https://circleci.com/gh/closeio/freezefrog/tree/master.svg?style=svg&circle-token=010565a97316df8a248f0f32d584357021a3873b
    :target: https://circleci.com/gh/closeio/freezefrog/tree/master

*FreezeFrog* lets you efficiently mock datetimes in unit tests.


(Interested in working on projects like this? `Close.io`_ is looking for `great engineers`_ to join our team)

.. _Close.io: http://close.io
.. _great engineers: http://jobs.close.io


.. contents:: Contents


Why FreezeFrog?
---------------

FreezeFrog is a Python library that lets you mock datetimes in unit tests. Its
goal is to be simple and fast.

* In comparison to certain other time freezing libraries, FreezeFrog doesn't loop
  through all imported modules, making it fast even for larger projects.

* FreezeFrog currently supports mocking the following basic methods:

  * ``datetime.datetime.now`` (if ``tz_delta`` is specified)

  * ``datetime.datetime.utcnow``

  * ``time.time``


Usage
-----

Use the ``FreezeTime`` context manager to freeze the time. Pass the desired
``datetime`` object to the constructor. The constructor also takes the ``tick``
keyword argument (``False`` by default), which makes the clock start ticking.

.. code:: python

  from freezefrog import FreezeTime
  import datetime

  with FreezeTime(datetime.datetime(2014, 1, 1)):
      # The clock is frozen.
      # Always prints 2014-01-01 00:00:00
      print datetime.datetime.utcnow()

  with FreezeTime(datetime.datetime(2014, 1, 1), tick=True):
      # The clock starts ticking immediately.
      # Example output: 2014-01-01 00:00:00.000005
      print datetime.datetime.utcnow()
