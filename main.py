import sys
from PyQt5.QtWidgets import QApplication
from ui.mainwindow import MainWindow
from ui.api_key_dialog import ApiKeyDialog, load_api_key


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("CodeTab AI") #uygulama ismo

    if not load_api_key():
        dialog = ApiKeyDialog(first_run=True)
        if dialog.exec_() != dialog.Accepted:
            sys.exit(0)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
