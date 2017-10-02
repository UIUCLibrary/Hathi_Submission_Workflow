import abc
from . import collection
from . import collection_builder
from pyhathiprep import package_creater
from hathi_validate import process as validate_process
from hathizip import process as zip_process
import typing


class AbsWorkflow(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def build_collection(self, root) -> collection.Package:
        pass

    @staticmethod
    def prep(package) -> typing.List[typing.Callable]:
        pass

    @staticmethod
    def validate(package) -> typing.List[typing.Callable]:
        # errors = []
        closures = []
        for package_object in package:
            def create_task(path):
                return validate_process.process_directory(path)

            closures.append(lambda p=package_object.metadata['path']: create_task(p))
        return closures

    @staticmethod
    def zip(package, destination):
        closures = []
        for package_object in package:
            def zip_creater(path, output):
                return zip_process.compress_folder(path, output)

            closures.append(lambda p=package_object.metadata['path'], o=destination: zip_creater(p, o))
        return closures


class BrittleBooksWorkflow(AbsWorkflow):
    def build_collection(self, root) -> collection.Package:
        return collection_builder.build_bb_collection(root)

    @staticmethod
    def validate(package) -> typing.List[typing.Callable]:
        # errors = []
        closures = []
        for package_object in package:
            def create_task(path):
                return validate_process.process_directory(path, require_page_data=False)

            closures.append(lambda path=package_object.metadata['path']: create_task(path))
        return closures


class DSWorkflow(AbsWorkflow):
    def build_collection(self, root) -> collection.Package:
        return collection_builder.build_ds_collection(root)

    @staticmethod
    def prep(package) -> typing.List[typing.Callable]:
        closures = []
        for package_object in package:
            def package_generator(path, title_page):
                package_builder = package_creater.InplacePackage(path)
                # title_page = package_object.metadata["title_page"]
                print(title_page)
                package_builder.generate_package(destination=path, title_page=title_page)

            closures.append(lambda path=package_object.metadata['path'],
                                   title_page=package_object.metadata["title_page"]: package_generator(path,
                                                                                                       title_page))
        return closures


class Workflow:
    def __init__(self, workflow: AbsWorkflow) -> None:
        self._template = workflow

    def build_package(self, root):
        return self._template.build_collection(root)

    def prep(self, package) -> typing.List[typing.Callable]:
        return self._template.prep(package)

    def validate(self, package) -> typing.List[typing.Callable]:
        return self._template.validate(package)

    def zip(self, package, destination) -> typing.List[typing.Callable]:
        return self._template.zip(package, destination)
