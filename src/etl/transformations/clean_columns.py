import pandas as pd

def clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nettoie un DataFrame en supprimant les colonnes inutiles pour l'analyse trafic.

    Args:
        df (pd.DataFrame): DataFrame brut   

    Returns:
        pd.DataFrame: DataFrame nettoyé
    """
    # Colonnes à supprimer
    columns_to_drop = [
        "Identifiant noeud amont",
        "Identifiant noeud aval",
        "geo_point_2d",
        "heure",
        "lat",
        "lon"
    ]

    # Suppression des colonnes inutiles (ne crée pas de copie si errors='ignore')
    existing_columns = [col for col in columns_to_drop if col in df.columns]
    if existing_columns:
        return df.drop(columns=existing_columns)
    
    return df
