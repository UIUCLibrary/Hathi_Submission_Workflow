import os
from pprint import pprint

import pytest

import hsw.collection_builder
from hsw import collection, collection_builder


@pytest.fixture(scope="session")
def ds_collection_root(tmpdir_factory):
    ds_collection_packages = [
        "1564651",
        "4564654",
        "7213538",
    ]
    ds_collection_package_files = [

        os.path.join("1564651", "00000001.jp2"),
        os.path.join("1564651", "00000001.txt"),
        os.path.join("1564651", "00000002.jp2"),
        os.path.join("1564651", "00000002.txt"),
        os.path.join("1564651", "00000003.jp2"),
        os.path.join("1564651", "00000003.txt"),
        os.path.join("1564651", "00000004.jp2"),
        os.path.join("1564651", "00000004.txt"),
        os.path.join("1564651", "00000005.jp2"),
        os.path.join("1564651", "00000005.txt"),
        os.path.join("1564651", "00000006.jp2"),
        os.path.join("1564651", "00000006.txt"),
        os.path.join("1564651", "00000007.jp2"),
        os.path.join("1564651", "00000007.txt"),
        os.path.join("1564651", "00000008.jp2"),
        os.path.join("1564651", "00000008.txt"),
        os.path.join("4564654", "00000001.jp2"),
        os.path.join("4564654", "00000001.txt"),
        os.path.join("4564654", "00000002.jp2"),
        os.path.join("4564654", "00000002.txt"),
        os.path.join("4564654", "00000003.jp2"),
        os.path.join("4564654", "00000003.txt"),
        os.path.join("4564654", "00000004.jp2"),
        os.path.join("4564654", "00000004.txt"),
        os.path.join("4564654", "00000005.jp2"),
        os.path.join("4564654", "00000005.txt"),
        os.path.join("4564654", "00000006.jp2"),
        os.path.join("4564654", "00000006.txt"),
        os.path.join("4564654", "00000007.jp2"),
        os.path.join("4564654", "00000007.txt"),
        os.path.join("4564654", "00000008.jp2"),
        os.path.join("4564654", "00000008.txt"),
        os.path.join("7213538", "00000001.jp2"),
        os.path.join("7213538", "00000001.txt"),
        os.path.join("7213538", "00000002.jp2"),
        os.path.join("7213538", "00000002.txt"),
        os.path.join("7213538", "00000003.jp2"),
        os.path.join("7213538", "00000003.txt"),
        os.path.join("7213538", "00000004.jp2"),
        os.path.join("7213538", "00000004.txt"),
        os.path.join("7213538", "00000005.jp2"),
        os.path.join("7213538", "00000005.txt"),
        os.path.join("7213538", "00000006.jp2"),
        os.path.join("7213538", "00000006.txt"),
        os.path.join("7213538", "00000007.jp2"),
        os.path.join("7213538", "00000007.txt"),
        os.path.join("7213538", "00000008.jp2"),
        os.path.join("7213538", "00000008.txt"),
        os.path.join("7213538", "00000009.jp2"),
        os.path.join("7213538", "00000009.txt"),
        os.path.join("7213538", "00000010.jp2"),
        os.path.join("7213538", "00000010.txt"),
        os.path.join("7213538", "00000011.jp2"),
        os.path.join("7213538", "00000011.txt"),
        os.path.join("7213538", "00000012.jp2"),
        os.path.join("7213538", "00000012.txt"),
        os.path.join("7213538", "00000013.jp2"),
        os.path.join("7213538", "00000013.txt"),
        os.path.join("7213538", "00000014.jp2"),
        os.path.join("7213538", "00000014.txt"),
        os.path.join("7213538", "00000015.jp2"),
        os.path.join("7213538", "00000015.txt"),
        os.path.join("7213538", "00000016.jp2"),
        os.path.join("7213538", "00000016.txt"),
        os.path.join("7213538", "00000017.jp2"),
        os.path.join("7213538", "00000017.txt"),
        os.path.join("7213538", "00000018.jp2"),
        os.path.join("7213538", "00000018.txt"),

    ]
    tests_files_dir = tmpdir_factory.mktemp("DS_Test")
    for package_name in ds_collection_packages:
        os.mkdir(os.path.join(tests_files_dir, package_name))
    for test_file in ds_collection_package_files:
        new_test_item = tests_files_dir.join(test_file)
        with open(new_test_item, "w") as f:
            pass
    return str(tests_files_dir)


@pytest.fixture(scope="session")
def bb_collection_root(tmpdir_factory):
    brittle_books_packages = [
        "1251150",
    ]
    brittle_books_package_files = [
        os.path.join("1251150", "00000001.jp2"),
        os.path.join("1251150", "00000001.txt"),
        os.path.join("1251150", "00000001.xml"),
        os.path.join("1251150", "00000002.jp2"),
        os.path.join("1251150", "00000002.txt"),
        os.path.join("1251150", "00000002.xml"),
        os.path.join("1251150", "00000003.jp2"),
        os.path.join("1251150", "00000003.txt"),
        os.path.join("1251150", "00000003.xml"),
        os.path.join("1251150", "00000004.jp2"),
        os.path.join("1251150", "00000004.txt"),
        os.path.join("1251150", "00000004.xml"),
        os.path.join("1251150", "00000005.jp2"),
        os.path.join("1251150", "00000005.txt"),
        os.path.join("1251150", "00000005.xml"),
        os.path.join("1251150", "00000006.jp2"),
        os.path.join("1251150", "00000006.txt"),
        os.path.join("1251150", "00000006.xml"),
        os.path.join("1251150", "00000007.jp2"),
        os.path.join("1251150", "00000007.txt"),
        os.path.join("1251150", "00000007.xml"),
        os.path.join("1251150", "00000008.jp2"),
        os.path.join("1251150", "00000008.txt"),
        os.path.join("1251150", "00000008.xml"),
        os.path.join("1251150", "00000009.jp2"),
        os.path.join("1251150", "00000009.txt"),
        os.path.join("1251150", "00000009.xml"),
        os.path.join("1251150", "00000010.jp2"),
        os.path.join("1251150", "00000010.txt"),
        os.path.join("1251150", "00000010.xml")
    ]
    tests_files_dir = tmpdir_factory.mktemp("BB_Test")
    for package_name in brittle_books_packages:
        os.mkdir(os.path.join(tests_files_dir, package_name))
    for test_file in brittle_books_package_files:
        new_test_item = tests_files_dir.join(test_file)
        with open(new_test_item, "w") as f:
            pass
    return str(tests_files_dir)


def test_build_bb_collection(bb_collection_root):
    my_collection = hsw.collection_builder.build_bb_collection(str(bb_collection_root))
    assert isinstance(my_collection, collection.Collection)


def test_collection_size(bb_collection_root):
    my_collection = hsw.collection_builder.build_bb_collection(str(bb_collection_root))
    assert len(my_collection) == 1


def test_collection_iter(bb_collection_root):
    my_collection = hsw.collection_builder.build_bb_collection(str(bb_collection_root))
    for i in my_collection:
        pass


def test_collection_index(bb_collection_root):
    my_collection = hsw.collection_builder.build_bb_collection(str(bb_collection_root))
    foo = my_collection[0]
    assert foo is not None


def test_package_size(bb_collection_root):
    my_collection = hsw.collection_builder.build_bb_collection(str(bb_collection_root))
    my_package_1251150 = my_collection[0]
    assert len(my_package_1251150) == 10


def test_item_size(bb_collection_root):
    my_collection = hsw.collection_builder.build_bb_collection(str(bb_collection_root))
    my_package_1251150 = my_collection[0]
    first_item = my_package_1251150[0]
    assert len(first_item) == 1


def test_item_metadata_name(bb_collection_root):
    my_collection = hsw.collection_builder.build_bb_collection(str(bb_collection_root))
    my_package_1251150 = my_collection[0]
    first_item = my_package_1251150[0]
    assert first_item.metadata["item_name"] == "00000001"


def test_item_instance(bb_collection_root):
    my_collection = hsw.collection_builder.build_bb_collection(str(bb_collection_root))
    my_package_1251150 = my_collection[0]
    first_item = my_package_1251150[0]
    access_instance = first_item.instantiations["access"]
    assert access_instance.metadata['category'] == "access"


def test_bb_collection_strat(bb_collection_root):
    strategy = collection_builder.BrittleBooksStrategy()
    package_builder = collection_builder.BuildPackage(strategy)
    my_collection = package_builder.build_package(bb_collection_root)
    assert isinstance(my_collection, collection.Collection)


def test_ds_collection_strategy(ds_collection_root):
    strategy = collection_builder.DSStrategy()
    package_builder = collection_builder.BuildPackage(strategy)
    my_collection = package_builder.build_package(ds_collection_root)
    assert isinstance(my_collection, collection.Collection)


def test_ds_collection_len(ds_collection_root):
    strategy = collection_builder.DSStrategy()
    package_builder = collection_builder.BuildPackage(strategy)
    my_collection = package_builder.build_package(ds_collection_root)
    assert len(my_collection) == 3


def test_ds_package_len(ds_collection_root):
    strategy = collection_builder.DSStrategy()
    package_builder = collection_builder.BuildPackage(strategy)
    my_collection = package_builder.build_package(ds_collection_root)
    my_package = my_collection[0]
    assert len(my_package) == 8


def test_ds_item_len(ds_collection_root):
    strategy = collection_builder.DSStrategy()
    package_builder = collection_builder.BuildPackage(strategy)
    my_collection = package_builder.build_package(ds_collection_root)
    my_package = my_collection[0]
    my_item = my_package[0]
    assert len(my_item) == 1


def test_ds_instantiations(ds_collection_root):
    strategy = collection_builder.DSStrategy()
    package_builder = collection_builder.BuildPackage(strategy)
    my_collection = package_builder.build_package(ds_collection_root)
    my_package = my_collection[0]
    my_item = my_package[0]
    my_instantiation = my_item.instantiations["access"]
    assert my_instantiation.metadata['category'] == "access"
    pprint(dict(my_instantiation.metadata))
    print(my_instantiation)
