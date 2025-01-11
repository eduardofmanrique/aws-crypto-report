import os
import zipfile
import boto3
import sys

local_env = os.getenv('LOCAL_ENV')

# Set the S3 bucket and object path
S3_BUCKET_NAME = "aws-alerts-config-bucket"
S3_OBJECT_KEY = "crypto_report/dependencies/lambda_dependencies.zip"
TMP_DIR = "tmp" if local_env else "/tmp"
DEPENDENCIES_ZIP_PATH = f"{TMP_DIR}/lambda_dependencies.zip"
DEPENDENCIES_DIR_PATH = f"{TMP_DIR}/python"

# Download and unzip the dependencies
def download_and_unzip_dependencies():
    # If dependencies are already unzipped, skip the download process
    if not os.path.exists(DEPENDENCIES_DIR_PATH):
        s3 = boto3.client("s3")

        print(f"Downloading {S3_OBJECT_KEY} from S3 to {DEPENDENCIES_ZIP_PATH}...")
        s3.download_file(S3_BUCKET_NAME, S3_OBJECT_KEY, DEPENDENCIES_ZIP_PATH)
        print(f"Downloaded {S3_OBJECT_KEY} from S3 to {DEPENDENCIES_ZIP_PATH}")

        print("Unziping...")
        with zipfile.ZipFile(DEPENDENCIES_ZIP_PATH, "r") as zip_ref:
            zip_ref.extractall(f"{TMP_DIR}")
        print("Unziped")

    else:
        print("Dependencies already exist, skipping download.")

def handler(event, context):

    download_and_unzip_dependencies()
    sys.path.append(DEPENDENCIES_DIR_PATH)

    from report.report import CryptoReport
    from mb_api.auth import MbAuthenticator

    mb_api_key = os.getenv('MB_ACCESS_KEY')
    mb_api_secret = os.getenv('MB_ACCESS_SECRET')
    if not mb_api_key or not mb_api_secret:
        raise Exception('Registre manualmente as chaves nas variáveis de ambiente')
    auth = MbAuthenticator(login=mb_api_key, password=mb_api_secret)
    crypto_report = CryptoReport(mb_auth=auth)
    crypto_report.gen_report()

if __name__ == '__main__':
    handler('', '')
