from PyQt5 import QtWidgets

from hsw.ui import message_logger
from . import wizard_steps

from collections import namedtuple

HathiWizardPageSteps = namedtuple("HathiWizardPageSteps", ("index", "wizard_page"))

HathiWizardPages = {
    "Welcome":
        HathiWizardPageSteps(index=0, wizard_page=wizard_steps.Welcome),
    "WorkflowSelection":
        HathiWizardPageSteps(index=1, wizard_page=wizard_steps.WorkflowSelection),
    "SelectRoot":
        HathiWizardPageSteps(index=2, wizard_page=wizard_steps.SelectRoot),
    "PackageBrowser":
        HathiWizardPageSteps(index=3, wizard_page=wizard_steps.PackageBrowser2),
    "Prep":
        HathiWizardPageSteps(index=4, wizard_page=wizard_steps.Prep),
    "Validate":
        HathiWizardPageSteps(index=5, wizard_page=wizard_steps.Validate),
    "Zip":
        HathiWizardPageSteps(index=6, wizard_page=wizard_steps.Zip),
    "EndPage":
        HathiWizardPageSteps(index=7, wizard_page=wizard_steps.EndPage),
}

class HathiWizard(QtWidgets.QWizard):
    NUM_PAGES = 1

    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = {}
        self.logger = message_logger.Logger()
        self.document_logger = message_logger.DocumentWriter()
        self.logger.attach(self.document_logger)
        for key, wizard_page in HathiWizardPages.items():
            self.setPage(wizard_page.index, wizard_page.wizard_page(self))

