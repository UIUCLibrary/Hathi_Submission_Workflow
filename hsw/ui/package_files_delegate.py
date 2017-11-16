import os

from PyQt5.QtWidgets import QItemDelegate, QComboBox


class FileSelectionDelegate2(QItemDelegate):
    def __init__(self, parent):
        self.model = parent.model
        self.choices = []
        self.acceptable_extensions = [".jp2", ".tif"]
        super().__init__(parent)

    def createEditor(self, parent, QStyleOptionViewItem, QModelIndex):
        selection = QComboBox(parent)
        return selection

    def setEditorData(self, editor: QComboBox, index):
        column = index.column()
        row = index.row()
        package_object = self.model._packages[row]
        item_names = []
        for item in package_object:
            for file_name in item.instantiations["access"].files:
                basename = os.path.basename(file_name)
                base, ext = os.path.splitext(basename)
                if ext.lower() in self.acceptable_extensions:
                    item_names.append(basename)
            # item_names.append(item.metadata["item_name"])
        self.choices = item_names
        editor.addItems([str(item) for item in self.choices])
        super().setEditorData(editor, index)

    @staticmethod
    def get_files(path):
        for files in filter(lambda x: x.is_file(), os.scandir(path)):
            yield files.name
