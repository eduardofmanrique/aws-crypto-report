import os
import json
import base64
import boto3

from report.report import CryptoReport
from mb_api.auth import MbAuthenticator

# SQS client
sqs_client = boto3.client('sqs', region_name='sa-east-1')

# Define the queue URL
queue_url = os.getenv('SQS_QUEUE_URL')

mb_api_key = os.getenv('MB_ACCESS_KEY')
mb_api_secret = os.getenv('MB_ACCESS_SECRET')

whatsapp_api_id = os.getenv('WHATSAPP_API_ID')
whatsapp_api_to = os.getenv('WHATSAPP_API_TO')

if (
        not mb_api_key or
        not mb_api_secret or
        not queue_url or
        not whatsapp_api_id or
        not whatsapp_api_to
):
    raise Exception('Registre manualmente as chaves nas variáveis de ambiente')

def handler(event, context):

    auth = MbAuthenticator(login=mb_api_key, password=mb_api_secret)
    crypto_report = CryptoReport(mb_auth=auth)
    report_dict = crypto_report.gen_report()

    message = {
        "resource_name": "messages",
        "resource_args": {
            "id": whatsapp_api_id
        },
        "resource_function": "send_template_message",
        "resource_function_args": {
            "to": whatsapp_api_to,
            "template_name": "crypto_report",
            "template_language": "en",
            "base64_document": report_dict['pdf'],
            "variables": [{
                "type": "text",
                "text": report_dict['text']
            }]
        }
    }
    print(json.dumps(message))

    sqs_client.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(message)
    )
    print("Message sent to SQS")


if __name__ == '__main__':
    pass
