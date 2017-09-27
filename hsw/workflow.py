import abc
from . import collection
from . import collection_builder
from pyhathiprep import package_creater
from hathi_validate import process as validate_process
from hathizip import process as zip_process

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
        for package_object in package:
            package_builder = package_creater.InplacePackage(package_object.metadata['path'])
            package_builder.generate_package()
            # package_creater.create_package(source=package_object.metadata['path'])

    def validate(self, package):
        print("Validating")
        errors = []
        for package_object in package:
            errors += validate_process.process_directory(package_object.metadata['path'])
        return errors

    def zip(self, package, destination):
        print("zipping")
        for package_object in package:
            print(package_object)
            zip_process.compress_folder(package_object.metadata['path'], destination)