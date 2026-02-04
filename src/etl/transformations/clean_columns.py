import pandas as pd

def clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nettoie un DataFrame en :
    - supprimant les lignes contenant des valeurs manquantes
    - supprimant les colonnes inutiles pour l'analyse trafic

    Args:
        df (pd.DataFrame): DataFrame brut   

    Returns:
        pd.DataFrame: DataFrame nettoyé
    """
    df = df.copy()

    # Colonnes à supprimer
    columns_to_drop = [
        "Identifiant noeud amont",
        "Identifiant noeud aval",
        "geo_point_2d",
        "heure",
        "lat",
        "lon"
    ]

    # Suppression des colonnes inutiles
    df.drop(columns=columns_to_drop, inplace=True, errors="ignore")
    

    return df
