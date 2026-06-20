"""Tests des modèles de données."""

from datetime import date

import pytest

from immo.models import BienInput, Comparable, DPEClass, EtatGeneral, EstimationResult, GeocodingResult


def test_bien_input_minimal():
    bien = BienInput(adresse="1 rue Test, Paris", surface_m2=50, nb_pieces=2, etage=3)
    assert bien.surface_m2 == 50
    assert bien.dpe == DPEClass.UNKNOWN
    assert bien.etat == EtatGeneral.BON


def test_bien_input_validation():
    with pytest.raises(Exception):
        BienInput(adresse="test", surface_m2=-1, nb_pieces=2, etage=0)


def test_comparable():
    c = Comparable(
        date_mutation=date(2025, 6, 1),
        prix=300000,
        surface_m2=60,
        prix_m2=5000,
        latitude=48.85,
        longitude=2.35,
        distance_m=200,
        score_similarite=0.8,
    )
    assert c.prix_m2 == 5000


def test_geocoding_result():
    g = GeocodingResult(
        latitude=48.85,
        longitude=2.35,
        code_insee="75101",
        commune="Paris",
        code_postal="75001",
        adresse_normalisee="1 Rue Test, 75001 Paris",
        score=0.95,
    )
    assert g.code_insee == "75101"
