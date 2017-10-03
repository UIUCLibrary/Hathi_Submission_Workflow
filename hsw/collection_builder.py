import abc
import logging
import os
import typing
import warnings

from hsw.collection import Instantiation, Item, Package, PackageObject
from . import collection

def _build_ds_instance(item, name, path):
    new_instantiation = Instantiation(category="access", parent=item)
    for file in filter(lambda i: i.is_file(), os.scandir(path)):
        if os.path.splitext(os.path.basename(file))[0] == name:
            new_instantiation.files.append(file.path)


def _build_ds_items(package, path):
    logger = logging.getLogger(__name__)
    files = sorted(set(map(lambda item: os.path.splitext(item)[0], os.listdir(path))))
    for unique_item in files:
        logger.debug(unique_item)
        new_item = Item(parent=package)
        new_item.component_metadata["item_name"] = unique_item
        _build_ds_instance(new_item, name=unique_item, path=path)


def _build_ds_object(parent_collection, path):
    for folder in filter(lambda i: i.is_dir(), os.scandir(path)):
        new_package = PackageObject(parent=parent_collection)
        new_package.component_metadata["path"] = folder.path
        new_package.component_metadata["id"] = folder.name
        new_package.component_metadata["title_page"] = None
        _build_ds_items(new_package, path=folder.path)


def build_ds_collection(root):
    new_collection = Package(root)
    new_collection.component_metadata["path"] = root
    new_collection.component_metadata["package_type"] = "DS HathiTrust Submission Package"
    _build_ds_object(parent_collection=new_collection, path=root)
    return new_collection



def build_bb_instance(new_item, path, name):
    new_instantiation = Instantiation(category="access", parent=new_item)
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


def build_bb_collection(root) -> Package:
    logger = logging.getLogger(__name__)
    new_collection = Package(root)
    for directory in filter(lambda i: i.is_dir(), os.scandir(root)):
        logger.debug("scanning {}".format(directory.path))
        new_object = PackageObject(parent=new_collection)
        new_object.component_metadata['path'] = directory.path
        new_object.component_metadata["id"] = directory.name
        new_object.component_metadata["package_type"] = "Brittle Books HathiTrust Submission Package"
        build_bb_package(new_object, path=directory.path)
    return new_collection
