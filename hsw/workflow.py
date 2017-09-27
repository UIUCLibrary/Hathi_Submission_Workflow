import abc
from . import collection
from . import collection_builder


class AbsStrategy(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def build_collection(self, root) -> collection.Package:
        pass


class BrittleBooksStrategy(AbsStrategy):
    def build_collection(self, root) -> collection.Package:
        return collection_builder.build_bb_collection(root)


class DSStrategy(AbsStrategy):
    def build_collection(self, root) -> collection.Package:
        return collection_builder.build_ds_collection(root)

class Workflow:
    def __init__(self, strategy: AbsStrategy) -> None:
        self._strategy = strategy

    def build_package(self, root):
        return self._strategy.build_collection(root)

    def prep(self, package):
        print("prepping")
