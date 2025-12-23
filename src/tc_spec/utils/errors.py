"""
TC Insight – Exceptions métier

Ce module définit l'ensemble des exceptions utilisées dans le
générateur de Specs TC Insight (V2).
"""

class SpecError(Exception):
    """
    Exception racine du générateur TC Insight.
    """
    pass
class ExcelValidationError(SpecError):
    """
    Erreur levée lorsque le fichier Excel est invalide
    (structure, cohérence, ambiguïté).
    """
    pass
class BuilderError(SpecError):
    """
    Erreur levée lors de la construction du modèle métier
    à partir des données Excel.
    """
    pass
class ModelError(SpecError):
    """
    Erreur levée lorsqu'un objet du modèle métier
    est invalide ou incohérent.
    """
    pass
class SchemaValidationError(SpecError):
    """
    Erreur levée lorsque le Spec généré ne respecte pas
    le JSON Schema officiel.
    """
    pass
class ExportError(SpecError):
    """
    Erreur levée lors de l'export du Spec (JSON, futur formats).
    """
    pass
