import logging
from pprint import pprint

from PyQt5 import QtWidgets
import sys
import multiprocessing
from hsw import collection_builder
from hsw.ui.wizard import HathiWizardPages, wizard_steps

def hello_world(name):
    print("HELLO {}".format(name))

class RootPageSpy(wizard_steps.SelectRoot):
    def nextId(self):
        return 1

class HathiSelectDestinationWizard(QtWidgets.QWizard):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = {
            "workflow": "BrittleBooks",
            "root": r"\\storage.library.illinois.edu\HathiTrust\HenryTest-PSR_2\Brittle Books\Brittle Books - Good"
        }
        # self.addPage(RootPageSpy(self))
        self.addPage(HathiWizardPages["SelectDestination"].wizard_page(self))

    # TODO create a simple wizard to test the load packages from root
    # Use test_object_browser.py as an example
    def initializePage(self, p_int):
        super().initializePage(p_int)
        pprint(self.data)




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
