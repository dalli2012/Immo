"""Tests du calcul de confiance."""

from datetime import date

from immo.estimation.confidence import compute_confidence
from immo.models import Comparable


def _comp(score=0.7, prix_m2=5000):
    return Comparable(
        date_mutation=date.today(), prix=prix_m2 * 50, surface_m2=50,
        prix_m2=prix_m2, latitude=48.85, longitude=2.35,
        distance_m=200, score_similarite=score,
    )


def test_no_comparables():
    assert compute_confidence([], {}) == 5.0


def test_many_similar_comparables():
    comps = [_comp(score=0.9, prix_m2=5000) for _ in range(15)]
    stats = {"median_prix_m2": 5000, "std_prix_m2": 100}
    conf = compute_confidence(comps, stats)
    assert conf > 80


def test_few_dispersed_comparables():
    comps = [_comp(score=0.3, prix_m2=p) for p in [3000, 7000]]
    stats = {"median_prix_m2": 5000, "std_prix_m2": 2000}
    conf = compute_confidence(comps, stats)
    assert conf < 40
