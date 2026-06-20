"""Widget d'affichage des résultats d'estimation."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from immo.models import EstimationResult


class ResultsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        self.estimation_group = QGroupBox("Estimation")
        est_layout = QHBoxLayout(self.estimation_group)

        self.lbl_bas = self._make_price_label("--", "Estimation basse")
        self.lbl_median = self._make_price_label("--", "Estimation médiane")
        self.lbl_haut = self._make_price_label("--", "Estimation haute")
        self.lbl_confiance = self._make_price_label("--", "Confiance")

        for w in [self.lbl_bas, self.lbl_median, self.lbl_haut, self.lbl_confiance]:
            est_layout.addWidget(w)

        layout.addWidget(self.estimation_group)

        self.facteurs_group = QGroupBox("Facteurs explicatifs")
        self.facteurs_layout = QVBoxLayout(self.facteurs_group)
        self.facteurs_label = QLabel("Lancez une estimation pour voir les résultats.")
        self.facteurs_layout.addWidget(self.facteurs_label)
        layout.addWidget(self.facteurs_group)

        self.comparables_group = QGroupBox("Comparables")
        comp_layout = QVBoxLayout(self.comparables_group)
        self.comp_table = QTableWidget(0, 6)
        self.comp_table.setHorizontalHeaderLabels(
            ["Date", "Surface", "Prix", "€/m²", "Distance", "Score"]
        )
        self.comp_table.horizontalHeader().setStretchLastSection(True)
        comp_layout.addWidget(self.comp_table)
        layout.addWidget(self.comparables_group)

    def _make_price_label(self, value: str, title: str) -> QWidget:
        w = QWidget()
        l = QVBoxLayout(w)
        l.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("font-size: 11px; color: #666;")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_value = QLabel(value)
        lbl_value.setStyleSheet("font-size: 18px; font-weight: bold;")
        lbl_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_value.setObjectName("value")
        l.addWidget(lbl_title)
        l.addWidget(lbl_value)
        return w

    def _fmt_price(self, prix: float) -> str:
        return f"{prix:,.0f} €".replace(",", " ")

    def display(self, result: EstimationResult):
        self.lbl_bas.findChild(QLabel, "value").setText(self._fmt_price(result.prix_bas))
        self.lbl_median.findChild(QLabel, "value").setText(self._fmt_price(result.prix_median))
        self.lbl_median.findChild(QLabel, "value").setStyleSheet(
            "font-size: 22px; font-weight: bold; color: #2e7d32;"
        )
        self.lbl_haut.findChild(QLabel, "value").setText(self._fmt_price(result.prix_haut))
        self.lbl_confiance.findChild(QLabel, "value").setText(f"{result.confiance_pct:.0f} %")

        for i in reversed(range(self.facteurs_layout.count())):
            self.facteurs_layout.itemAt(i).widget().deleteLater()

        for f in result.facteurs_explicatifs[:6]:
            color = "#2e7d32" if f["impact_pct"] > 0 else "#c62828" if f["impact_pct"] < 0 else "#666"
            signe = "+" if f["impact_pct"] > 0 else ""
            lbl = QLabel(f"<span style='color:{color}'>{signe}{f['impact_pct']}%</span> — {f['description']}")
            lbl.setWordWrap(True)
            self.facteurs_layout.addWidget(lbl)

        self.comp_table.setRowCount(len(result.comparables))
        for i, c in enumerate(result.comparables):
            self.comp_table.setItem(i, 0, QTableWidgetItem(c.date_mutation.strftime("%d/%m/%Y")))
            self.comp_table.setItem(i, 1, QTableWidgetItem(f"{c.surface_m2:.0f} m²"))
            self.comp_table.setItem(i, 2, QTableWidgetItem(self._fmt_price(c.prix)))
            self.comp_table.setItem(i, 3, QTableWidgetItem(f"{c.prix_m2:,.0f}".replace(",", " ")))
            self.comp_table.setItem(i, 4, QTableWidgetItem(f"{c.distance_m:.0f} m"))
            self.comp_table.setItem(i, 5, QTableWidgetItem(f"{c.score_similarite:.0%}"))
