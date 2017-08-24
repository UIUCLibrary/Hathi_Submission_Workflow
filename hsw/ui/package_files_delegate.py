import os
from PyQt5.QtWidgets import QItemDelegate, QComboBox


class FileSelectionDelegate(QItemDelegate):
    def __init__(self, parent):
        self.model = parent.model
        self.choices = []
        super().__init__(parent)

    def createEditor(self, parent, QStyleOptionViewItem, QModelIndex):
        selection = QComboBox(parent)
        return selection

    def setEditorData(self, editor: QComboBox, index):
        column = index.column()
        row = index.row()
        path = self.model._packages[row].path
        self.choices = [None] + list(self.get_files(path))
        editor.addItems([str(item) for item in self.choices])
        super().setEditorData(editor, index)

    @staticmethod
    def get_files(path):
        for files in filter(lambda x: x.is_file(), os.scandir(path)):
            yield files.name
