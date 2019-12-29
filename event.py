import copy
import inspect
from typing import Callable, Iterable, Any
from functools import wraps


VersionMethod = Callable[[dict], str]
FactoryMethod = Callable[[dict], Any]


class Event:
    " Wrapper class for events "
    def __init__(self, event: dict, get_version: VersionMethod = None):
        " get_version should be a function, not a method - there's no self provided in the call "
        self.event = event
        if get_version:
            self.get_version = get_version
        else:
            self.get_version = lambda x: str(x.get('version'))

    @property
    def version(self) -> str:
        return getattr(self, 'get_version')(self.event)  # Phrased strangely because 'self.get_version()' will introduce a self


def upgrade(version: str = ''):
    " Decorator to declare that a method is an upgrade method "
    def upgrade_decorator(func: Callable[[dict], dict]):
        @wraps(func)
        def wrapped_function(event: Event) -> Event:
            if event.version == version:
                newCopy = copy.deepcopy(event.event)
                ret = func(newCopy)
                return Event(ret and ret or newCopy, get_version=event.get_version)  # Allow return or mutate
            return event
        return wrapped_function
    return upgrade_decorator

class Upgrader:
    def __init__(self, upgrades: Iterable = None, get_version: VersionMethod = None, factory: FactoryMethod = None):
        " upgrades is an iterable collection of version upgrade methods "
        self.upgrades = upgrades or []
        self.get_version = get_version
        self.factory = factory

    def upgrade(self, event: Event):
        " Apply all the upgrades to the event "
        for u in self.upgrades:
            event = u(event)
        return event

    def ingest(self, event: dict):
        " This is if you want to build an upgrader class then call it repeatedly for events "
        upgraded = self.upgrade(Event(event, get_version=self.get_version))
        return (self.factory and self.factory(upgraded) or upgraded)


def ingest(upgrades: Iterable, event: dict, factory: FactoryMethod = None):
    " In case you want to call the ingester without setting up an upgrader object "
    u = Upgrader(upgrades)
    upgraded = u.upgrade(Event(event))
    return (factory and factory(upgraded) or upgraded)


class Upgraders:  # Not yet done
    " Every method in here will be used as an upgrade method. Just be sure to decorate. "
    def upgraders(self):
        return [ method for name, method in inspect.getmembers(self, predicate=inspect.ismethod) if name != 'upgraders' ]