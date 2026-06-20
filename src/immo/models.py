"""Modèles de données Pydantic partagés entre les modules."""

from datetime import date
from enum import Enum

from pydantic import BaseModel, Field


class DPEClass(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    F = "F"
    G = "G"
    UNKNOWN = "N/C"


class EtatGeneral(str, Enum):
    NEUF = "neuf"
    TRES_BON = "tres_bon"
    BON = "bon"
    MOYEN = "moyen"
    A_RENOVER = "a_renover"


class BienInput(BaseModel):
    """Caractéristiques du bien saisies par l'utilisateur."""

    adresse: str
    surface_m2: float = Field(gt=0)
    nb_pieces: int = Field(ge=1)
    etage: int = Field(ge=0)
    nb_etages_immeuble: int | None = None
    ascenseur: bool | None = None
    annee_construction: int | None = None
    dpe: DPEClass = DPEClass.UNKNOWN
    etat: EtatGeneral = EtatGeneral.BON
    balcon: bool = False
    terrasse: bool = False
    parking: bool = False
    cave: bool = False


class GeocodingResult(BaseModel):
    """Résultat du géocodage d'une adresse."""

    latitude: float
    longitude: float
    code_insee: str
    commune: str
    code_postal: str
    adresse_normalisee: str
    score: float = Field(ge=0, le=1)


class Comparable(BaseModel):
    """Transaction comparable issue de DVF."""

    date_mutation: date
    prix: float
    surface_m2: float
    prix_m2: float
    nb_pieces: int | None = None
    etage: int | None = None
    latitude: float
    longitude: float
    distance_m: float
    score_similarite: float = Field(ge=0, le=1)
    adresse: str = ""
    code_postal: str = ""
    commune: str = ""


class DPEInfo(BaseModel):
    """Information DPE issue de la base ADEME."""

    classe_dpe: DPEClass
    classe_ges: DPEClass | None = None
    date_etablissement: date | None = None
    adresse: str = ""


class Amenites(BaseModel):
    """Aménités à proximité du bien (OSM)."""

    distance_transport_m: float | None = None
    distance_ecole_m: float | None = None
    distance_commerce_m: float | None = None
    distance_espace_vert_m: float | None = None
    nb_transports_500m: int = 0
    nb_commerces_500m: int = 0


class ContexteINSEE(BaseModel):
    """Indicateurs socio-économiques du quartier."""

    revenu_median: float | None = None
    densite_population: float | None = None
    code_iris: str | None = None


class EstimationResult(BaseModel):
    """Résultat complet d'une estimation."""

    prix_bas: float
    prix_median: float
    prix_haut: float
    prix_m2_median: float
    confiance_pct: float = Field(ge=0, le=100)
    nb_comparables: int
    facteurs_explicatifs: list[dict] = Field(default_factory=list)
    bien: BienInput
    geocoding: GeocodingResult
    comparables: list[Comparable] = Field(default_factory=list)
    amenites: Amenites | None = None
    date_estimation: date = Field(default_factory=date.today)
