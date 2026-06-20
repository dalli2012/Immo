"""Calcul du score de confiance de l'estimation."""

from immo.models import Comparable


def compute_confidence(comparables: list[Comparable], stats: dict) -> float:
    """Score de confiance 0-100% basé sur quantité et qualité des comparables."""
    if not comparables:
        return 5.0

    count_score = min(len(comparables) / 15.0, 1.0) * 40

    median = stats.get("median_prix_m2", 0)
    std = stats.get("std_prix_m2", 0)
    if median > 0:
        cv = std / median
        dispersion_score = max(0, 1.0 - cv * 2) * 30
    else:
        dispersion_score = 0

    avg_similarite = sum(c.score_similarite for c in comparables) / len(comparables)
    quality_score = avg_similarite * 30

    return round(min(count_score + dispersion_score + quality_score, 100), 1)
