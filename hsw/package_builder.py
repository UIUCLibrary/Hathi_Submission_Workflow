import abc

import os

from hsw.packages import Package


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
        package.metadata = {
            "package_name": None,
            "title_page": None
        }

    def add_items(self, package: Package):
        if self.path:
            for file in os.scandir(self.path):
                package._items.append(file.path)

    def build(self) -> Package:
        new_package = Package(self.path)
        PackageBuilder.set_default_metadata(new_package)
        if self.path:
            package_name = self.get_package_name(self.path)
            new_package.metadata["package_name"] = package_name
        self.add_items(new_package)
        return new_package

    @staticmethod
    def get_package_name(path):
        return os.path.split(path)[-1]
