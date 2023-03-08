import boto3


class SSMReader:
    def __init__(self):
        self.client = boto3.client('ssm')

    def read(self, name: str) -> str:
        response = self.client.get_parameter(Name=name, WithDecryption=True)
        return response['Parameter']['Value']
