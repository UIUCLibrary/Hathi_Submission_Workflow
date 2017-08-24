from PyQt5.QtWidgets import QWidget
from .ui_packages import Ui_PackagesDialog
from .packagesModel import PackageModel
from hsw.package_list import PackagesList

class PackageBrowser(QWidget, Ui_PackagesDialog):
    def __init__(self, packages: PackagesList) -> None:
        super().__init__()
        self.setupUi(self)
        self.model = PackageModel(packages)
        self.packageView.setModel(self.model)
        self.root = packages.root
        self.show()
