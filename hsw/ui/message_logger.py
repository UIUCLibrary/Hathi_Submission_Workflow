import abc
from PyQt5.QtGui import QTextDocument


class AbsObserver(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def update(self, value):
        pass


class AbsSubject(metaclass=abc.ABCMeta):
    _observers = set()  # type: ignore

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
        self.messages = []  # type: ignore

    def log(self, message):
        self.messages.append(str(message))
        self.notify(self.messages)

    def clean(self):
        self.messages = []
        self.notify(self.messages)


class DocumentWriter(AbsObserver):
    def __init__(self) -> None:
        self.document = QTextDocument()

    def update(self, value):
        message = "\n".join(reversed(value))

        self.document.setPlainText(message)
