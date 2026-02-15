import pandas as pd

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nettoie un DataFrame en :
    - supprimant les lignes contenant des valeurs manquantes
    - supprimant les lignes dupliquées
    - nettoyant les espaces dans les colonnes de type objet

    Args:
        df (pd.DataFrame): DataFrame brut

    Returns:
        pd.DataFrame: DataFrame nettoyé
    """
    # Supprimer toutes les lignes qui contiennent au moins une valeur manquante
    df_clean = df.dropna()
    
    # Supprimer les duplicatas
    df_clean = df_clean.drop_duplicates()
    
    # Nettoyer les espaces dans les colonnes texte (plus efficace que apply)
    str_columns = df_clean.select_dtypes(include=['object']).columns
    if len(str_columns) > 0:
        df_clean[str_columns] = df_clean[str_columns].apply(lambda x: x.str.strip() if x.dtype == 'object' else x)
    
    return df_clean
