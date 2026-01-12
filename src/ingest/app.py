import os
import shutil

def fetch_dataset(dataset_name="dossier.csv"):
    """
    Récupère le dataset selon l'environnement :
    - En prod : le chercher sur AWS S3
    - En preprod : vérifier sa présence dans data/, le déplacer/copier dans raw/
    """
    env = os.environ.get("ENV", "preprod").lower()
    if env == "PROD":
        import boto3
        s3 = boto3.client("s3")
        bucket_name = os.environ.get("DATA_BUCKET", "my-bucket")
        local_path = os.path.join("raw", dataset_name)
        try:
            s3.download_file(bucket_name, dataset_name, local_path)
            print(f"✅ Dataset récupéré depuis S3 ({bucket_name}/{dataset_name})")
        except Exception as e:
            print(f"❌ Erreur lors du téléchargement depuis S3: {e}")
    elif env == "PREPROD":
        dest_path = os.path.join("raw", dataset_name)
        if os.path.exists(dest_path):
            print(f"✅ Le fichier {dest_path} existe dans raw/")
        else:
            print(f"❌ Fichier {dest_path} introuvable dans raw/.")
    else:
        print("⚠️ ENV non reconnu. Valeurs attendues : 'prod' ou 'preprod'.")
    return dest_path

if __name__ == "__main__":
    fetch_dataset()