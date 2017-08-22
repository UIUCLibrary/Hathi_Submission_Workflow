import sys
from PyQt5 import QtWidgets, QtCore
from hsw.ui import PackageBroswer
# from .ui.ui_packages import Ui_PackagesDialog
# 
# 
# class PackageBrowser(Ui_PackagesDialog):
#     pass

def main():
    app = QtWidgets.QApplication(sys.argv)
    # TODO setup args
    try:
        window = PackageBroswer(sys.argv[1])
    except IndexError:
        print("Missing path")
        sys.exit(1)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()