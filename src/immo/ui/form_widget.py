"""Widget de formulaire de saisie des caractéristiques du bien."""

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QDoubleSpinBox,
    QVBoxLayout,
    QWidget,
)

from immo.models import BienInput, DPEClass, EtatGeneral


class FormWidget(QWidget):
    estimate_requested = pyqtSignal(object)
    export_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("Caractéristiques du bien")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 8px;")
        layout.addWidget(title)

        addr_group = QGroupBox("Localisation")
        addr_layout = QFormLayout(addr_group)
        self.adresse = QLineEdit()
        self.adresse.setPlaceholderText("Ex : 12 rue de la Paix, 75002 Paris")
        addr_layout.addRow("Adresse :", self.adresse)
        layout.addWidget(addr_group)

        caract_group = QGroupBox("Caractéristiques")
        caract_layout = QFormLayout(caract_group)

        self.surface = QDoubleSpinBox()
        self.surface.setRange(5, 500)
        self.surface.setValue(50)
        self.surface.setSuffix(" m²")
        caract_layout.addRow("Surface :", self.surface)

        self.nb_pieces = QSpinBox()
        self.nb_pieces.setRange(1, 20)
        self.nb_pieces.setValue(2)
        caract_layout.addRow("Pièces :", self.nb_pieces)

        self.etage = QSpinBox()
        self.etage.setRange(0, 50)
        caract_layout.addRow("Étage :", self.etage)

        self.nb_etages = QSpinBox()
        self.nb_etages.setRange(0, 50)
        self.nb_etages.setSpecialValueText("Inconnu")
        caract_layout.addRow("Étages immeuble :", self.nb_etages)

        self.ascenseur = QComboBox()
        self.ascenseur.addItems(["Inconnu", "Oui", "Non"])
        caract_layout.addRow("Ascenseur :", self.ascenseur)

        self.annee = QSpinBox()
        self.annee.setRange(0, 2026)
        self.annee.setSpecialValueText("Inconnue")
        caract_layout.addRow("Année construction :", self.annee)

        self.dpe = QComboBox()
        for d in DPEClass:
            self.dpe.addItem(d.value, d)
        self.dpe.setCurrentText("N/C")
        caract_layout.addRow("DPE :", self.dpe)

        self.etat = QComboBox()
        etat_labels = {"neuf": "Neuf", "tres_bon": "Très bon", "bon": "Bon", "moyen": "Moyen", "a_renover": "À rénover"}
        for e in EtatGeneral:
            self.etat.addItem(etat_labels.get(e.value, e.value), e)
        self.etat.setCurrentIndex(2)
        caract_layout.addRow("État :", self.etat)

        layout.addWidget(caract_group)

        extras_group = QGroupBox("Annexes")
        extras_layout = QHBoxLayout(extras_group)
        self.balcon = QCheckBox("Balcon")
        self.terrasse = QCheckBox("Terrasse")
        self.parking = QCheckBox("Parking")
        self.cave = QCheckBox("Cave")
        for cb in [self.balcon, self.terrasse, self.parking, self.cave]:
            extras_layout.addWidget(cb)
        layout.addWidget(extras_group)

        buttons = QHBoxLayout()
        self.btn_estimate = QPushButton("Estimer la valeur")
        self.btn_estimate.setStyleSheet(
            "QPushButton { background-color: #4472C4; color: white; padding: 8px 16px; "
            "font-size: 14px; border-radius: 4px; }"
            "QPushButton:hover { background-color: #3561b3; }"
        )
        self.btn_estimate.clicked.connect(self._on_estimate)
        buttons.addWidget(self.btn_estimate)

        self.btn_export = QPushButton("Exporter PDF")
        self.btn_export.setEnabled(False)
        self.btn_export.clicked.connect(self.export_requested.emit)
        buttons.addWidget(self.btn_export)

        layout.addLayout(buttons)
        layout.addStretch()

    def _on_estimate(self):
        adresse = self.adresse.text().strip()
        if not adresse:
            return

        ascenseur_map = {"Inconnu": None, "Oui": True, "Non": False}

        bien = BienInput(
            adresse=adresse,
            surface_m2=self.surface.value(),
            nb_pieces=self.nb_pieces.value(),
            etage=self.etage.value(),
            nb_etages_immeuble=self.nb_etages.value() or None,
            ascenseur=ascenseur_map[self.ascenseur.currentText()],
            annee_construction=self.annee.value() or None,
            dpe=self.dpe.currentData(),
            etat=self.etat.currentData(),
            balcon=self.balcon.isChecked(),
            terrasse=self.terrasse.isChecked(),
            parking=self.parking.isChecked(),
            cave=self.cave.isChecked(),
        )
        self.estimate_requested.emit(bien)

    def set_enabled(self, enabled: bool):
        self.btn_estimate.setEnabled(enabled)

    def enable_export(self, enabled: bool):
        self.btn_export.setEnabled(enabled)
