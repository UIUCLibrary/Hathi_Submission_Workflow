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
        # TODO refactor to use an enum
        self.setPage(0, wizard_steps.Welcome(self))
        self.setPage(1, wizard_steps.WorkflowSelection(self))
        self.setPage(2, wizard_steps.SelectRoot(self))
        self.setPage(3, wizard_steps.PackageBrowser(self))
        self.setPage(4, wizard_steps.Prep(self))
        self.setPage(5, wizard_steps.Validate(self))
        self.setPage(6, wizard_steps.Zip(self))
        self.setPage(7, wizard_steps.EndPage(self))
