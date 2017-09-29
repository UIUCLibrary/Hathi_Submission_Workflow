from pprint import pprint

from PyQt5 import QtWidgets
import sys

from hsw import collection_builder
from hsw import workflow
from hsw.ui.wizard import HathiWizardPages

ROOT = r"\\storage.library.illinois.edu\HathiTrust\HenryTest-PSR_2\DCC\Test_PSR-37_20170925"

class HathiFilesWizard(QtWidgets.QWizard):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = {
            "workflow": "DS"
        }
        self.addPage(HathiWizardPages["PackageBrowser"].wizard_page(self))
        self.addPage(HathiWizardPages["EndPage"].wizard_page(self))
        self.data["root"] = ROOT
        workflow_strat = collection_builder.DSStrategy()

        # package_builder = collection_builder.BuildPackage(workflow_strat)
        package_builder = workflow.Workflow(workflow_strat)
        self.data["package"] = package_builder.build_package(ROOT)

    #
    def initializePage(self, p_int):
        super().initializePage(p_int)
        for object in self.data["package"]:
            pprint(object.metadata)
        pprint(self.data)



def main():
    print("opening simple Wizard")
    app = QtWidgets.QApplication(sys.argv)
    wiz = HathiFilesWizard()
    wiz.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
