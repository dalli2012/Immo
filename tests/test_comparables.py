"""Tests du scoring des comparables."""

from datetime import date, timedelta

from immo.estimation.comparables import analyse_comparables, score_and_sort, score_comparable
from immo.models import BienInput, Comparable


def _make_bien():
    return BienInput(adresse="test", surface_m2=60, nb_pieces=3, etage=2)


def _make_comparable(**kwargs):
    defaults = dict(
        date_mutation=date.today() - timedelta(days=90),
        prix=300000,
        surface_m2=60,
        prix_m2=5000,
        latitude=48.85,
        longitude=2.35,
        distance_m=200,
        score_similarite=0.0,
    )
    defaults.update(kwargs)
    return Comparable(**defaults)


def test_score_identical():
    bien = _make_bien()
    comp = _make_comparable(surface_m2=60, distance_m=0, nb_pieces=3)
    score = score_comparable(bien, comp)
    assert score > 0.8


def test_score_distant():
    bien = _make_bien()
    comp = _make_comparable(distance_m=1800)
    score = score_comparable(bien, comp)
    assert score < 0.75


def test_score_and_sort():
    bien = _make_bien()
    comps = [
        _make_comparable(distance_m=1500, surface_m2=80),
        _make_comparable(distance_m=100, surface_m2=58),
    ]
    sorted_comps = score_and_sort(bien, comps)
    assert sorted_comps[0].score_similarite > sorted_comps[1].score_similarite


def test_analyse_comparables():
    comps = [_make_comparable(prix_m2=5000), _make_comparable(prix_m2=5500)]
    stats = analyse_comparables(comps)
    assert stats["count"] == 2
    assert stats["median_prix_m2"] == 5250
