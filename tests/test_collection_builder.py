import os
from pprint import pprint

import pytest
from hsw import collection


@pytest.fixture(scope="session")
def bb_collection(tmpdir_factory):
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
    return collection.build_bb_collection(str(tests_files_dir))


def test_build_bb_collection(bb_collection):
    assert isinstance(bb_collection, collection.Collection)


def test_collection_size(bb_collection):
    assert len(bb_collection) == 1


def test_collection_iter(bb_collection):
    for i in bb_collection:
        pass


def test_collection_index(bb_collection):
    foo = bb_collection[0]
    assert foo.metadata


def test_package_size(bb_collection):
    my_package_1251150 = bb_collection[0]
    assert len(my_package_1251150) == 10


def test_item_size(bb_collection):
    my_package_1251150 = bb_collection[0]
    first_item = my_package_1251150[0]
    assert len(first_item) == 1


def test_item_metadata_name(bb_collection):
    my_package_1251150 = bb_collection[0]
    first_item = my_package_1251150[0]
    assert first_item.metadata["item_name"] == "00000001"


def test_item_instance(bb_collection):
    my_package_1251150 = bb_collection[0]
    first_item = my_package_1251150[0]
    access_instance = first_item.instantiations["access"]
    pprint(dict(access_instance.metadata))
    assert access_instance.metadata['category'] == "access"
