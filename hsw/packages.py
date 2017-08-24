import warnings
from collections import abc


class Package(abc.Collection):
    def __init__(self, path):
        self.metadata = dict()
        self._items = []
        self.path = path

    def __len__(self):
        return len(self._items)

    def __contains__(self, x):
        for name in self._items:
            if name == x:
                return True
        else:
            return False

    def __iter__(self):
        return self._items.__iter__()


class Packages(abc.Mapping):
    def __init__(self, root=None):
        warnings.warn("Use PackageList instead", DeprecationWarning)
        self._data = dict()
        self.root = root

    def __len__(self):
        return len(self._data)

    def __getitem__(self, key):
        return self._data[key]

    def __iter__(self):
        return self._data.__iter__()

    def add_package(self, path):
        if path in self._data:
            raise FileExistsError("{} already in packages".format(path))
        self._data[path] = self._build_package(path)

    @staticmethod
    def _build_package(path):
        new_package = Package(path)
        new_package.metadata["title_page"] = None
        return new_package
