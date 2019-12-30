import copy
import inspect
from typing import Callable, Iterable, Any, List
from functools import wraps


VersionMethod = Callable[[dict], str]
VersionSetMethod = Callable[[dict, str], None]
FactoryMethod = Callable[[dict], Any]


class Event:
    " Wrapper class for events "
    def __init__(self, event: dict, get_version: VersionMethod = None, set_version: VersionSetMethod = None):
        " get_version should be a function, not a method - there's no self provided in the call "
        self.event = event
        self.get_version: VersionMethod = get_version or (lambda x: str(x.get('version')))
        self.set_version: VersionSetMethod = set_version or (lambda x, y: x.update({'version': y}))

    @property
    def version(self) -> str:
        return getattr(self, 'get_version')(self.event)  # Phrased strangely because 'self.get_version()' will introduce a self

    @version.setter
    def version(self, value: str) -> None:
        return getattr(self, 'set_version')(self.event, value)  # Phrased strangely because 'self.set_version()' will introduce a self


def upgrade(version: str = '', new_version: str = ''):
    """
    Decorator to declare that a method is an upgrade method

    Takes version to be applied to, and optionally new version to set.
    """
    def upgrade_decorator(func: Callable[[dict], dict]):
        @wraps(func)
        def wrapped_function(event: Event) -> Event:
            if event.version == version:
                newCopy = copy.deepcopy(event.event)
                ret = func(newCopy)
                newEvent = Event(ret and ret or newCopy, get_version=event.get_version, set_version=event.set_version)  # Allow return or mutate
                if new_version:
                    newEvent.version = new_version
                return newEvent
            return event
        return wrapped_function
    return upgrade_decorator

class Upgrader:
    def __init__(self, upgrades: Iterable = None, get_version: VersionMethod = None, factory: FactoryMethod = None):
        " upgrades is an iterable collection of version upgrade methods "
        self.upgrades = upgrades or []
        self.get_version = get_version
        self.factory = factory

    def upgrade(self, event: Event) -> Event:
        " Apply all the upgrades to the event "
        for u in self.upgrades:  # TODO: Make this a repeated dict query on version
            event = u(event)
        return event

    def ingest(self, event: dict):  # Returns Any because factory can return anything
        " This is if you want to build an upgrader class then call it repeatedly for events "
        upgraded = self.upgrade(Event(event, get_version=self.get_version))
        return (self.factory and self.factory(upgraded.event) or upgraded.event)


def ingest(upgrades: Iterable, event: dict, factory: FactoryMethod = None):  # Returns Any because factory can return anything
    " In case you want to call the ingester without setting up an upgrader object "
    u = Upgrader(upgrades)
    upgraded = u.upgrade(Event(event))
    return (factory and factory(upgraded.event) or upgraded.event)


class Upgraders:  # Not yet done
    " Every method in here will be used as an upgrade method. Just be sure to decorate. "
    def upgraders(self) -> List[VersionMethod]:
        return [ method for name, method in inspect.getmembers(self, predicate=inspect.ismethod) if name != 'upgraders' ]