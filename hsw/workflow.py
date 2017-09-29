import abc
from . import collection
from . import collection_builder
from pyhathiprep import package_creater
from hathi_validate import process as validate_process
from hathizip import process as zip_process


class AbsWorkflow(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def build_collection(self, root) -> collection.Package:
        pass

    @staticmethod
    def prep(package):
        for package_object in package:
            package_builder = package_creater.InplacePackage(package_object.metadata['path'])
            package_builder.generate_package()

    @staticmethod
    def validate(package):
        errors = []
        for package_object in package:
            errors += validate_process.process_directory(package_object.metadata['path'])
        return errors

    @staticmethod
    def zip(package, destination):
        for package_object in package:
            zip_process.compress_folder(package_object.metadata['path'], destination)


class BrittleBooksWorkflow(AbsWorkflow):
    def build_collection(self, root) -> collection.Package:
        return collection_builder.build_bb_collection(root)

    @staticmethod
    def validate(package):
        errors = []
        for package_object in package:
            errors += validate_process.process_directory(package_object.metadata['path'],require_page_data=False)
        return errors


class DSWorkflow(AbsWorkflow):
    def build_collection(self, root) -> collection.Package:
        return collection_builder.build_ds_collection(root)


class Workflow:
    def __init__(self, workflow: AbsWorkflow) -> None:
        self._template = workflow

    def build_package(self, root):
        return self._template.build_collection(root)

    def prep(self, package):
        return self._template.prep(package)

    def validate(self, package):
        return self._template.validate(package)

    def zip(self, package, destination):
        return self._template.zip(package, destination)
