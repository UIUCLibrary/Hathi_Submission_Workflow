import pytest
import os
from hsw.package_list import PackagesList

PACKAGE_DIRECTORIES = [
    "SPAM_00000001",
    "SPAM_00000002",
    "SPAM_00000003",
]


@pytest.fixture(scope="session")
def packages_empty(tmpdir_factory):
    new_package = tmpdir_factory.mktemp("dummyPackages", numbered=False)
    for path in PACKAGE_DIRECTORIES:
        os.makedirs(os.path.join(new_package, path))
    root_path = str(new_package)
    my_packages = PackagesList(root_path)
    return my_packages


def test_root(tmpdir):
    new_package = tmpdir.mkdir("dummyPackages")
    for path in PACKAGE_DIRECTORIES:
        os.makedirs(os.path.join(new_package, path))
    root_path = str(new_package)
    my_packages = PackagesList(root_path)
    assert isinstance(my_packages, PackagesList)
    assert isinstance(my_packages.root, str)
    assert my_packages.root.endswith("dummyPackages") is True


def test_empty_size(packages_empty):
    assert len(packages_empty) == 0


def test_add_packages(packages_empty: PackagesList):
    for package_name in PACKAGE_DIRECTORIES:
        package_path = os.path.join(packages_empty.root, package_name)
        packages_empty.add_package(package_path)

    assert len(packages_empty) == 3


def test_alert_dup_added(packages_empty, monkeypatch):
    def mockreturn(path):
        return []

    monkeypatch.setattr(os, "scandir", mockreturn)
    packages_empty.add_package(path=os.path.join("temp", "foo"))
    with pytest.raises(FileExistsError):
        packages_empty.add_package(path=os.path.join("temp", "foo"))
