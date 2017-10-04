from PyQt5.QtWidgets import QWidget, QTreeView
from .packages_model import PackageModel, PackageModel2
from hsw.package_list import PackagesList
from .package_files_delegate import FileSelectionDelegate2

class PackageBrowser(QWidget):
    def __init__(self, packages: PackagesList) -> None:
        super().__init__()
        self.setupUi(self)
        self.model = PackageModel2(packages)
        self.packageView.setModel(self.model)
        self.packageView.setItemDelegateForColumn(1, FileSelectionDelegate2(self))
        self.root = packages.root
        self.show()
