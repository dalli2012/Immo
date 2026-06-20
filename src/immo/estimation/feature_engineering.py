"""Transformation des données brutes en vecteur de variables pour le modèle."""

import numpy as np
import pandas as pd

from immo.models import Amenites, BienInput, Comparable, ContexteINSEE, DPEClass, EtatGeneral

DPE_ORDINAL = {"A": 7, "B": 6, "C": 5, "D": 4, "E": 3, "F": 2, "G": 1, "N/C": 3}
ETAT_ORDINAL = {"neuf": 5, "tres_bon": 4, "bon": 3, "moyen": 2, "a_renover": 1}


def build_features(
    bien: BienInput,
    comparables: list[Comparable],
    amenites: Amenites | None = None,
    contexte: ContexteINSEE | None = None,
) -> dict[str, float]:
    """Construit le dictionnaire de features pour le modèle d'estimation."""
    prix_m2_comparables = [c.prix_m2 for c in comparables] if comparables else []
    prix_m2_median = float(np.median(prix_m2_comparables)) if prix_m2_comparables else 0.0
    prix_m2_std = float(np.std(prix_m2_comparables)) if len(prix_m2_comparables) > 1 else 0.0

    features = {
        "surface_m2": bien.surface_m2,
        "nb_pieces": float(bien.nb_pieces),
        "etage": float(bien.etage),
        "etage_relatif": (
            bien.etage / bien.nb_etages_immeuble
            if bien.nb_etages_immeuble and bien.nb_etages_immeuble > 0
            else 0.5
        ),
        "ascenseur": float(bien.ascenseur) if bien.ascenseur is not None else 0.5,
        "dpe_ordinal": float(DPE_ORDINAL.get(bien.dpe.value, 3)),
        "etat_ordinal": float(ETAT_ORDINAL.get(bien.etat.value, 3)),
        "balcon": float(bien.balcon),
        "terrasse": float(bien.terrasse),
        "parking": float(bien.parking),
        "cave": float(bien.cave),
        "prix_m2_median_local": prix_m2_median,
        "prix_m2_std_local": prix_m2_std,
        "nb_comparables": float(len(comparables)),
    }

    if bien.annee_construction:
        features["anciennete"] = float(2026 - bien.annee_construction)
    else:
        features["anciennete"] = 30.0

    if amenites:
        features["distance_transport_m"] = amenites.distance_transport_m or 1000.0
        features["distance_ecole_m"] = amenites.distance_ecole_m or 1000.0
        features["distance_commerce_m"] = amenites.distance_commerce_m or 500.0
        features["distance_espace_vert_m"] = amenites.distance_espace_vert_m or 500.0
        features["nb_transports_500m"] = float(amenites.nb_transports_500m)
        features["nb_commerces_500m"] = float(amenites.nb_commerces_500m)
    else:
        features.update({
            "distance_transport_m": 1000.0,
            "distance_ecole_m": 1000.0,
            "distance_commerce_m": 500.0,
            "distance_espace_vert_m": 500.0,
            "nb_transports_500m": 0.0,
            "nb_commerces_500m": 0.0,
        })

    if contexte and contexte.densite_population:
        features["densite_population"] = contexte.densite_population
    else:
        features["densite_population"] = 1000.0

    return features


def features_to_dataframe(features: dict[str, float]) -> pd.DataFrame:
    """Convertit le dictionnaire de features en DataFrame pour le modèle."""
    return pd.DataFrame([features])
