import pandas as pd

def clean_date(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforme la colonne 'Date et heure de comptage' pour extraire l'heure.

    Args:
        df (pd.DataFrame): DataFrame brut

    Returns:
        pd.DataFrame: DataFrame avec la colonne 'Heure de comptage' extraite
    """
    if "Date et heure de comptage" not in df.columns:
        return df
    
    # Conversion optimisée avec cache
    df_result = df.copy()
    df_result["Heure de comptage"] = pd.to_datetime(
        df_result["Date et heure de comptage"], 
        errors="coerce",
        cache=True  # Cache les conversions pour améliorer les performances
    ).dt.hour
    
    # Supprimer la colonne d'origine
    df_result = df_result.drop(columns=["Date et heure de comptage"])
    
    return df_result
