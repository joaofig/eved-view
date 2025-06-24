from typing import Any, Dict

from nicemvvm.singleton import singleton


@singleton
class ResourceLocator:
    def __init__(self):
        self._resources: Dict[str:Any] = dict()

    def __getitem__(self, key):
        return self._resources[key]

    def __setitem__(self, key, value):
        self._resources[key] = value
