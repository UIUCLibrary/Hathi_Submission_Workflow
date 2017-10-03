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
from .package_files_delegate import FileSelectionDelegate2
from .packages_model import PackageModel2, PackageModel
from hathi_validate import report as hathi_validate_report


class LocatingPackagesDialog(QtWidgets.QProgressDialog):
    completed_successfully = QtCore.pyqtSignal()

    def worker(self, finished_callback: typing.Callable = None, reporter_callback: typing.Callable = None):
        package = self.package_builder.build_package(self.root)
        with self.lock:
            self.package = package
        if finished_callback:
            finished_callback()
        self.completed_successfully.emit()

    def __init__(self, package_builder, root, *__args):
        super().__init__(*__args)
        self.completed_successfully.connect(self.all_done)
        self.lock = threading.Lock()
        self.package_builder = package_builder
        self.root = root
        # self.q = queue.Queue()
        self.setRange(0, 0)
        self.package_builder = package_builder
        self.package = None
        self.setWindowTitle("Locating objects")
        self.setCancelButton(None)
        self.setLabelText("Locating your files."
                          "\nThis might take some time depending on the size of the collection.")
        self.thr = threading.Thread(target=self.worker)

    def all_done(self):
        self.close()

    def close(self):
        self.thr.join()
        value = super().close()
        print("Closing")
        return value

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
            workflow_strats = workflow.DSWorkflow()
        elif self.data['workflow'] == "BrittleBooks":
            workflow_strats = workflow.BrittleBooksWorkflow()
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
            return wizard.HathiWizardPages['Validate'].index


class SelectDestination(QtHathiWizardPage):
    page_title = "Zip Packages"
    help_information = "Select a folder to save the zipped packages"

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
        if "export_destination" in self.data:
            print(self.data['root'])
            self.source_path_text.setText(self.data['root'])
        self.registerField("export_destination*", self.source_path_text)

    def browser_folder(self):

        folder = self.source_path_text.text()

        if os.path.exists(folder):
            path = QtWidgets.QFileDialog.getExistingDirectory(self, "Find path", folder)
        else:
            path = QtWidgets.QFileDialog.getExistingDirectory(self, "Find path")
        if path:
            self.source_path_text.setText(path)

    def isComplete(self):
        root = self.field("export_destination")
        if root:
            if os.path.isdir(root) and os.path.exists(root):
                return True
        return False

    def cleanupPage(self):
        if "export_destination" in self.data:
            del self.data['export_destination']

    def validatePage(self):
        super().validatePage()
        destination = self.field("export_destination")
        if destination:
            try:
                if os.path.isdir(destination) and os.path.exists(destination):
                    self.data["export_destination"] = destination

                    return True
            except WindowsError as e:
                error_message = QtWidgets.QMessageBox(self)
                error_message.setIcon(QtWidgets.QMessageBox.Critical)
                error_message.setText("Error")
                error_text = str(e)
                error_message.setInformativeText(error_text)
        return False


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
        print("loading model")
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


class Prep(HathiWizardProcess):
    page_title = "Prep"

    def process(self):
        self.logger.log("{} Processing".format(datetime.datetime.now()))
        if self.data['workflow'] == "DS":
            processing_workflow = workflow.Workflow(workflow.DSWorkflow())
        else:
            raise Exception("invalid workflow, {}".format(self.data['workflow']))

        # foo = processing.ListProgress2(self, self.data['package'])  # ,
        # foo.logger = lambda x: self.logger.log("Prepping: {}".format(x))
        tasks = processing_workflow.prep(self.data['package'])
        processing_window = processing.ListCallableProgress(self, tasks=tasks, task_name="Prepping")
        processing_window.logger = self.logger.log
        try:

            self.logger.log("Prep started".format(datetime.datetime.now()))
            processing_window.process()
            self.logger.log("Prep ended".format(datetime.datetime.now()))
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
        if self.data['workflow'] == "DS":
            processing_workflow = workflow.Workflow(workflow.DSWorkflow())
        elif self.data['workflow'] == "BrittleBooks":
            processing_workflow = workflow.Workflow(workflow.BrittleBooksWorkflow())
        else:
            raise Exception("Unknown workflow, {}".format(self.data['workflow']))
        tasks = processing_workflow.validate(self.data['package'])
        processing_window = processing.ListCallableProgress(self, tasks=tasks, task_name="Validating")

        processing_window.logger = self.logger.log
        try:
            processing_window.process()

        except processing.ProcessCanceled:
            return False
        message = self.build_report(processing_window.results)

        self.logger.log(message)
        return True

    def build_report(self, results) -> str:
        splitter = "*" * 20
        title = "Validation report"
        sorted_results = sorted(results, key=lambda r: r.source)
        message_lines = []
        for result in sorted_results:
            message_lines.append(str(result))
        report_data = "\n".join(message_lines)

        return "\n" \
               "{}\n" \
               "{}\n" \
               "{}\n" \
               "{}\n" \
               "{}\n" \
            .format(splitter, title, splitter, report_data, splitter)


class Zip(HathiWizardProcess):
    page_title = "Zip packages for submit"

    def process(self):
        # foo = processing.ListProgress2(self, self.data['package'])
        # foo.logger = lambda x: self.logger.log("Zipping : {}".format(x))
        # lambda l: self.logger.log("{}{}".format(datetime.datetime.now(), l)))

        if self.data['workflow'] == "DS":
            processing_workflow = workflow.Workflow(workflow.DSWorkflow())
        elif self.data['workflow'] == "BrittleBooks":
            processing_workflow = workflow.Workflow(workflow.BrittleBooksWorkflow())
        else:
            raise Exception("Unknown workflow, {}".format(self.data['workflow']))
        tasks = processing_workflow.zip(self.data['package'], self.data['export_destination'])
        processing_window = processing.ListCallableProgress(self, tasks=tasks, task_name="Zipping")
        processing_window.logger = self.logger.log
        try:
            self.logger.log("Zipping")
            processing_window.process()
            self.logger.log("Zipping completed.")
            self.logger.log("Files can be found at {}".format(self.data['export_destination']))
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
