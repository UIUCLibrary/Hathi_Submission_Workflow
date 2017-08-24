from PyQt5.QtWidgets import QWidget, QTreeView
from .ui_packages import Ui_PackagesDialog
from .packages_model import PackageModel
from hsw.package_list import PackagesList
from .package_files_delegate import FileSelectionDelegate

class PackageBrowser(QWidget, Ui_PackagesDialog):
    def __init__(self, packages: PackagesList) -> None:
        super().__init__()
        self.setupUi(self)
        self.model = PackageModel(packages)
        self.packageView.setModel(self.model)
        self.packageView.setItemDelegateForColumn(1, FileSelectionDelegate(self))
        self.root = packages.root
        self.show()
