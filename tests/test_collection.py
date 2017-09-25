from hsw import collection


def test_collection_instance():
    root = collection.Collection()
    assert isinstance(root, collection.Collection)


def test_collection_metadata():
    root = collection.Collection()
    root.component_metadata['spam'] = "eggs"
    assert root.metadata['spam'] == 'eggs'
    assert root.path is None
    assert root.packages == []


def test_collection_with_path():
    root = collection.Collection(path="/usr/spam")
    assert root.path == "/usr/spam"
    assert root.packages == []


def test_package_instance():
    package = collection.Package()
    assert isinstance(package, collection.Package)
    assert len(package.package_files) == 0
    assert len(package.items) == 0


def test_collection_with_package():
    root = collection.Collection(path="/usr/spam")

    package = collection.Package(parent=root)
    assert isinstance(package, collection.Package)

    assert len(root.packages) == 1
    # noinspection PyUnusedLocal
    package2 = collection.Package(parent=root)
    assert len(root.packages) == 2


def test_collection_with_package_transitive_metadata():
    root = collection.Collection(path="/usr/spam")
    root.component_metadata['spam'] = "eggs"
    package = collection.Package(parent=root)
    package.metadata["eggs"] = "bacon"
    assert package.metadata['spam'] == "eggs"
    assert package.metadata['eggs'] == "bacon"
    assert "eggs" not in root.metadata.keys()


def test_item_instance():
    item = collection.Item()
    assert isinstance(item, collection.Item)
    assert len(item.instantiations) == 0


def test_item_transitive_metadata():
    root = collection.Collection()
    root.component_metadata['spam'] = "eggs"

    package = collection.Package(parent=root)
    package.metadata["eggs"] = "bacon"

    item = collection.Item(parent=package)
    item.metadata['foo'] = "bar"

    assert item.metadata['spam'] == "eggs"
    assert item.metadata['eggs'] == "bacon"
    assert item.metadata['foo'] == "bar"
    assert "eggs" not in root.metadata.keys()
    assert "bar" not in root.metadata.keys()
    assert "bar" not in package.metadata.keys()


def test_instantiation_instance():
    instantiation = collection.Instantiation("access")
    assert isinstance(instantiation, collection.Instantiation)
    assert len(instantiation.files) == 0
    assert instantiation.category == "access"


def test_instantiation_instance_with_parent():
    item = collection.Item()
    access_instantiation = collection.Instantiation("access", parent=item)
    assert len(item.children) == 1
    assert item.instantiations["access"] == access_instantiation

    preservation_instantiation = collection.Instantiation("preservation", parent=item)
    assert len(item.children) == 2
    assert item.instantiations["preservation"] == preservation_instantiation


def test_full_package():
    root = collection.Collection(path="/usr/spam")
    root.component_metadata["package_type"] = "DS"
    my_package = collection.Package(parent=root)
    my_item = collection.Item(parent=my_package)
    my_instantiation = collection.Instantiation("access", parent=my_item)
    assert my_instantiation.metadata["package_type"] == "DS"
