import os
import zipfile
import boto3
import sys


# Set the S3 bucket and object path
S3_BUCKET_NAME = "aws-alerts-config-bucket"
S3_OBJECT_KEY = "/crypto_report/dependencies/lambda_dependencies.zip"
TMP_DIR = "/tmp"

# Download and unzip the dependencies
def download_and_unzip_dependencies():
    s3 = boto3.client("s3")

    # Download the dependencies zip file from S3
    s3.download_file(S3_BUCKET_NAME, S3_OBJECT_KEY, f"{TMP_DIR}/lambda_dependencies.zip")

    # Unzip the dependencies
    with zipfile.ZipFile(f"{TMP_DIR}/lambda_dependencies.zip", "r") as zip_ref:
        zip_ref.extractall(f"{TMP_DIR}/python")

    # Add the unzipped dependencies to the system path
    sys.path.append(f"{TMP_DIR}/python")

def handler(event, context):

    download_and_unzip_dependencies()

    from report.report import CryptoReport
    from mb_api.auth import MbAuthenticator

    mb_api_key = os.getenv('MB_ACCESS_KEY')
    mb_api_secret = os.getenv('MB_ACCESS_SECRET')
    if not mb_api_key or mb_api_secret:
        raise Exception('Registre manualmente as chaves nas variáveis de ambiente')
    auth = MbAuthenticator(login=mb_api_key, password=mb_api_secret)
    crypto_report = CryptoReport(mb_auth=auth)
    crypto_report.gen_report()

if __name__ == '__main__':
    handler('', '')