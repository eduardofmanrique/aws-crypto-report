import os

from report.report import CryptoReport
from mb_api.auth import MbAuthenticator

def handler(event, context):

    mb_api_key = os.getenv('MB_ACCESS_KEY')
    mb_api_secret = os.getenv('MB_ACCESS_SECRET')
    if not mb_api_key or not mb_api_secret:
        raise Exception('Registre manualmente as chaves nas variáveis de ambiente')
    auth = MbAuthenticator(login=mb_api_key, password=mb_api_secret)
    crypto_report = CryptoReport(mb_auth=auth)
    report_dict = crypto_report.gen_report()
    print(report_dict)
    print(type(report_dict['pdf']))

if __name__ == '__main__':
    handler('', '')
