"""Point d'entrée de l'application."""

import logging
import sys


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    from PyQt6.QtWidgets import QApplication

    from immo.ui.main_window import MainWindow

    app = QApplication(sys.argv)
    app.setApplicationName("Immo Estimateur")
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
