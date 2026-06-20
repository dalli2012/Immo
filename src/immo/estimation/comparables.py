"""Scoring et analyse des comparables."""

from datetime import date

import numpy as np

from immo.models import BienInput, Comparable


def score_comparable(bien: BienInput, comp: Comparable) -> float:
    """Calcule un score de similarité [0, 1] entre le bien et un comparable."""
    scores = []

    surface_diff = abs(bien.surface_m2 - comp.surface_m2) / bien.surface_m2
    scores.append(max(0, 1.0 - surface_diff * 2))

    dist_score = max(0, 1.0 - comp.distance_m / 2000)
    scores.append(dist_score)

    jours = (date.today() - comp.date_mutation).days
    temps_score = max(0, 1.0 - jours / (36 * 30))
    scores.append(temps_score)

    if comp.nb_pieces and bien.nb_pieces:
        pieces_diff = abs(bien.nb_pieces - comp.nb_pieces)
        scores.append(max(0, 1.0 - pieces_diff * 0.25))

    weights = [0.35, 0.25, 0.25, 0.15] if len(scores) == 4 else [0.4, 0.3, 0.3]
    return round(sum(s * w for s, w in zip(scores, weights)), 3)


def score_and_sort(bien: BienInput, comparables: list[Comparable]) -> list[Comparable]:
    """Score tous les comparables et retourne la liste triée par similarité décroissante."""
    for comp in comparables:
        comp.score_similarite = score_comparable(bien, comp)
    return sorted(comparables, key=lambda c: c.score_similarite, reverse=True)


def analyse_comparables(comparables: list[Comparable]) -> dict:
    """Analyse statistique des comparables scorés."""
    if not comparables:
        return {"median_prix_m2": 0, "mean_prix_m2": 0, "std_prix_m2": 0, "count": 0}

    prix_m2 = [c.prix_m2 for c in comparables]
    poids = [c.score_similarite for c in comparables]
    total_poids = sum(poids) or 1.0

    weighted_avg = sum(p * w for p, w in zip(prix_m2, poids)) / total_poids

    return {
        "median_prix_m2": float(np.median(prix_m2)),
        "mean_prix_m2": float(np.mean(prix_m2)),
        "weighted_avg_prix_m2": round(weighted_avg, 2),
        "std_prix_m2": float(np.std(prix_m2)),
        "min_prix_m2": min(prix_m2),
        "max_prix_m2": max(prix_m2),
        "count": len(comparables),
    }
