"""Génération du rapport PDF d'estimation."""

import logging
from datetime import date
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from immo.models import EstimationResult

logger = logging.getLogger(__name__)

PAGE_W, PAGE_H = A4


def generate_report(result: EstimationResult, output_path: Path) -> Path:
    """Génère un rapport PDF complet pour une estimation."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle", parent=styles["Title"], fontSize=18, spaceAfter=12
    )
    heading_style = ParagraphStyle(
        "CustomHeading", parent=styles["Heading2"], fontSize=13, spaceBefore=16, spaceAfter=8
    )
    body_style = styles["Normal"]

    elements = []

    elements.append(Paragraph("Rapport d'Estimation Immobilière", title_style))
    elements.append(Spacer(1, 6 * mm))

    elements.append(Paragraph(f"<b>Adresse :</b> {result.geocoding.adresse_normalisee}", body_style))
    elements.append(Paragraph(f"<b>Commune :</b> {result.geocoding.commune} ({result.geocoding.code_postal})", body_style))
    elements.append(Paragraph(f"<b>Date :</b> {result.date_estimation.strftime('%d/%m/%Y')}", body_style))
    elements.append(Spacer(1, 8 * mm))

    elements.append(Paragraph("Estimation de valeur", heading_style))

    prix_data = [
        ["Estimation basse", f"{result.prix_bas:,.0f} €".replace(",", " ")],
        ["Estimation médiane", f"{result.prix_median:,.0f} €".replace(",", " ")],
        ["Estimation haute", f"{result.prix_haut:,.0f} €".replace(",", " ")],
        ["Prix au m² médian", f"{result.prix_m2_median:,.0f} €/m²".replace(",", " ")],
        ["Indice de confiance", f"{result.confiance_pct:.0f} %"],
    ]
    prix_table = Table(prix_data, colWidths=[8 * cm, 6 * cm])
    prix_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8e8e8")),
        ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#d4edda")),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(prix_table)
    elements.append(Spacer(1, 6 * mm))

    elements.append(Paragraph("Caractéristiques du bien", heading_style))
    bien = result.bien
    caract_data = [
        ["Surface", f"{bien.surface_m2} m²"],
        ["Nombre de pièces", str(bien.nb_pieces)],
        ["Étage", str(bien.etage)],
        ["DPE", bien.dpe.value],
        ["État général", bien.etat.value.replace("_", " ").title()],
    ]
    if bien.annee_construction:
        caract_data.append(["Année de construction", str(bien.annee_construction)])
    extras = []
    if bien.balcon:
        extras.append("Balcon")
    if bien.terrasse:
        extras.append("Terrasse")
    if bien.parking:
        extras.append("Parking")
    if bien.cave:
        extras.append("Cave")
    if extras:
        caract_data.append(["Annexes", ", ".join(extras)])

    caract_table = Table(caract_data, colWidths=[6 * cm, 8 * cm])
    caract_table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(caract_table)
    elements.append(Spacer(1, 6 * mm))

    if result.facteurs_explicatifs:
        elements.append(Paragraph("Facteurs explicatifs", heading_style))
        for f in result.facteurs_explicatifs[:8]:
            signe = "+" if f["impact_pct"] > 0 else ""
            elements.append(Paragraph(
                f"• {f['description']} ({signe}{f['impact_pct']} %)", body_style
            ))
        elements.append(Spacer(1, 6 * mm))

    if result.comparables:
        elements.append(Paragraph(f"Transactions comparables ({result.nb_comparables} retenues)", heading_style))
        comp_header = ["Date", "Surface", "Prix", "€/m²", "Distance", "Score"]
        comp_rows = [comp_header]
        for c in result.comparables[:10]:
            comp_rows.append([
                c.date_mutation.strftime("%d/%m/%Y"),
                f"{c.surface_m2:.0f} m²",
                f"{c.prix:,.0f} €".replace(",", " "),
                f"{c.prix_m2:,.0f}".replace(",", " "),
                f"{c.distance_m:.0f} m",
                f"{c.score_similarite:.0%}",
            ])
        comp_table = Table(comp_rows, colWidths=[2.3 * cm] * 6)
        comp_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4472C4")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f2f2f2")]),
        ]))
        elements.append(comp_table)
        elements.append(Spacer(1, 6 * mm))

    elements.append(Paragraph("Méthodologie et limites", heading_style))
    elements.append(Paragraph(
        "Cette estimation repose sur une analyse des transactions immobilières enregistrées "
        "dans la base DVF (Demandes de Valeurs Foncières, DGFiP) et sur un modèle statistique "
        "hédonique. Elle ne constitue pas une expertise immobilière au sens réglementaire.",
        body_style,
    ))
    elements.append(Spacer(1, 3 * mm))
    elements.append(Paragraph(
        "Sources : DVF/DGFiP, Géoplateforme IGN, ADEME (DPE), OpenStreetMap, INSEE. "
        f"Données extraites le {date.today().strftime('%d/%m/%Y')}.",
        ParagraphStyle("Small", parent=body_style, fontSize=8, textColor=colors.grey),
    ))

    doc.build(elements)
    logger.info("Rapport PDF généré : %s", output_path)
    return output_path
