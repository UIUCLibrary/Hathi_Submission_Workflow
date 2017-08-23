import sys
import os
from PyQt5.QtWidgets import QApplication
from hsw.ui import PackageBrowser
from hsw.packages import Packages

def main():
    app = QApplication(sys.argv)
    # TODO setup args
    try:
        my_packages = Packages(root=sys.argv[1])
        for path in filter(lambda item: item.is_dir(), os.scandir(sys.argv[1])):
            my_packages.add_package(path.path)
        print(len(my_packages))
        window = PackageBrowser(packages=my_packages)
    except IndexError:
        print("Missing path")
        sys.exit(1)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()