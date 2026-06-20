"""Configuration centralisée de l'application."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    geocoding_base_url: str = "https://data.geopf.fr/geocodage/search"
    geocoding_timeout: int = 10

    dvf_base_url: str = "https://apidf-preprod.cerema.fr"
    dvf_timeout: int = 30

    dpe_base_url: str = (
        "https://data.ademe.fr/data-fair/api/v1/datasets/dpe-v2-logements-existants/lines"
    )
    dpe_timeout: int = 15

    geo_api_base_url: str = "https://geo.api.gouv.fr"
    geo_api_timeout: int = 10

    overpass_base_url: str = "https://overpass-api.de/api/interpreter"
    overpass_timeout: int = 30

    database_path: Path = Field(default=Path("data/immo_cache.db"))
    model_path: Path = Field(default=Path("data/models/model_latest.pkl"))

    default_search_radius_m: int = 500
    max_search_radius_m: int = 2000
    comparable_months: int = 36
    surface_tolerance_pct: float = 0.30
    min_comparables: int = 3


settings = Settings()
