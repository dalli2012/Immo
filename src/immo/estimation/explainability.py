"""Explicabilité de l'estimation via analyse des facteurs contributifs."""

import logging

from immo.models import Amenites, BienInput, Comparable

logger = logging.getLogger(__name__)

FACTOR_LABELS = {
    "dpe": {
        "A": ("DPE classe A (excellent)", +5),
        "B": ("DPE classe B (très bon)", +3),
        "C": ("DPE classe C (bon)", +1),
        "D": ("DPE classe D (moyen)", -2),
        "E": ("DPE classe E (passable)", -5),
        "F": ("DPE classe F (mauvais)", -8),
        "G": ("DPE classe G (très mauvais)", -12),
    },
    "etat": {
        "neuf": ("État neuf", +8),
        "tres_bon": ("Très bon état", +4),
        "bon": ("Bon état", 0),
        "moyen": ("État moyen", -5),
        "a_renover": ("À rénover", -12),
    },
}


def explain_estimation(
    bien: BienInput,
    comparables: list[Comparable],
    amenites: Amenites | None = None,
) -> list[dict]:
    """Génère une liste de facteurs explicatifs en langage naturel."""
    facteurs = []

    dpe_info = FACTOR_LABELS["dpe"].get(bien.dpe.value)
    if dpe_info:
        label, impact = dpe_info
        facteurs.append({
            "facteur": label,
            "impact_pct": impact,
            "description": f"Le {label} {'valorise' if impact > 0 else 'pénalise'} "
            f"l'estimation d'environ {abs(impact)} %",
        })

    etat_info = FACTOR_LABELS["etat"].get(bien.etat.value)
    if etat_info:
        label, impact = etat_info
        if impact != 0:
            facteurs.append({
                "facteur": label,
                "impact_pct": impact,
                "description": f"L'{label.lower()} {'valorise' if impact > 0 else 'pénalise'} "
                f"le bien d'environ {abs(impact)} %",
            })

    if bien.etage >= 4 and (bien.ascenseur is None or bien.ascenseur):
        facteurs.append({
            "facteur": "Étage élevé avec ascenseur",
            "impact_pct": 3,
            "description": "Un étage élevé avec ascenseur offre luminosité et calme (+3 %)",
        })
    elif bien.etage >= 4 and bien.ascenseur is False:
        facteurs.append({
            "facteur": "Étage élevé sans ascenseur",
            "impact_pct": -5,
            "description": "Un étage élevé sans ascenseur est pénalisant (-5 %)",
        })
    elif bien.etage == 0:
        facteurs.append({
            "facteur": "Rez-de-chaussée",
            "impact_pct": -4,
            "description": "Le rez-de-chaussée est généralement moins valorisé (-4 %)",
        })

    extras = []
    if bien.balcon:
        extras.append(("Balcon", 2))
    if bien.terrasse:
        extras.append(("Terrasse", 4))
    if bien.parking:
        extras.append(("Parking", 3))
    if bien.cave:
        extras.append(("Cave", 1))
    for name, impact in extras:
        facteurs.append({
            "facteur": name,
            "impact_pct": impact,
            "description": f"La présence d'un(e) {name.lower()} valorise le bien (+{impact} %)",
        })

    if amenites:
        if amenites.distance_transport_m and amenites.distance_transport_m < 300:
            facteurs.append({
                "facteur": "Proximité transports",
                "impact_pct": 3,
                "description": f"Transport en commun à {int(amenites.distance_transport_m)} m (+3 %)",
            })
        elif amenites.distance_transport_m and amenites.distance_transport_m > 1000:
            facteurs.append({
                "facteur": "Éloignement transports",
                "impact_pct": -3,
                "description": "Transports en commun à plus de 1 km (-3 %)",
            })

    facteurs.sort(key=lambda f: abs(f["impact_pct"]), reverse=True)
    return facteurs
