import pytest
from hsw import packages as pkgs


@pytest.fixture()
def packages():
    return pkgs.Packages()
    pass


@pytest.fixture()
def sample_package():
    my_packages = pkgs.Packages()
    my_packages.add_package(path="c:/temp/foo")
    return my_packages["c:/temp/foo"]


@pytest.fixture()
def sample_package_with_items():
    my_packages = pkgs.Packages()
    my_packages.add_package(path="c:/temp/foo")
    my_package = my_packages["c:/temp/foo"]
    my_package._items.append("c:/temp/foo/spam0001.tif")
    return my_package


def test_package_empty_len(packages):
    assert len(packages) == 0


def test_add_package_entry(packages):
    packages.add_package(path="c:/temp/foo")
    assert len(packages) == 1


def test_set_and_retrieve_entry(packages):
    packages.add_package(path="c:/temp/foo")
    assert len(packages) == 1
    spam = packages["c:/temp/foo"]
    assert spam.path == "c:/temp/foo"
    assert len(spam) == 0


def test_alert_dup_added(packages):
    packages.add_package(path="c://temp/foo")
    with pytest.raises(FileExistsError):
        packages.add_package(path="c://temp/foo")


def test_package_size(sample_package):
    assert len(sample_package) == 0
