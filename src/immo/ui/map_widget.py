"""Widget de carte interactive avec Folium/QWebEngine."""

import logging
import tempfile
from pathlib import Path

from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QVBoxLayout, QWidget

from immo.models import EstimationResult

logger = logging.getLogger(__name__)

MAP_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8"/>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9/dist/leaflet.css"/>
    <script src="https://unpkg.com/leaflet@1.9/dist/leaflet.js"></script>
    <style>html,body,#map{{margin:0;padding:0;height:100%;}}</style>
</head>
<body>
<div id="map"></div>
<script>
var map = L.map('map').setView([{lat}, {lon}], 15);
L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
    attribution: '&copy; OpenStreetMap'
}}).addTo(map);

L.marker([{lat}, {lon}], {{
    icon: L.divIcon({{
        html: '<div style="background:#c62828;color:white;padding:4px 8px;border-radius:4px;font-weight:bold;white-space:nowrap;">Bien estimé</div>',
        className: ''
    }})
}}).addTo(map);

{markers}
</script>
</body>
</html>
"""

MARKER_TEMPLATE = """
L.circleMarker([{lat}, {lon}], {{
    radius: 6, color: '#4472C4', fillColor: '#4472C4', fillOpacity: 0.7
}}).addTo(map).bindPopup('<b>{prix}</b><br>{surface} m² — {prix_m2} €/m²<br>{date}<br>Score: {score}');
"""


class MapWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.web = QWebEngineView()
        layout.addWidget(self.web)
        self.web.setHtml("<html><body><p style='padding:20px;color:#999;'>La carte s'affichera après une estimation.</p></body></html>")

    def display(self, result: EstimationResult):
        markers = ""
        for c in result.comparables:
            markers += MARKER_TEMPLATE.format(
                lat=c.latitude,
                lon=c.longitude,
                prix=f"{c.prix:,.0f} €".replace(",", " "),
                surface=f"{c.surface_m2:.0f}",
                prix_m2=f"{c.prix_m2:,.0f}".replace(",", " "),
                date=c.date_mutation.strftime("%d/%m/%Y"),
                score=f"{c.score_similarite:.0%}",
            )

        html = MAP_TEMPLATE.format(
            lat=result.geocoding.latitude,
            lon=result.geocoding.longitude,
            markers=markers,
        )
        self.web.setHtml(html)
