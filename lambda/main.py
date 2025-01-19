import json
import boto3

from report.report import CryptoReport
from mb_api.auth import MbAuthenticator


def handler(event, context):
    try:

        sqs_client = boto3.client('sqs', region_name='sa-east-1')
        try:
            ssm_client = boto3.client('ssm', region_name='sa-east-1')
            secrets = json.loads(ssm_client.get_parameter(Name="crypto_report_secrets")['Parameter']['Value'])

            queue_url = secrets['SQS_QUEUE_URL']

            mb_api_key = secrets['MB_ACCESS_KEY']
            mb_api_secret = secrets['MB_ACCESS_SECRET']

            whatsapp_api_id = secrets['WHATSAPP_API_ID']
            whatsapp_api_to = secrets['WHATSAPP_API_TO']
        except Exception as e:
            raise Exception(f'Registre manualmente as chaves nas variáveis de ambiente - {e}')

        auth = MbAuthenticator(login=mb_api_key, password=mb_api_secret)
        crypto_report = CryptoReport(mb_auth=auth)
        report_dict = crypto_report.gen_report()

        message = {
            "resource_name": "messages",
            "resource_args": {
                "id": whatsapp_api_id
            },
            "resource_function": "send_document_message",
            "resource_function_args": {
                "to": whatsapp_api_to,
                "base64_document": report_dict['pdf'],
                "document_filename": 'report.pdf',
                "caption": report_dict['text']
            }
        }
        print(json.dumps(message))

        sqs_client.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(message)
        )
        print("Message sent to SQS")
        return {'statusCode': 200}
    except Exception as e:
        return {'statusCode': 400, 'message': f'Error - {e}'}


if __name__ == '__main__':
    handler('', '')
