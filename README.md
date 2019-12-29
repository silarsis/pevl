# pevl
Python Event Versioning Library

This library covers the heavy lifting for event versioning in python.

The target environment is either an event sourcing system, or microservices with
an event bus - anywhere you're consuming events and doing something with them.

Pre-requisites
==============

All events must be versioned. That is, there must be a version number in the event
structure somewhere.

There must be a way to map from a given event version to version+1 for every version number.
This is typically done by defining an upgrade method (ala Flyway for Databases).

The library will present an "ingest" method, which will take events in, extract the
version number, run all appropriate upgrade methods until the version is current, then
call an event factory with the upgraded data and return the appropriate object.

Design decisions (and whys)
===========================

* Factory is only called with the latest data, not for each version - this is to save
  from having to maintain factories for every version.

* Supporting Python 3.7 and above - because I want to.

* All events are dictionaries - for simplicity.

* Upgrade methods may mutate events in place - each event is provided as a deepcopy (so don't upgrade things that don't deepcopy).
  If you return, that will be used - if not, the assumed mutated event will be used.

* Upgrade methods will get dictionaries and return dictionaries, and wrapping will be invisible - because
  I want this to be as simple to use as possible.

How to Use
==========

Create a module that holds a bunch of version upgrade methods.

Each method should use the "pevl.event.upgrade" decorator, and in the decorator you specify a version number.

Each method should apply an appropriate upgrade from the verison number given to the next version number.

Each method should be named descriptively.

Each method takes an event :dict, and returns an event: dict

Version numbers need to sort properly.

Example:

```python
from pevl.event import upgrade

@upgrade('v0.1')
def split_first_last_name(event):
    event['first'], event['last'] = event['name'].split()
```

For an example of the code that does the upgrades, see `sample_sns.py`