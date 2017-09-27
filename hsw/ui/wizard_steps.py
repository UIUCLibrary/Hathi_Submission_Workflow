import abc
import datetime
import logging
import os
import typing
import warnings
from hsw import workflow
import multiprocessing
import threading
import queue

import sys
from PyQt5 import QtWidgets, QtCore

# from hsw import collection_builder
from hsw.package_list import PackagesList
from . import processing
from . import wizard
from .package_files_delegate import FileSelectionDelegate, FileSelectionDelegate2
from .packages_model import PackageModel2, PackageModel


class LocatingPackagesDialog(QtWidgets.QProgressDialog):
    def worker(self, finished_callback: typing.Callable, reporter_callback: typing.Callable = None):
        package = self.package_builder.build_package(self.root)
        with self.lock:
            self.package = package
        finished_callback()

    def __init__(self, package_builder, root, *__args):
        super().__init__(*__args)
        self.lock = threading.Lock()
        self.package_builder = package_builder
        self.root = root
        self.q = queue.Queue()
        self.setRange(0, 0)
        self.package_builder = package_builder
        self.package = None
        self.setWindowTitle("Locating objects")
        self.setCancelButton(None)
        self.setLabelText("Locating your files."
                          "\nThis might take some time depending on the size of the collection.")
        self.thr = threading.Thread(target=self.worker, args=(self.close,))

    def exec_(self):
        self.thr.start()
        return super().exec_()

        #


class QtHathiWizardPage(QtWidgets.QWizardPage):
    page_title = None  # type: str
    help_information = None  # type: str

    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = parent.data
        self.my_layout = QtWidgets.QVBoxLayout(self)
        self.update_title(self)
        self.add_information_card(self)
        self.valid = True

    def initializePage(self):
        logger = logging.getLogger(__name__)
        super().initializePage()
        self.valid = True
        logger.debug(self.data)

    @classmethod
    def update_title(cls, value: "QtHathiWizardPage"):
        if cls.page_title:
            value.setTitle(cls.page_title)

    @classmethod
    def add_information_card(cls, value: "QtHathiWizardPage"):
        if value.help_information:
            value.setSubTitle(value.help_information)


class HathiWizardProcess(QtHathiWizardPage):
    @abc.abstractmethod
    def process(self):
        pass

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = parent.logger
        self.console = QtWidgets.QTextBrowser(self)
        self.console.setDocument(parent.document_logger.document)
        self.process_button = QtWidgets.QPushButton(self)
        self.process_button.setText("Process")
        self.process_button.clicked.connect(self.process)
        self.my_layout.addWidget(self.console)
        self.my_layout.addWidget(self.process_button)
        self.my_layout.setContentsMargins(0, 0, 0, 0)



        # def cleanupPage(self):
        #     super().cleanupPage()
        #     self.logger.clean()


###############################################################################
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
        self.source_path_browse_button.clicked.connect(self.browser_folder)
        self.source_path_browse_button.setText("Browse")
        self.source_path_text.textChanged.connect(self.completeChanged)
        self.source_path_layout.addWidget(self.source_path_text)
        self.source_path_layout.addWidget(self.source_path_browse_button)
        self.my_layout.addLayout(self.source_path_layout)
        if "root" in self.data:
            print(self.data['root'])
            self.source_path_text.setText(self.data['root'])
        self.registerField("RootLocation*", self.source_path_text)

    def browser_folder(self):

        folder = self.source_path_text.text()

        if os.path.exists(folder):
            path = QtWidgets.QFileDialog.getExistingDirectory(self, "Find path", folder)
        else:
            path = QtWidgets.QFileDialog.getExistingDirectory(self, "Find path")
        if path:
            self.source_path_text.setText(path)

    def isComplete(self):
        root = self.field("RootLocation")
        if root:
            if os.path.isdir(root) and os.path.exists(root):
                return True
        return False

    def validatePage(self):
        super().validatePage()
        root = self.field("RootLocation")
        if root:
            try:
                if os.path.isdir(root) and os.path.exists(root):
                    self.data["root"] = root
                    self.data["package"] = self.build_package(root)

                    return True
            except WindowsError as e:
                error_message = QtWidgets.QMessageBox(self)
                error_message.setIcon(QtWidgets.QMessageBox.Critical)
                error_message.setText("Error")
                error_text = str(e)
                error_message.setInformativeText(error_text)
        return False

    def build_package(self, root):
        if self.data['workflow'] == "DS":
            workflow_strats = workflow.DSStrategy()
        elif self.data['workflow'] == "BrittleBooks":
            workflow_strats = workflow.BrittleBooksStrategy()
        else:
            raise Exception("Unknown workflow {}".format(self.data['workflow']))
        # package_builder = collection_builder.BuildPackage(workflow_strats)
        package_builder = workflow.Workflow(workflow_strats)
        print("Loading")
        package_locator = LocatingPackagesDialog(package_builder, root)
        package_locator.exec_()
        # self.data
        return package_locator.package

    def cleanupPage(self):
        if "root" in self.data:
            del self.data['root']

    def nextId(self):
        if self.data['workflow'] == "DS":
            return wizard.HathiWizardPages['PackageBrowser'].index
        else:
            return wizard.HathiWizardPages['Prep'].index


# TODO: REMOVE WHEN SAFE TO DO SO
class PackageBrowser(QtHathiWizardPage):
    page_title = "Package Browser"

    def __init__(self, parent=None):
        warnings.warn("use PackageBrowser2 instead", DeprecationWarning)
        super().__init__(parent)
        self.package_view = QtWidgets.QTreeView(self)
        self.package_view.setContentsMargins(0, 0, 0, 0)
        self.my_layout.addWidget(self.package_view)
        self.my_layout.setContentsMargins(0, 0, 0, 0)

    def load_model(self, root):
        packages = PackagesList(root)
        try:
            for path in filter(lambda item: item.is_dir(), os.scandir(root)):
                packages.add_package(path.path)
            self.package_view.setEnabled(True)

        except OSError as e:
            self.package_view.setEnabled(False)
            self.valid = False
            error_message = QtWidgets.QMessageBox(self)
            error_message.setIcon(QtWidgets.QMessageBox.Critical)
            error_message.setText("Error")
            error_message.setInformativeText(str(e))
            error_message.setWindowTitle("Error")
            error_message.show()
        # self.model = PackageModel2(packages)
        self.model = PackageModel(packages)

    def initializePage(self):
        super().initializePage()
        root = self.field("RootLocation")
        self.load_model(root)

        self.package_view.setModel(self.model)
        self.package_view.setItemDelegateForColumn(1, FileSelectionDelegate(self))


class PackageBrowser2(QtHathiWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.package_view = QtWidgets.QTreeView(self)
        self.package_view.setContentsMargins(0, 0, 0, 0)
        self.my_layout.addWidget(self.package_view)

        self.my_layout.setContentsMargins(0, 0, 0, 0)

    def initializePage(self):
        print("running alterntiave")
        # super().initializePage()
        # root = self.field("RootLocation")

        packages = self.data["package"]

        # package = self.f
        self.load_model2(packages)

        self.package_view.setModel(self.model)
        self.package_view.setItemDelegateForColumn(1, FileSelectionDelegate2(self))

    def load_model2(self, packages):
        print("loaing model")
        print(packages)
        self.model = PackageModel2(packages)
        # self.model = PackageModel(packages)

    def isComplete(self):
        if not self.valid:
            return False
        return True

    def validatePage(self):
        if not self.valid:
            return False

        self.data["package"] = self.model._packages
        return True


# FIXME: HathiTrust Brittlebooks skips previous step so there no data has been set yet
class Prep(HathiWizardProcess):
    page_title = "Prep"

    def process(self):
        self.logger.log("{} Processing".format(datetime.datetime.now()))
        foo = processing.ListProgress2(self, self.data['package'])  # ,
        foo.logger = lambda x: self.logger.log("Prepping: {}".format(x))
        try:
            foo.process()
        except processing.ProcessCanceled:
            return False
        return True


class EndPage(QtHathiWizardPage):
    page_title = "End"
    help_information = "This is the end of the Wizard"

    def isCommitPage(self):
        return True


class Validate(HathiWizardProcess):
    page_title = "Validate Package"

    def process(self):
        foo = processing.ListProgress2(self, self.data['package'])
        foo.logger = lambda x: self.logger.log("Validating: {}".format(x))
        try:
            foo.process()
        except processing.ProcessCanceled:
            return False
        return True


class Zip(HathiWizardProcess):
    page_title = "Zip packages for submit"

    def process(self):
        foo = processing.ListProgress2(self, self.data['package'])
        foo.logger = lambda x: self.logger.log("Zipping : {}".format(x))
        # lambda l: self.logger.log("{}{}".format(datetime.datetime.now(), l)))
        try:
            foo.process()
        except processing.ProcessCanceled:
            return False
        return True


class WorkflowSelection(QtHathiWizardPage):
    page_title = "Select Workflow"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selection = None
        self.selection_layout = QtWidgets.QVBoxLayout()
        self.workflow_box = QtWidgets.QGroupBox(self)
        self.workflow_box.setTitle("Workflows")
        self.workflow_box.setLayout(self.selection_layout)
        self.option_group = QtWidgets.QButtonGroup(self.workflow_box)
        self.option_group.setExclusive(True)
        self.option1 = QtWidgets.QRadioButton(self)
        self.option1.setText("DS")
        self.option1.setChecked(True)
        self.option_group.addButton(self.option1)
        self.selection_layout.addWidget(self.option1)

        self.option2 = QtWidgets.QRadioButton(self)
        self.option2.setText("BrittleBooks")
        self.option_group.addButton(self.option2)
        self.option_group.buttonToggled.connect(self.updated)
        self.selection_layout.addWidget(self.option2)

        self.my_layout.addWidget(self.workflow_box)

    def updated(self, selection: QtWidgets.QRadioButton):
        if selection.isChecked():
            self.setField("workflow", selection.text())

    def validatePage(self):
        is_valid = super().validatePage()
        if is_valid:
            self.data['workflow'] = self.option_group.checkedButton().text()
        return is_valid

    def cleanupPage(self):
        self.setField("workflow", None)
        if "workflow" in self.data:
            del self.data["workflow"]

# TODO: register self.selection
