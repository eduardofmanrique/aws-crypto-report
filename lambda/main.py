import pandas as pd


def handler(event, context):
    print(pd.DataFrame(
        {
            'A': [1,2,3],
            'B': [3,4,5]
        }
    ))
    return {
        'statusCode': 200,
        'body': 'Dummy Lambda function executed! From git'
    }

if __name__ == '__main__':
    handler('', '')