import copy
import inspect
from typing import Callable, Iterable, Any, List
from functools import wraps, reduce


VersionMethod = Callable[[dict], str]
VersionSetMethod = Callable[[dict, str], None]
FactoryMethod = Callable[[dict], Any]
UpgradeMethod = Callable[[dict], dict]


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
    def upgrade_decorator(func: UpgradeMethod):
        @wraps(func)
        def wrapped_function(event: Event) -> Event:
            if event.version == version:
                newCopy = copy.deepcopy(event.event)
                ret = func(newCopy)
                newEvent = Event(ret and ret or newCopy, get_version=event.get_version, set_version=event.set_version)  # Allow return or mutate
                if new_version:
                    newEvent.version = new_version
                if newEvent.version == version:
                    raise KeyError('Upgrade did not change version number - {}'.format(version))
                return newEvent
            return event
        return wrapped_function
    return upgrade_decorator

class Upgrader:
    def __init__(self, upgrades: Iterable[Callable[[Event], Event]] = [], get_version: VersionMethod = None, set_version: VersionSetMethod = None, factory: FactoryMethod = None):
        " upgrades is a dict of version upgrade methods keyed on version "
        self.upgrades = dict({(inspect.getclosurevars(u).nonlocals['version'], u) for u in upgrades})
        self.get_version = get_version
        self.set_version = set_version
        self.factory = factory

    def upgrade(self, event: dict, target_version: str = None) -> dict:
        " Apply all the upgrades to the event, to an optional target version "
        wrappedEvent = Event(event, get_version=self.get_version, set_version=self.set_version)
        while True:
            if target_version and (wrappedEvent.version == target_version):
                break
            u = self.upgrades.get(wrappedEvent.version, None)
            if u is None:
                break  # This should mean we've reached the end, may mean we have an aberrant version
            wrappedEvent = u(wrappedEvent)
        if (target_version is not None) and (target_version != wrappedEvent.version):
            raise KeyError("All upgrades done, target version {} doesn't match event version {}".format(target_version, wrappedEvent.version))
        return wrappedEvent.event

    def ingest(self, event: dict, target_version: str = None):  # Returns Any because factory can return anything
        " This is if you want to build an upgrader class then call it repeatedly for events "
        upgraded = self.upgrade(event, target_version=target_version)
        return (self.factory and self.factory(upgraded) or upgraded)


class Upgraders:  # Not yet done
    " Every method in here will be used as an upgrade method. Just be sure to decorate. "
    def upgraders(self) -> List[VersionMethod]:
        return [ method for name, method in inspect.getmembers(self, predicate=inspect.ismethod) if name != 'upgraders' ]
