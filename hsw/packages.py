from collections import abc


# TODO: make into an abc.Set with metadata because MutableMapping doesn't really makes sense for this .
# https://docs.python.org/3.6/library/collections.abc.html#collections-abstract-base-classes
class Package(abc.MutableMapping):
    def __init__(self, path):
        self._data = dict()
        self.path = path

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        # TODO: Make package size the number of items, not the amount of metadata it has
        return self._data.__iter__()

    def __delitem__(self, key):
        del self._data[key]

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value


class Packages(abc.Mapping):
    def __init__(self):
        self._data = dict()

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
        new_package["pages"] = []
        new_package["title_page"] = None
        return new_package
