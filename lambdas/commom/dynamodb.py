import os
import boto3

class DynamoDB:
    def __init__(self):
        self.dynamo_client = boto3.client('dynamodb')
        self.table_name = os.environ['tableName']

    def put_item(self, dynamo_item):
        #dynamo_item = {'id': {'S': id}, 'callback_url': {'S': callback_url}, 'image_file_name': {'S': image_file_name}}
        response = self.dynamo_client.put_item(TableName=self.table_name, Item=dynamo_item)
        return response