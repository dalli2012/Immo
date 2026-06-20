"""Orchestrateur du pipeline d'estimation."""

import logging

from immo.data.dpe import fetch_dpe_by_address
from immo.data.dvf import fetch_with_expanding_radius
from immo.data.geocoding import geocode
from immo.data.insee import fetch_contexte_insee
from immo.data.osm import fetch_amenites
from immo.data.persistence import db
from immo.estimation.explainability import explain_estimation
from immo.estimation.valuation import estimate
from immo.models import BienInput, EstimationResult

logger = logging.getLogger(__name__)


def run_estimation(bien: BienInput, save: bool = True) -> EstimationResult:
    """Pipeline complet d'estimation d'un bien."""
    logger.info("Géocodage de l'adresse : %s", bien.adresse)
    geo = geocode(bien.adresse)
    logger.info("Adresse géocodée : %s (score=%.2f)", geo.adresse_normalisee, geo.score)

    logger.info("Récupération des transactions DVF...")
    comparables = fetch_with_expanding_radius(
        code_insee=geo.code_insee,
        lat=geo.latitude,
        lon=geo.longitude,
        surface_ref=bien.surface_m2,
    )
    logger.info("%d comparables trouvés", len(comparables))

    logger.info("Enrichissement DPE...")
    try:
        dpe_list = fetch_dpe_by_address(geo.code_insee, geo.adresse_normalisee)
        if dpe_list and bien.dpe.value == "N/C":
            bien.dpe = dpe_list[0].classe_dpe
            logger.info("DPE enrichi depuis ADEME : %s", bien.dpe.value)
    except Exception:
        logger.debug("Enrichissement DPE échoué", exc_info=True)

    logger.info("Récupération des aménités OSM...")
    try:
        amenites = fetch_amenites(geo.latitude, geo.longitude)
    except Exception:
        logger.debug("Aménités OSM non disponibles", exc_info=True)
        amenites = None

    logger.info("Récupération du contexte INSEE...")
    try:
        contexte = fetch_contexte_insee(geo.code_insee)
    except Exception:
        logger.debug("Contexte INSEE non disponible", exc_info=True)
        contexte = None

    logger.info("Calcul de l'estimation...")
    result = estimate(bien, geo, comparables, amenites, contexte)

    result.facteurs_explicatifs = explain_estimation(bien, comparables, amenites)

    if save:
        est_id = db.save_estimation(result)
        logger.info("Estimation sauvegardée (id=%d)", est_id)

    return result
