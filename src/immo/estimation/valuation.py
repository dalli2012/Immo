"""Moteur d'estimation hybride : modèle ML + comparables."""

import logging
from pathlib import Path

import joblib
import numpy as np

from immo.config import settings
from immo.estimation.comparables import analyse_comparables, score_and_sort
from immo.estimation.confidence import compute_confidence
from immo.estimation.feature_engineering import build_features, features_to_dataframe
from immo.models import Amenites, BienInput, Comparable, ContexteINSEE, EstimationResult, GeocodingResult

logger = logging.getLogger(__name__)


def _load_model():
    model_path = settings.model_path
    if model_path.exists():
        return joblib.load(model_path)
    return None


def estimate(
    bien: BienInput,
    geocoding: GeocodingResult,
    comparables: list[Comparable],
    amenites: Amenites | None = None,
    contexte: ContexteINSEE | None = None,
) -> EstimationResult:
    """Produit une estimation hybride du bien."""
    comparables_scored = score_and_sort(bien, comparables)
    stats = analyse_comparables(comparables_scored)

    features = build_features(bien, comparables_scored, amenites, contexte)

    model = _load_model()
    ml_prix_m2 = None
    if model is not None:
        try:
            df = features_to_dataframe(features)
            ml_prix_m2 = float(model.predict(df)[0])
        except Exception:
            logger.warning("Erreur prédiction modèle ML", exc_info=True)

    comp_prix_m2 = stats["weighted_avg_prix_m2"] if stats["count"] > 0 else None

    if ml_prix_m2 and comp_prix_m2:
        density_weight = min(stats["count"] / 10.0, 0.7)
        model_weight = 1.0 - density_weight
        prix_m2_median = ml_prix_m2 * model_weight + comp_prix_m2 * density_weight
    elif comp_prix_m2:
        prix_m2_median = comp_prix_m2
    elif ml_prix_m2:
        prix_m2_median = ml_prix_m2
    else:
        raise ValueError("Impossible d'estimer : aucun comparable ni modèle disponible.")

    ecart_type = stats["std_prix_m2"] if stats["count"] > 1 else prix_m2_median * 0.10

    prix_median = round(prix_m2_median * bien.surface_m2)
    prix_bas = round((prix_m2_median - ecart_type) * bien.surface_m2)
    prix_haut = round((prix_m2_median + ecart_type) * bien.surface_m2)

    prix_bas = max(prix_bas, int(prix_median * 0.75))
    prix_haut = min(prix_haut, int(prix_median * 1.35))

    confiance = compute_confidence(comparables_scored, stats)

    return EstimationResult(
        prix_bas=prix_bas,
        prix_median=prix_median,
        prix_haut=prix_haut,
        prix_m2_median=round(prix_m2_median, 2),
        confiance_pct=confiance,
        nb_comparables=stats["count"],
        bien=bien,
        geocoding=geocoding,
        comparables=comparables_scored[:10],
        amenites=amenites,
    )
