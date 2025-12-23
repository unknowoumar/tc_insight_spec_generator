"""
TC Insight – Helpers utilitaires

Fonctions utilitaires partagées par l'ensemble du projet.
Aucune logique métier ne doit apparaître ici.
"""

from typing import Any, Iterable, List, Optional

def normalize_str(value: Any) -> Optional[str]:
    """
    Convertit une valeur en string normalisée.
    Retourne None si la valeur est vide ou NaN.
    """
    if value is None:
        return None

    if isinstance(value, float) and value != value:  # NaN
        return None

    s = str(value).strip()
    return s if s else None

def safe_int(value: Any, field_name: str = "") -> Optional[int]:
    """
    Convertit une valeur en int de manière sûre.
    Retourne None si la valeur est vide.
    """
    if value is None:
        return None

    try:
        return int(value)
    except Exception:
        raise ValueError(
            f"Invalid integer value for {field_name}: {value}"
        )

def safe_number(value: Any, field_name: str = "") -> Optional[float]:
    """
    Convertit une valeur en nombre (float).
    """
    if value is None:
        return None

    try:
        return float(value)
    except Exception:
        raise ValueError(
            f"Invalid numeric value for {field_name}: {value}"
        )

def parse_csv(value: Any) -> List[str]:
    """
    Parse une chaîne CSV simple en liste de strings.
    """
    if value is None:
        return []

    if not isinstance(value, str):
        return []

    return [
        v.strip()
        for v in value.split(",")
        if v.strip()
    ]

def has_duplicates(values: Iterable[Any]) -> bool:
    """
    Retourne True si des doublons sont présents.
    """
    seen = set()
    for v in values:
        if v in seen:
            return True
        seen.add(v)
    return False

def clean_dict(data: dict) -> dict:
    """
    Supprime les clés avec des valeurs None.
    """
    return {
        k: v
        for k, v in data.items()
        if v is not None
    }
