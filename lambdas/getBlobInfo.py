import json
from commom.dynamodb import DynamoDB
from commom.responses import Responses
from boto3.dynamodb.types import TypeDeserializer

def handler(event, context):
    responses = Responses()
    query_params = event['queryStringParameters']
    if not 'id' in query_params:
        return responses._400_response("id parameter not found. Please provide 'id' parameter on url query string")
    id = query_params['id']

    blob_response = get_blob(id)

    if blob_response['ResponseMetadata']['HTTPStatusCode'] != 200:
        return responses._500_response("Failed to retrieve data from database")

    body = from_dynamodb_to_dict(blob_response['Item'])
    
    response = {"statusCode": 200, "body": json.dumps(body)}

    return response

def get_blob(id):
    dynamo = DynamoDB()
    item_response = dynamo.get_item({'id': {'S': id}})
    return item_response

def from_dynamodb_to_dict(item):
    d = TypeDeserializer()
    image_data = {k: d.deserialize(value=v) for k, v in item.items()}
    new_labels = []
    labels_with_decimal = image_data['labels']
    for l in labels_with_decimal:
        new_labels.append({"Confidence": float(l['Confidence']), "label": l['label']})
    image_data['labels'] = new_labels
    return image_data