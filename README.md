# pevl
Python Event Versioning Library

![](https://github.com/silarsis/pevl/workflows/Python%20Event%20Versioning%20Libary/badge.svg)

This library provides code to upgrade events. Think of it as an event equivalent to flyway,
where you can define the mappings between events and have all incoming events upgraded to
a version your code can deal with, on the fly.

The target environment is either an event sourcing system, or microservices with
an event bus - anywhere you're consuming events and doing something with them.

Pre-requisites
==============

All events must be versioned. That is, there must be a version number in the event
structure somewhere.

There must be a way to map from a given event version to version+1 for every version number.
This is typically done by defining an upgrade method.

The library provides a class, `Upgrader`, which will take events in, extract the
version number, run all appropriate upgrade methods until the version is current, then
call an event factory with the upgraded data and return the appropriate object.

Design decisions (and whys)
===========================

* Factory is only called with the latest data, not for each version - this is to save
  from having to maintain factories for every version.

* Supporting Python 3.8 and above - because I want static types.

* All events are dictionaries - for simplicity. Events are deepcopy'ed as part of the implementation.

* Upgrade methods may mutate events in place - each event is provided as a deepcopy (so don't upgrade things that don't deepcopy).
  If you return, that will be used - if not, the assumed mutated event will be used.

* Upgrade methods will get dictionaries and return dictionaries, and wrapping will be invisible - because
  I want this to be as simple to use as possible.

* All versions should be strings, not numbers or other oddball things - for simplicity.

* No version will be represented with str(None) (ie. 'None')

How to Use
==========

Create a module that holds a bunch of version upgrade methods.

Each method should use the `@pevl.event.upgrade` decorator, and in the decorator you specify a version number to apply to and a new-version number to set (otherwise you must set the new version number in the upgrade script itself).

Each method should apply an appropriate upgrade from the version number given to the next version number.

Each method should be named descriptively.

Each method takes an event :dict, and returns an event: dict

Version numbers do not need to sort properly - but each version needs to upgrade to another version that is then handled (or not, if final version)

Example:

```python
from pevl.event import upgrade

@upgrade('v0.1', 'v0.2')
def split_first_last_name(event):
    event['first'], event['last'] = event['name'].split()
```

The code to upgrade the events:

```python
from pevl.event import Upgrader

upgrader = event.Upgrader(upgrades=[split_first_name, ])
upgraded = upgrader.ingest(event, target_version='v0.2')
```

For an example of the code that does the upgrades, see `sample_sns.py`

Likely Failure Modes
====================

Make sure your versions match what comes out of the event itself. str/int mismatches may be silently ignored.

Make sure you have a version. Again, failed version matches may be ignored.