from PyQt5 import QtWidgets
from .ui_packages import Ui_PackagesDialog
class PackageBroswer(QtWidgets.QWidget, Ui_PackagesDialog):
    def __init__(self, path) -> None:
        super().__init__()
        self.setupUi(self)
        self.root = path
        self.show()

