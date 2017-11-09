import abc

import os

import sys

from . import collection
from . import collection_builder
from pyhathiprep import package_creater, checksum
from hathi_validate import process as validate_process
from hathizip import process as zip_process
import imgvalidator
import imgvalidator.validate
import imgvalidator.report
from imgvalidator import cli
import typing


class AbsWorkflow(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def build_collection(self, root) -> collection.Package:
        pass

    @staticmethod
    def prep(package) -> typing.List[typing.Callable]:
        return [lambda *args: None]

    @staticmethod
    def update_checksums(package) -> typing.List[typing.Callable]:
        return [lambda *args: None]

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

    @staticmethod
    def qc(package) -> typing.List[typing.Callable]:
        return [lambda *args: None]


class BrittleBooksWorkflow(AbsWorkflow):
    def build_collection(self, root) -> collection.Package:
        return collection_builder.build_bb_collection(root)

    @staticmethod
    def validate(package) -> typing.List[typing.Callable]:
        closures = []
        for package_object in package:
            def create_task(path):
                return validate_process.process_directory(path, require_page_data=False)

            closures.append(lambda path=package_object.metadata['path']: create_task(path))
        return closures

    @staticmethod
    def update_checksums(package) -> typing.List[typing.Callable]:
        closures = []
        for package_object in package:
            package_object_path = package_object.metadata["path"]

            def create_task(path):
                checksum_file = os.path.join(path, "checksum.md5")
                if os.path.exists(checksum_file):
                    os.remove(checksum_file)
                checksum_report_data = checksum.create_checksum_report(path)
                with open(checksum_file, "w") as f:
                    f.write(checksum_report_data)
            closures.append(lambda path=package_object_path: create_task(path))

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
                # print(title_page)
                package_builder.generate_package(destination=path, title_page=title_page)

            closures.append(lambda path=package_object.metadata['path'],
                                   title_page=package_object.metadata["title_page"]: package_generator(path,
                                                                                                       title_page))
        return closures

    @staticmethod
    def qc(package) -> typing.List[typing.Callable]:
        closures = []
        profile_builder = imgvalidator.validation_profile.ProfileBuilder(imgvalidator.get_profile_builder("DSPreservationTiff"))
        profile = profile_builder.build_profile()
        # fixme: select the correct file dynamically
        image_format = [".tif"]

        for package_object in package:
            for item in package_object:
                for inst in item:
                    for file_path in inst.files:
                        if os.path.splitext(file_path)[1].lower() in image_format:
                            def qc_package(path, validation_profile):
                                result = imgvalidator.report.ValidationData(path)
                                try:
                                    errors = list(imgvalidator.validate.validate_file(path, validation_profile))
                                    result.errors = errors
                                    if errors:
                                        result.valid = False
                                    else:
                                        result.valid = True
                                except AssertionError as e:
                                    failure_message = "Validation of {} failed. Reason: {}".format(path, e)
                                    print(failure_message, file=sys.stderr)
                                except Exception as e:
                                    print(e)
                                    raise
                                return [result]
                                # return cli.validate_files()
                                # print("QCing")
                                # print(path)
                                # print(validation_profile)

                            closures.append(lambda path=file_path, validation_profile=profile:
                                            qc_package(path, validation_profile))
        return closures
        # print(package_object)
        # print(type(package_object))


        # try:
        #     return AbsWorkflow.qc(package)
        # except Exception as e:
        #     print(e)
        #     raise
        # rv = super().qc(package)
        # print("QC")
        # return rv


class Workflow:
    def __init__(self, workflow: AbsWorkflow) -> None:
        self._template = workflow

    def build_package(self, root) -> collection.Package:
        return self._template.build_collection(root)

    def prep(self, package) -> typing.List[typing.Callable]:
        return self._template.prep(package)

    def validate(self, package) -> typing.List[typing.Callable]:
        return self._template.validate(package)

    def zip(self, package, destination) -> typing.List[typing.Callable]:
        return self._template.zip(package, destination)

    def update_checksums(self, package) -> typing.List[typing.Callable]:
        return self._template.update_checksums(package)

    def qc(self, package) -> typing.List[typing.Callable]:
        return self._template.qc(package)