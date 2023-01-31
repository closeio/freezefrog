==========
FreezeFrog
==========
.. image:: https://circleci.com/gh/closeio/freezefrog/tree/master.svg?style=svg&circle-token=010565a97316df8a248f0f32d584357021a3873b
    :target: https://circleci.com/gh/closeio/freezefrog/tree/master

*FreezeFrog* lets you mock datetimes in tests.

(Interested in working on projects like this? `Close`_ is looking for `great engineers`_ to join our team.)

.. _Close: https://close.com
.. _great engineers: https://jobs.close.com

.. contents:: Contents

Why FreezeFrog?
---------------

FreezeFrog is a Python library that lets you mock datetimes in tests. Its goal
is to be simple and fast.

* In comparison to certain other time freezing libraries, FreezeFrog doesn't
  loop through all imported modules, making it fast even for larger projects.

* FreezeFrog currently supports mocking the following basic methods:

  * ``datetime.datetime.now``

  * ``datetime.datetime.utcnow``

  * ``time.time``

* FreezeFrog supports both ``datetime`` and ``pytz`` timezone objects.

Usage
-----

Use the ``FreezeTime`` context manager to freeze the time. Pass the desired
``datetime`` object to the constructor, and the timezone to mock the system's
timezone (defaults to `datetime.timzone.utc`). The constructor also takes the
``fold`` argument (``0`` by default), which defines whether an ambiguous time
refers to its first or second appearance, and the ``tick`` argument
(``False`` by default), which makes the clock start ticking.

.. code:: python

  import datetime

  from freezefrog import FreezeTime

  with FreezeTime(datetime.datetime(2014, 1, 1)):
      # The clock is frozen.
      # Always prints 2014-01-01 00:00:00
      print(datetime.datetime.utcnow())

  with FreezeTime(datetime.datetime(2014, 1, 1), tick=True):
      # The clock starts ticking immediately.
      # Example output: 2014-01-01 00:00:00.000005
      print(datetime.datetime.utcnow())
