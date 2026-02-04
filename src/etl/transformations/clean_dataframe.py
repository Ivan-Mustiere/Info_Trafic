import pandas as pd

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nettoie un DataFrame en :
    - supprimant les lignes contenant des valeurs manquantes
    - supprimant les espaces en début et fin pour les colonnes texte

    Args:
        df (pd.DataFrame): DataFrame brut

    Returns:
        pd.DataFrame: DataFrame nettoyé
    """
    df = df.copy()  # éviter de modifier l'original

    # Supprimer toutes les lignes qui contiennent au moins une valeur manquante
    df.dropna(inplace=True)


    return df
