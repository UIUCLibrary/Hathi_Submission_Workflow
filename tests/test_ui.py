import pytest
from hsw.ui import packagesModel


def test_name_adapter_empty_len():
    adapter = packagesModel.NameAdapter()
    assert len(adapter) == 0


def test_name_adapter_add():
    adapter = packagesModel.NameAdapter()
    adapter.add(column_header="Title Page", data_entry="title_page")
    assert len(adapter) == 1


def test_multiple_mappings_error():
    adapter = packagesModel.NameAdapter()
    adapter.add(column_header="Title Page", data_entry="title_page")
    with pytest.raises(AttributeError):
        adapter.add(column_header="Title Page", data_entry="something_else")


def test_name_adapter_get_column_from_data_entry():
    adapter = packagesModel.NameAdapter()
    adapter.add(column_header="Title Page", data_entry="title_page")
    assert adapter.get_column_header(data_entry="title_page") == "Title Page"

def test_name_adapter_get_data_entry_from_column():
    adapter = packagesModel.NameAdapter()
    adapter.add(column_header="Title Page", data_entry="title_page")
    assert adapter.get_data_entry(column_header= "Title Page") == "title_page"
