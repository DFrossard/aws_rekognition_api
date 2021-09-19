import os
import boto3

class DynamoDB:
    def __init__(self):
        self.dynamo_client = boto3.client('dynamodb')
        self.table_name = os.environ['tableName']

    def get_item(self, key):
        response = self.dynamo_client.get_item(TableName=self.table_name, Key=key)
        return response

    def put_item(self, dynamo_item):
        response = self.dynamo_client.put_item(TableName=self.table_name, Item=dynamo_item)
        return response