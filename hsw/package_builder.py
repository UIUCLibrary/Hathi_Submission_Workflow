import abc

import os

from .packages import Package


class AbsPackageBuilder(metaclass=abc.ABCMeta):
    def __init__(self, path=None):
        self._package = None
        self.path = path

    @abc.abstractmethod
    def add_items(self, package: Package):
        pass

    @staticmethod
    @abc.abstractmethod
    def set_default_metadata(package: Package):
        pass

    @abc.abstractmethod
    def build(self) -> Package:
        pass


class PackageBuilder(AbsPackageBuilder):
    @staticmethod
    def set_default_metadata(package: Package):
        package.metadata = {"title_page": None}

    def add_items(self, package: Package):
        if self.path:
            for file in os.scandir(self.path):
                package._items.append(file.path)

    def build(self) -> Package:
        new_package = Package(self.path)
        self.add_items(new_package)
        PackageBuilder.set_default_metadata(new_package)
        return new_package
