import pytest
import os
from hsw import workflow
import itertools


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
    for package_name, package_files in itertools.groupby(brittle_books_package_files, key=lambda x: os.path.split(x)[0]):
        print(package_name)

        new_package_folder = os.path.join(tests_files_dir, package_name)
        os.mkdir(new_package_folder)

        with open(os.path.join(new_package_folder, "meta.yml"), "w") as f:
            f.write("capture_date: 2016-06-21T08:00:00Z\n")
            f.write("capture_agent: TRIGONIX\n")
            f.write("scanner_user: TRIGONIX\n")
            f.write("scanner_make: TRIGONIX\n")
            f.write("scanner_model: TRIGO-C1\n")

    for test_file in brittle_books_package_files:
        new_test_item = tests_files_dir.join(test_file)
        with open(new_test_item, "w") as f:
            pass
    return str(tests_files_dir)


def test_full_workflow(bb_collection):
    print(bb_collection)
    my_workflow = workflow.Workflow(workflow.BrittleBooksWorkflow())
    new_package = my_workflow.build_package(bb_collection)

    for package_object in new_package:
        with open(os.path.join(package_object.metadata['path'], "marc.xml"), "w") as f:
            f.write(
                '\n<record xmlns="http://www.loc.gov/MARC21/slim" xsi:schemaLocation="http://www.loc.gov/MARC21/slim http://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">')
            f.write('\n  <leader>00616nam a2200181 a 4500</leader>')
            f.write('\n  <controlfield tag="001">1251150</controlfield>')
            f.write('\n  <controlfield tag="005">20020415162036.0</controlfield>')
            f.write('\n  <controlfield tag="008">840418s1913    fr            00010 fre d</controlfield>')
            f.write('\n  <datafield tag="035" ind1=" " ind2=" ">')
            f.write('\n    <subfield code="a">(OCoLC)ocm10643170</subfield>')
            f.write('\n  </datafield>')
            f.write('\n  <datafield tag="035" ind1=" " ind2=" ">')
            f.write('\n    <subfield code="9">AHI-6903</subfield>')
            f.write('\n  </datafield>')
            f.write('\n  <datafield tag="040" ind1=" " ind2=" ">')
            f.write('\n    <subfield code="a">ORC</subfield>')
            f.write('\n    <subfield code="c">ORC</subfield>')
            f.write('\n    <subfield code="d">UIU</subfield>')
            f.write('\n  </datafield>')
            f.write('\n  <datafield tag="043" ind1=" " ind2=" ">')
            f.write('\n    <subfield code="a">e-fr---</subfield>')
            f.write('\n  </datafield>')
            f.write('\n  <datafield tag="100" ind1="1" ind2="0">')
            f.write('\n    <subfield code="a">Doumic, Rene,</subfield>')
            f.write('\n    <subfield code="d">1860-1937</subfield>')
            f.write('\n  </datafield>')
            f.write('\n  <datafield tag="245" ind1="1" ind2="0">')
            f.write('\n    <subfield code="a">De Scribe Ibsen :</subfield>')
            f.write('\n   <subfield code="b">causeries sur le tcontemporain : ouvrage r Francaise /</subfield>')
            f.write('\n    <subfield code="c">Ree Doumic.</subfield>')
            f.write('\n  </datafield>')
            f.write('\n  <datafield tag="260" ind1="0" ind2=" ">')
            f.write('\n    <subfield code="a">Paris :</subfield>')
            f.write('\n    <subfield code="b">Perrin,</subfield>')
            f.write('\n    <subfield code="c">1913.</subfield>')
            f.write('\n  </datafield>')
            f.write('\n  <datafield tag="300" ind1=" " ind2=" ">')
            f.write('\n    <subfield code="a">xvi, 352 p. ;</subfield>')
            f.write('\n    <subfield code="c">19 cm.</subfield>')
            f.write('\n  </datafield>')
            f.write('\n  <datafield tag="650" ind1=" " ind2="0">')
            f.write('\n    <subfield code="a">Drama</subfield>')
            f.write('\n    <subfield code="x">History and criticism</subfield>')
            f.write('\n  </datafield>')
            f.write('\n  <datafield tag="650" ind1=" " ind2="0">')
            f.write('\n    <subfield code="a">French drama</subfield>')
            f.write('\n    <subfield code="y">19th century</subfield>')
            f.write('\n    <subfield code="x">History and criticism.</subfield>')
            f.write('\n  </datafield>')
            f.write('\n  <datafield tag="955" ind1=" " ind2=" ">')
            f.write('\n    <subfield code="b">1251150</subfield>')
            f.write('\n  </datafield>')
            f.write('\n</record>')
            f.write('\n<?query @attr 1=12 "1251150" ?>')
            f.write('\n<?count 1 ?>')

    for task in my_workflow.update_checksums(new_package):
        task()

    errors = []
    for task in my_workflow.validate(new_package):
        errors += task()
    for error in errors:
        print(error)
    assert len(errors) == 0
