from collections import abc
from .package_builder import PackageBuilder

class PackagesList(abc.Sequence):
    def __init__(self, root=None):
        self._packages = []
        self.root = root

    def __len__(self):
        return len(self._packages)

    def __iter__(self):
        return self._packages.__iter__()

    def add_package(self, path):
        for package in self._packages:
            if package.path == path:
                raise FileExistsError("{} already in packages".format(path))
        else:
            new_package = self._build_package(path)
            self._packages.append(new_package)

    def __getitem__(self, index):
        return self._packages[index]

    @staticmethod
    def _build_package(path):
        builder = PackageBuilder(path)
        new_package = builder.build()
        # new_package = Package(path)
        # new_package.metadata["title_page"] = None
        return new_package