import logging
from pprint import pprint

from PyQt5 import QtWidgets
import sys
import multiprocessing
from hsw import collection_builder, workflow
from hsw.ui.wizard import HathiWizardPages, wizard_steps
from hsw.ui import message_logger
from hsw.ui.wizard_steps import LocatingPackagesDialog


def hello_world(name):
    print("HELLO {}".format(name))


class RootPageSpy(wizard_steps.SelectRoot):
    def nextId(self):
        return 1


class HathiSelectDestinationWizard(QtWidgets.QWizard):
    def __init__(self, parent=None):
        super().__init__(parent)
        root = r"\\storage.library.illinois.edu\HathiTrust\HenryTest-PSR_2\Brittle Books\Brittle Books - Good"
        # root = r"\\storage.library.illinois.edu\\HathiTrust\\HenryTest-PSR_2\\DCC\\Test_PSR-37_20170925"

        self.data = {
            "workflow": "BrittleBooks",
            # "workflow": "DS",
            "root": root,
        }

        self.data["package"] = self.build_package(root)
        self.logger = message_logger.Logger()
        # self.addPage(RootPageSpy(self))

        self.document_logger = message_logger.DocumentWriter()
        self.logger.attach(self.document_logger)
        self.addPage(HathiWizardPages["Validate"].wizard_page(self))

    # TODO create a simple wizard to test the load packages from root
    # Use test_object_browser.py as an example
    def initializePage(self, p_int):
        super().initializePage(p_int)
        pprint(self.data)

    def build_package(self, root):
        if self.data['workflow'] == "DS":
            workflow_strats = workflow.DSWorkflow()
        elif self.data['workflow'] == "BrittleBooks":
            workflow_strats = workflow.BrittleBooksWorkflow()
        else:
            raise Exception("Unknown workflow {}".format(self.data['workflow']))
        # package_builder = collection_builder.BuildPackage(workflow_strats)
        package_builder = workflow.Workflow(workflow_strats)
        print("Loading")
        package_locator = LocatingPackagesDialog(package_builder, root)
        package_locator.exec_()
        # self.data
        return package_locator.package


def main():
    print("opening simple Wizard")
    logging.root.setLevel(logging.DEBUG)
    logger = logging.getLogger(__name__)
    std_handler = logging.StreamHandler(sys.stdout)
    logging.root.addHandler(std_handler)
    logger.debug("Debug on")
    app = QtWidgets.QApplication(sys.argv)

    wiz = HathiSelectDestinationWizard()
    wiz.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
