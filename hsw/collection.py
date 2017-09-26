import abc
import collections
import logging
import typing

import os


class AbsPackageComponent(metaclass=abc.ABCMeta):
    def __init__(self, parent=None) -> None:
        self.parent = parent
        if parent is not None:
            self.add_to_parent(child=self)

        self.component_metadata = self.init_local_metadata()
        metadata = self._gen_combined_metadata()
        self.metadata: typing.ChainMap[str, str] = metadata

    def add_to_parent(self, child):
        self.parent.children.append(child)

    def __len__(self):
        return len(self.children)

    def __getitem__(self, item) -> typing.Type["AbsPackageComponent"]:
        return self.children[item]

    def __iter__(self):
        yield self.children

    @property
    @abc.abstractmethod
    def children(self) -> typing.List[typing.Type["AbsPackageComponent"]]:
        pass

    def _gen_combined_metadata(self) -> typing.ChainMap[str, str]:
        if self.parent:
            metadata = collections.ChainMap(self.component_metadata, self.parent.metadata)
        else:
            metadata = collections.ChainMap(self.component_metadata)
        return metadata

    @staticmethod
    def init_local_metadata() -> dict:
        return dict()


class Collection(AbsPackageComponent):
    def __init__(self, path=None, parent=None):
        self.path = path
        self.packages: typing.List[Package] = []
        super().__init__(parent)

    @property
    def children(self):
        return self.packages


class Package(AbsPackageComponent):
    def __init__(self, parent: typing.Optional[Collection] = None) -> None:
        super().__init__(parent)
        self.package_files: typing.List[str] = []
        self.items: typing.List[Item] = []

    @property
    def children(self):
        return self.items


class Item(AbsPackageComponent):
    def __init__(self, parent: typing.Optional[Package] = None) -> None:
        super().__init__(parent)
        self.instantiations = dict()  # type: typing.Dict[str, Instantiation]

    @property
    def children(self):
        return self.instantiations.values()


class Instantiation(AbsPackageComponent):
    def __init__(self, category="generic", parent: typing.Optional[Item] = None) -> None:
        self.category = category
        super().__init__(parent)
        self.component_metadata['category'] = category
        self.files: typing.List[str] = []

    @property
    def children(self):
        return []

    def add_to_parent(self, child):
        self.parent.instantiations[self.category] = child


def build_bb_instance(new_item, path, name):
    new_instantiation = Instantiation(category="access",parent=new_item)
    for file in filter(lambda i: i.is_file(), os.scandir(path)):
        if os.path.splitext(os.path.basename(file))[0] == name:
            new_instantiation.files.append(file.path)


def build_bb_package(new_package, path):
    logger = logging.getLogger(__name__)
    files = set(map(lambda item: os.path.splitext(item)[0], os.listdir(path)))
    for unique_item in sorted(files):
        logger.debug(unique_item)
        new_item = Item(parent=new_package)
        new_item.component_metadata["item_name"] = unique_item
        build_bb_instance(new_item, name=unique_item, path=path)


def build_bb_collection(root) -> Collection:
    logger = logging.getLogger(__name__)
    new_collection = Collection(root)
    for directory in filter(lambda i: i.is_dir(), os.scandir(root)):
        logger.debug("scanning {}".format(directory.path))
        new_package = Package(parent=new_collection)
        new_package.component_metadata['path'] = directory.path
        new_package.component_metadata["package_type"] = "Brittle Books HathiTrust Submission Package"
        build_bb_package(new_package, path=directory.path)
    return new_collection
