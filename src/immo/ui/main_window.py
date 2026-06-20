"""Fenêtre principale de l'application."""

import logging
import sys
from pathlib import Path

from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QSplitter,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from immo.models import BienInput, EstimationResult
from immo.orchestrator import run_estimation
from immo.report.pdf_generator import generate_report
from immo.ui.form_widget import FormWidget
from immo.ui.map_widget import MapWidget
from immo.ui.results_widget import ResultsWidget

logger = logging.getLogger(__name__)


class EstimationWorker(QThread):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, bien: BienInput):
        super().__init__()
        self.bien = bien

    def run(self):
        try:
            result = run_estimation(self.bien)
            self.finished.emit(result)
        except Exception as e:
            logger.error("Erreur estimation", exc_info=True)
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Estimateur de Valeur Immobilière")
        self.setMinimumSize(1200, 800)

        self._result: EstimationResult | None = None
        self._worker: EstimationWorker | None = None
        self._setup_ui()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        left = QWidget()
        left_layout = QVBoxLayout(left)
        self.form = FormWidget()
        self.form.estimate_requested.connect(self._on_estimate)
        self.form.export_requested.connect(self._on_export)
        left_layout.addWidget(self.form)

        self.progress = QProgressBar()
        self.progress.setVisible(False)
        left_layout.addWidget(self.progress)

        right = QWidget()
        right_layout = QVBoxLayout(right)

        self.results = ResultsWidget()
        right_layout.addWidget(self.results)

        self.map_widget = MapWidget()
        right_layout.addWidget(self.map_widget)

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setSizes([400, 800])
        layout.addWidget(splitter)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Prêt")

    def _on_estimate(self, bien: BienInput):
        self.progress.setVisible(True)
        self.progress.setRange(0, 0)
        self.status_bar.showMessage("Estimation en cours...")
        self.form.set_enabled(False)

        self._worker = EstimationWorker(bien)
        self._worker.finished.connect(self._on_result)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_result(self, result: EstimationResult):
        self._result = result
        self.progress.setVisible(False)
        self.form.set_enabled(True)
        self.form.enable_export(True)

        self.results.display(result)
        self.map_widget.display(result)

        self.status_bar.showMessage(
            f"Estimation : {result.prix_median:,.0f} € "
            f"(confiance {result.confiance_pct:.0f} %, "
            f"{result.nb_comparables} comparables)"
        )

    def _on_error(self, message: str):
        self.progress.setVisible(False)
        self.form.set_enabled(True)
        self.status_bar.showMessage("Erreur")
        QMessageBox.critical(self, "Erreur d'estimation", message)

    def _on_export(self):
        if not self._result:
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Exporter le rapport", "estimation.pdf", "PDF (*.pdf)"
        )
        if path:
            try:
                generate_report(self._result, Path(path))
                self.status_bar.showMessage(f"Rapport exporté : {path}")
                QMessageBox.information(self, "Export", f"Rapport PDF généré :\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "Erreur export", str(e))
