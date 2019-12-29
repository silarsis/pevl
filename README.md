# pevl
Python Event Versioning Library

This library covers the heavy lifting for event versioning in python.

The target environment is either an event sourcing system, or microservices with
an event bus - anywhere you're consuming events and doing something with them.

Pre-requisites:

All events must be versioned. That is, there must be a version number in the event
structure somewhere.

There must be a way to map from a given event version to version+1 for every version number.
This is typically done by defining an upgrade method (ala Flyway for Databases).

The library will present an "ingest" method, which will take events in, extract the
version number, run all appropriate upgrade methods until the version is current, then
call an event factory with the upgraded data and return the appropriate object.

Design decisions (and whys):

* Factory is only called with the latest data, not for each version - this is to save
from having to maintain factories for every version.

* Supporting Python 3.8 and above - because I want to.

* 