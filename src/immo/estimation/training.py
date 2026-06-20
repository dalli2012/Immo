"""Pipeline d'entraînement du modèle de prédiction du prix au m²."""

import logging
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import cross_val_score

from immo.config import settings

logger = logging.getLogger(__name__)

FEATURE_COLUMNS = [
    "surface_m2",
    "nb_pieces",
    "etage",
    "etage_relatif",
    "ascenseur",
    "dpe_ordinal",
    "etat_ordinal",
    "balcon",
    "terrasse",
    "parking",
    "cave",
    "prix_m2_median_local",
    "prix_m2_std_local",
    "nb_comparables",
    "anciennete",
    "distance_transport_m",
    "distance_ecole_m",
    "distance_commerce_m",
    "distance_espace_vert_m",
    "nb_transports_500m",
    "nb_commerces_500m",
    "densite_population",
]

TARGET_COLUMN = "prix_m2"


def train_model(
    df: pd.DataFrame,
    output_path: Path | None = None,
) -> dict:
    """Entraîne un GradientBoosting sur le jeu de données et sauvegarde le modèle."""
    output = output_path or settings.model_path
    output.parent.mkdir(parents=True, exist_ok=True)

    available_features = [c for c in FEATURE_COLUMNS if c in df.columns]
    X = df[available_features].fillna(0)
    y = df[TARGET_COLUMN]

    model = GradientBoostingRegressor(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.1,
        subsample=0.8,
        random_state=42,
    )

    cv_scores = cross_val_score(model, X, y, cv=5, scoring="neg_mean_absolute_error")
    logger.info("CV MAE: %.2f ± %.2f", -cv_scores.mean(), cv_scores.std())

    model.fit(X, y)
    y_pred = model.predict(X)

    metrics = {
        "mae": round(mean_absolute_error(y, y_pred), 2),
        "rmse": round(np.sqrt(mean_squared_error(y, y_pred)), 2),
        "r2": round(r2_score(y, y_pred), 4),
        "cv_mae": round(-cv_scores.mean(), 2),
        "cv_mae_std": round(cv_scores.std(), 2),
        "n_samples": len(df),
        "features_used": available_features,
    }

    joblib.dump(model, output)
    logger.info("Modèle sauvegardé : %s", output)
    logger.info("Métriques : %s", metrics)

    return metrics
