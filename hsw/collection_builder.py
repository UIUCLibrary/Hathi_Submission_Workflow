import abc
import typing

from . import collection


class AbsStrategy(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def build_package(self, strategy) -> collection.Collection:
        pass


class BrittleBooksStrategy(AbsStrategy):
    def build_package(self, root) -> collection.Collection:
        return collection.build_bb_collection(root)


class DSStrategy(AbsStrategy):
    def build_package(self, strategy) -> collection.Collection:
        raise NotImplementedError()


class BuildPackage:
    def __init__(self, strategy: AbsStrategy) -> None:
        self._strategy = strategy

    def build_package(self, root):
        return self._strategy.build_package(root)
