import os
import pytest
from hsw import package_builder

files = [
    "00000001.jp2", "00000001.txt",
    "00000002.jp2", "00000002.txt",
    "00000003.jp2", "00000003.txt",
    "marc.xml"
]


@pytest.fixture(scope="session")
def SamplePackage(tmpdir_factory):
    new_package = tmpdir_factory.mktemp("dummyPackage")
    for file in files:
        new_file = new_package.join(file)
        with open(new_file, "w"):
            pass
    return str(new_package)


def test_path(SamplePackage):
    new_package = package_builder.PackageBuilder(SamplePackage)
    dummy = new_package.build()
    assert dummy.path == SamplePackage


def test_files(SamplePackage):
    new_package = package_builder.PackageBuilder(SamplePackage)
    dummy = new_package.build()
    for package_file in dummy:
        assert os.path.basename(package_file) in files
    assert len(dummy) == 7

def test_no_path(SamplePackage):
    new_package = package_builder.PackageBuilder()
    dummy = new_package.build()
    assert len(dummy) == 0
    pass
