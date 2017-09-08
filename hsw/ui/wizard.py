from PyQt5 import QtWidgets
from . import wizard_steps


class HathiWizard(QtWidgets.QWizard):
    NUM_PAGES = 1

    def __init__(self, parent=None):
        super().__init__(parent)
        self.addPage(wizard_steps.Welcome(self))
        self.addPage(wizard_steps.WorkflowSelection(self))
        self.addPage(wizard_steps.SelectRoot(self))
        self.addPage(wizard_steps.PackageBrowser(self))
        self.addPage(wizard_steps.EndPage(self))
