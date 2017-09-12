from time import sleep

from PyQt5 import QtWidgets, QtCore
import abc


class ProcessCanceled(Exception):
    pass


class ProcessProgress(metaclass=abc.ABCMeta):
    def __init__(self, parent):
        self.parent = parent
        self.process_dialog = QtWidgets.QProgressDialog("Processing", "Cancel", 0, self.total_tasks, self.parent)
        self.process_dialog.setWindowModality(QtCore.Qt.WindowModal)

    @property
    @abc.abstractmethod
    def total_tasks(self) -> int:
        pass

    @property
    @abc.abstractmethod
    def current_task_index(self) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def process_next_task(self):
        raise NotImplementedError

    def process(self):

        self.process_dialog.setWindowTitle("Processing")
        self.process_dialog.show()
        for i in range(self.total_tasks):
            QtCore.QCoreApplication.processEvents()
            if self.process_dialog.wasCanceled():
                raise ProcessCanceled

            self.process_next_task()
            self.process_dialog.setValue(i + 1)

    def _update_message(self, message):
        self.process_dialog.setLabelText(message)


class DummyProgress(ProcessProgress):
    """Not to be used, mainly as an example"""

    def __init__(self, parent):
        self.items = [lambda: print("fooo") for x in range(50)]
        super().__init__(parent)
        self._counter = 0

    @property
    def total_tasks(self) -> int:
        return len(self.items)

    def process_next_task(self):
        self.items[self.current_task_index]()
        sleep(1)
        self._update_message("working on {}".format(self._counter))
        self._counter += 1

    @property
    def current_task_index(self) -> int:
        return self._counter


class ListProgress(ProcessProgress):
    """Not to be used, mainly as an example"""

    def __init__(self, parent, items: list) -> None:
        self.items = items
        super().__init__(parent)
        self._counter = 0

    @property
    def total_tasks(self) -> int:
        return len(self.items)

    @property
    def current_task_index(self) -> int:
        return self._counter

    def process_next_task(self):
        item = self.items[self._counter]
        print(item)
        self._counter += 1
