"""Tests du feature engineering."""

from datetime import date

from immo.estimation.feature_engineering import build_features
from immo.models import Amenites, BienInput, Comparable, DPEClass


def test_build_features_basic():
    bien = BienInput(adresse="test", surface_m2=50, nb_pieces=2, etage=3)
    features = build_features(bien, [])
    assert features["surface_m2"] == 50
    assert features["nb_pieces"] == 2
    assert features["etage"] == 3
    assert "dpe_ordinal" in features


def test_build_features_with_comparables():
    bien = BienInput(adresse="test", surface_m2=50, nb_pieces=2, etage=3)
    comps = [
        Comparable(
            date_mutation=date.today(), prix=250000, surface_m2=50,
            prix_m2=5000, latitude=48.85, longitude=2.35,
            distance_m=100, score_similarite=0.9,
        ),
    ]
    features = build_features(bien, comps)
    assert features["prix_m2_median_local"] == 5000
    assert features["nb_comparables"] == 1


def test_build_features_with_amenites():
    bien = BienInput(adresse="test", surface_m2=50, nb_pieces=2, etage=3)
    amenites = Amenites(distance_transport_m=150, nb_transports_500m=5)
    features = build_features(bien, [], amenites)
    assert features["distance_transport_m"] == 150
    assert features["nb_transports_500m"] == 5
