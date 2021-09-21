import json
from commom.dynamodb import DynamoDB
from commom.responses import Responses
from commom.blob_dynamo_deserializer import BlobDeserializer

def handler(event, context):
    responses = Responses()
    query_params = event['queryStringParameters']
    if type(query_params) != type(None):
        if not 'id' in query_params:
            return responses._400_response("id parameter not found. Please provide 'id' parameter on url query string")
    else:
        return responses._400_response("No query string parameter provided. Please provide 'id' parameter on url query string")

    id = query_params['id']
    blob_response = get_blob(id)
    
    if blob_response['ResponseMetadata']['HTTPStatusCode'] != 200:
        return responses._500_response("Failed to retrieve data from database")

    deserializer = BlobDeserializer()
    body = deserializer.deserialize_dynamo_blob(blob_response['Item'])
    
    response = {"statusCode": 200, "body": json.dumps(body)}

    return response

def get_blob(id):
    dynamo = DynamoDB()
    item_response = dynamo.get_item({'id': {'S': id}})
    return item_response
