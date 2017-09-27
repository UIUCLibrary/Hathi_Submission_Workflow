import pytest
import os
from hsw import collection_builder


@pytest.fixture(scope="session")
def bb_collection(tmpdir_factory):
    brittle_books_packages = [
        "1251150",
        "1790923"
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
        os.path.join("1251150", "00000010.xml"),
        os.path.join("1790923", "00000001.jp2"),
        os.path.join("1790923", "00000001.txt"),
        os.path.join("1790923", "00000001.xml"),
        os.path.join("1790923", "00000002.jp2"),
        os.path.join("1790923", "00000002.txt"),
        os.path.join("1790923", "00000002.xml"),
        os.path.join("1790923", "00000003.jp2"),
        os.path.join("1790923", "00000003.txt"),
        os.path.join("1790923", "00000003.xml"),
        os.path.join("1790923", "00000004.jp2"),
        os.path.join("1790923", "00000004.txt"),
        os.path.join("1790923", "00000004.xml"),
    ]
    tests_files_dir = tmpdir_factory.mktemp("BB_Test")
    for package_name in brittle_books_packages:
        os.mkdir(os.path.join(tests_files_dir, package_name))
    for test_file in brittle_books_package_files:
        new_test_item = tests_files_dir.join(test_file)
        with open(new_test_item, "w") as f:
            pass
    return collection_builder.build_bb_collection(tests_files_dir)


def test_prep(bb_collection):
    print(bb_collection)
