import sys

from PySide6 import QtCore, QtWidgets
from qt_material import apply_stylesheet

from controle_financas.main_window import MainWindow

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    QtCore.QLocale.setDefault(QtCore.QLocale.Language.Portuguese)
    apply_stylesheet(app, 'dark_blue.xml')
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())
