from PyQt5.QtCore import QAbstractTableModel, Qt, QVariant
from hsw.packages import Packages
from collections import namedtuple

HeaderMap = namedtuple("HeaderMap", ("column_header", "data_entry"))

class PackageModel(QAbstractTableModel):

    public_headers = {
        0: HeaderMap(column_header="Package", data_entry=""),
        1: HeaderMap(column_header="Title Page", data_entry="title_page")
    }
    # # public_headers = [
    #     "Package",
    #     "Title Page",
    # ]
    def __init__(self, packages: Packages):
        super().__init__()
        self._packages = packages

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self._packages)

    def columnCount(self, parent=None, *args, **kwargs):
        return len(PackageModel.public_headers)

    def headerData(self, index, orientation, role=None):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            try:
                return PackageModel.public_headers[index].column_header
            except IndexError:
                return ""
        super().headerData(index, orientation, role)

    def data(self, index, role=None):
        row = index.row()
        column = index.column()
        if role == Qt.DisplayRole:
            # print(self._packages[])
            return "ads"
        return QVariant()
        # return super().data(index, role)
