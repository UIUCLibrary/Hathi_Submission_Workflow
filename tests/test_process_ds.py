import os
import pytest
from hsw import workflow

@pytest.fixture(scope="session")
def ds_collection(tmpdir_factory):
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
    strategy = workflow.DSStrategy()
    package_builder = workflow.Workflow(strategy)
    return package_builder.build_package(tests_files_dir)
    # return str(tests_files_dir)

def test_prep(ds_collection):

    processor = workflow.Workflow(workflow.DSStrategy())
    processor.prep(ds_collection)


    print(ds_collection)