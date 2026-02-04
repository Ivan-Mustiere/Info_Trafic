import pandas as pd

def clean_date(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforme la colonne 'Date et heure de comptage' pour ne conserver que l'heure.

    Args:
        df (pd.DataFrame): DataFrame brut

    Returns:
        pd.DataFrame: DataFrame avec la colonne 'Date et heure de comptage' transformée
    """
    df = df.copy()  # éviter de modifier l'original

    if "Date et heure de comptage" in df.columns:
        df["Date et heure de comptage"] = pd.to_datetime(
            df["Date et heure de comptage"], errors="coerce"
        ).dt.hour

    return df
