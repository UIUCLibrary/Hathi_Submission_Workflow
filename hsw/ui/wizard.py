from PyQt5 import QtWidgets

from hsw.ui import message_logger
from . import wizard_steps


class HathiWizard(QtWidgets.QWizard):
    NUM_PAGES = 1

    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = {}
        self.logger = message_logger.Logger()
        self.document_logger = message_logger.DocumentWriter()
        self.logger.attach(self.document_logger)
        self.addPage(wizard_steps.Welcome(self))
        self.addPage(wizard_steps.WorkflowSelection(self))
        self.addPage(wizard_steps.SelectRoot(self))
        self.addPage(wizard_steps.PackageBrowser(self))
        self.addPage(wizard_steps.Prep(self))
        self.addPage(wizard_steps.Validate(self))
        self.addPage(wizard_steps.Zip(self))
        self.addPage(wizard_steps.EndPage(self))
