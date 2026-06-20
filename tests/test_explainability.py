"""Tests de l'explicabilité."""

from immo.estimation.explainability import explain_estimation
from immo.models import Amenites, BienInput, DPEClass, EtatGeneral


def test_explain_dpe_penalite():
    bien = BienInput(
        adresse="test", surface_m2=50, nb_pieces=2, etage=1,
        dpe=DPEClass.F, etat=EtatGeneral.BON,
    )
    facteurs = explain_estimation(bien, [])
    dpe_f = [f for f in facteurs if "DPE" in f["facteur"]]
    assert len(dpe_f) == 1
    assert dpe_f[0]["impact_pct"] < 0


def test_explain_extras():
    bien = BienInput(
        adresse="test", surface_m2=50, nb_pieces=2, etage=1,
        balcon=True, parking=True,
    )
    facteurs = explain_estimation(bien, [])
    names = [f["facteur"] for f in facteurs]
    assert "Balcon" in names
    assert "Parking" in names
