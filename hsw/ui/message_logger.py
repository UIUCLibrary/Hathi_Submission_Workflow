import abc
from PyQt5 import QtGui


class AbsObserver(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def update(self, value):
        pass


class AbsSubject(metaclass=abc.ABCMeta):
    _observers = set()

    def attach(self, observer: AbsObserver):
        self._observers |= {observer}

    def detach(self, observer: AbsObserver):
        self._observers -= {observer}

    def notify(self, value=None):
        for observer in self._observers:
            if value is None:
                observer.update()
            else:
                observer.update(value)


class Logger(AbsSubject):
    def __init__(self) -> None:
        super().__init__()
        self.messages = []

    def log(self, message):
        self.messages.append(message)
        self.notify(self.messages)

    def clean(self):
        self.messages = []
        self.notify(self.messages)
        print("Clean")

class DocumentWriter(AbsObserver):

    def __init__(self) -> None:
        self.document = QtGui.QTextDocument()


    def update(self, value):
        message = "\n".join(reversed(value))
        self.document.setPlainText(message)
