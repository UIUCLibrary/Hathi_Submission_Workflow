import os
from PyQt5 import QtWidgets
from .packages_model import PackageModel
from hsw.package_list import PackagesList
from .package_files_delegate import FileSelectionDelegate


class QtHathiWizardPage(QtWidgets.QWizardPage):
    page_title = None
    help_information = None

    def __init__(self, parent=None):
        super().__init__(parent)
        self.my_layout = QtWidgets.QVBoxLayout(self)
        self.update_title(self)
        self.add_information_card(self)
        self.help_information = QtWidgets.QLabel(self)

    @classmethod
    def update_title(cls, value: "QtHathiWizardPage"):
        if cls.page_title:
            value.setTitle(cls.page_title)

    @classmethod
    def add_information_card(cls, value: "QtHathiWizardPage"):
        if value.help_information:
            value._info_card = QtWidgets.QLabel(value)
            value._info_card.setText(value.help_information)
            value.my_layout.addWidget(value._info_card)


class Welcome(QtHathiWizardPage):
    page_title = "Welcome to the Hathi Trust Submission Workflow Wizard"
    help_information = "This wizard will walk you through the steps needed to submit packages to HathiTrust"


class SelectRoot(QtHathiWizardPage):
    page_title = "Packages Location"
    help_information = "Select root folder of package"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.source_path_layout = QtWidgets.QHBoxLayout()
        self.source_path_text = QtWidgets.QLineEdit(self)
        self.source_path_browse_button = QtWidgets.QPushButton(self)
        self.source_path_browse_button.setText("Browse")
        self.source_path_layout.addWidget(self.source_path_text)
        self.source_path_layout.addWidget(self.source_path_browse_button)
        self.my_layout.addLayout(self.source_path_layout)


class PackageBrowser(QtHathiWizardPage):
    page_title = "Package Browser"

    def __init__(self, parent=None):
        super().__init__(parent)
        # TODO FIX THIS so it's loaded between steps
        packages = PackagesList("C:\\Users\\Public")
        for path in filter(lambda item: item.is_dir(), os.scandir("C:\\Users\\Public")):
            packages.add_package(path.path)

        self.model = PackageModel(packages)
        self.package_view = QtWidgets.QTreeView(self)
        self.package_view.setModel(self.model)
        self.package_view.setItemDelegateForColumn(1, FileSelectionDelegate(self))
        self.my_layout.addWidget(self.package_view)


class EndPage(QtHathiWizardPage):
    page_title = "End"
    help_information = "This is the end of the Wizard"


class WorkflowSelection(QtHathiWizardPage):
    page_title = "Select Workflow"
    help_information = "Select your workflow"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selection1 = QtWidgets.QRadioButton(self)
        self.selection1.setText("DS")
        self.selection2 = QtWidgets.QRadioButton(self)
        self.selection2.setText("Vendors")
        self.my_layout.addWidget(self.selection1)
        self.my_layout.addWidget(self.selection2)
