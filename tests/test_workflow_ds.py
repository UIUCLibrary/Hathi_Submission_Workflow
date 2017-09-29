import os
import pytest
from hsw import workflow
import tempfile

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
        package_path = os.path.join(tests_files_dir, package_name)
        os.mkdir(package_path)
        with open(os.path.join(package_path, "marc.xml"), "w") as f:
            f.write("""<record xmlns="http://www.loc.gov/MARC21/slim" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.loc.gov/MARC21/slim http://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd">
  <leader>01342cam a2200277Ka 4500</leader>
  <controlfield tag="001">2693684</controlfield>
  <controlfield tag="005">20170511212234.0</controlfield>
  <controlfield tag="008">900530s1845    it bf         000 0 ita d</controlfield>
  <datafield ind1=" " ind2=" " tag="035">
    <subfield code="a">(OCoLC)ocm77313810</subfield>
  </datafield>
  <datafield ind1=" " ind2=" " tag="040">
    <subfield code="a">UIU</subfield>
    <subfield code="e">dcrmb</subfield>
    <subfield code="c">UIU</subfield>
    <subfield code="d">UKMGB</subfield>
    <subfield code="d">UIU</subfield>
  </datafield>
  <datafield ind1=" " ind2=" " tag="019">
    <subfield code="a">561873437</subfield>
  </datafield>
  <datafield ind1=" " ind2=" " tag="035">
    <subfield code="a">(OCoLC)77313810</subfield>
    <subfield code="z">(OCoLC)561873437</subfield>
  </datafield>
  <datafield ind1=" " ind2=" " tag="043">
    <subfield code="a">e-it---</subfield>
  </datafield>
  <datafield ind1=" " ind2=" " tag="049">
    <subfield code="a">UIUU</subfield>
    <subfield code="o">skip</subfield>
  </datafield>
  <datafield ind1="1" ind2=" " tag="100">
    <subfield code="a">Monti, Carlo,</subfield>
    <subfield code="d">19th cent.</subfield>
  </datafield>
  <datafield ind1="1" ind2="0" tag="245">
    <subfield code="a">Studio topografico intorno alla piu&#768; breve congiunzione stradale fra i due mari nell'alta Italia merce&#768; un varco esistente nel tronco settentrionale dell'Apennino :</subfield>
    <subfield code="b">memoria /</subfield>
    <subfield code="c">dell'avvocato Carlo Monti.</subfield>
  </datafield>
  <datafield ind1=" " ind2=" " tag="260">
    <subfield code="a">Bologna :</subfield>
    <subfield code="b">Tipi governativi alla Volpe,</subfield>
    <subfield code="c">1845.</subfield>
  </datafield>
  <datafield ind1=" " ind2=" " tag="300">
    <subfield code="a">48 p., [1] folded leaf of plates :</subfield>
    <subfield code="b">map ;</subfield>
    <subfield code="c">27 cm.</subfield>
  </datafield>
  <datafield ind1=" " ind2=" " tag="500">
    <subfield code="a">Cavagna 1693: University of Illinois bookplate: "From the library of Conte Antonio Cavagna Sangiuliani di Gualdana Lazelada di Bereguardo, purchased 1921".</subfield>
    <subfield code="5">IU-R</subfield>
  </datafield>
  <datafield ind1=" " ind2=" " tag="500">
    <subfield code="a">625.7 M767s: Cavagna Library stamp on p. [3].</subfield>
    <subfield code="5">IU-R</subfield>
  </datafield>
  <datafield ind1=" " ind2="0" tag="650">
    <subfield code="a">Roads</subfield>
    <subfield code="z">Italy.</subfield>
  </datafield>
  <datafield ind1="1" ind2=" " tag="700">
    <subfield code="a">Cavagna Sangiuliani di Gualdana, Antonio,</subfield>
    <subfield code="c">conte,</subfield>
    <subfield code="d">1843-1913,</subfield>
    <subfield code="e">former owner.</subfield>
    <subfield code="5">IU-R</subfield>
  </datafield>
  <datafield ind1="2" ind2=" " tag="710">
    <subfield code="a">Cavagna Collection (University of Illinois at Urbana-Champaign Library)</subfield>
    <subfield code="5">IU-R</subfield>
  </datafield>
  <datafield ind1=" " ind2=" " tag="752">
    <subfield code="a">Italy</subfield>
    <subfield code="d">Bologna.</subfield>
  </datafield>
  <datafield ind1="4" ind2="1" tag="856">
    <subfield code="u">https://hdl.handle.net/2027/uiug.30112088620619</subfield>
    <subfield code="3">HathiTrust Digital Library</subfield>
  </datafield>
  <datafield ind1=" " ind2=" " tag="994">
    <subfield code="a">C0</subfield>
    <subfield code="b">UIU</subfield>
  </datafield>
  <datafield ind1=" " ind2=" " tag="955">
    <subfield code="b">2693684</subfield>
  </datafield>
</record>""")



    for test_file in ds_collection_package_files:
        new_test_item = tests_files_dir.join(test_file)
        with open(new_test_item, "w") as f:
            pass

    return str(tests_files_dir)


def test_prep(ds_collection):
    ds_workflow = workflow.Workflow(workflow.DSWorkflow())
    new_package = ds_workflow.build_package(ds_collection)

    new_package.children[0].component_metadata["title_page"] = "00000002.jp2"
    new_package.children[1].component_metadata["title_page"] = "00000002.jp2"
    new_package.children[2].component_metadata["title_page"] = "00000002.jp2"

    ds_workflow.prep(new_package)
    prepped_package = ds_workflow.build_package(new_package.path)
    errors = ds_workflow.validate(prepped_package)

    for package_object in prepped_package:
        path = package_object.metadata['path']
        meta = os.path.join(path, "meta.yml")
        assert os.path.exists(meta)
        with open(meta, "r") as f:
            yaml = f.read()
            if """    00000002.jp2:
        label: TITLE""" not in yaml:
                pytest.fail("missing title_page in {}".format(meta))

    for error in errors:
        print(error)
    assert len(errors) == 0
    with tempfile.TemporaryDirectory() as temp_destination:
        ds_workflow.zip(prepped_package, temp_destination)
        assert os.path.exists(os.path.join(temp_destination, "1564651.zip"))
        assert os.path.exists(os.path.join(temp_destination, "4564654.zip"))
        assert os.path.exists(os.path.join(temp_destination, "7213538.zip"))

