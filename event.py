import copy
from typing import Callable, Iterable


class Event:
    " Wrapper class for events "
    def __init__(self, event: dict):
        self.event = event

    @property
    def version(self):
        return event.get('version')


def upgrade(version=None):
    " Decorator to declare that a method is an upgrade method "
    def upgrade_decorator(func):
        @wraps(func)
        def wrapped_function(event: Event):
            if event.version == version:
                newCopy = copy.deepcopy(event.event)
                ret = func(newCopy)
                return ret and Event(ret) or Event(newCopy) # Allow return or mutate
            return event


class Upgrader:
    def __init__(self, upgrades: Iterable = None, factory: Callable = None):
        " upgrades is an iterable collection of version upgrade methods "
        self.upgrades = upgrades or []
        self.factory = factory

    def upgrade(self, event: Event):
        " Apply all the upgrades to the event "
        for u in self.upgrades:
            event = u(event)
        return event

    def ingest(self, event: dict):
        " This is if you want to build an upgrader class then call it repeatedly for events "
        upgraded = self.upgrade(Event(event))
        return (self.factory and self.factory(upgraded) or upgraded)


def ingest(upgrades: Iterable, event: dict, factory: Callable = None):
    " In case you want to call the ingester without setting up an upgrader object "
    u = Upgrader(upgrades)
    upgraded = u.upgrade(Event(event))
    return (factory and factory(upgraded) or upgraded)
