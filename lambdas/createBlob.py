import os
import uuid
import json
import logging
import boto3
import re
from botocore.exceptions import ClientError

def handler(event, context):
    logging.info("Starting createBlob")
    try:
        body = json.loads(event['body'])
        image_file_name = body['image_file_name']
    except KeyError:
        return _400_response("Field image_file_name not detected in request body")
    except:
        return _400_response('Invalid request body. Please use {"callback_uri": your_callback_url, "image_file_name": your_image_file_name}')
    
    is_valid = validate_image_file_name(image_file_name)
    if not is_valid:
        return _400_response("Field image_file_name is invalid. Must end with .jpg, .png, .jpeg")

    if "callback_url" in body.keys():
        callback_url = body['callback_url']
    else:
        callback_url = ""

    id = generate_unique_id()
    img_bucket_path = id + '/' + image_file_name
    bucket = os.environ['bucketName']

    presign_url = create_presigned_post(bucket, img_bucket_path)

    dynamo = DynamoDB()
    dynamo_response = dynamo.put_object(id, callback_url, image_file_name)

    response_status_code = dynamo_response['ResponseMetadata']['HTTPStatusCode']
    if response_status_code != 200:
        return _500_response("Failed to save to database.")

    message = "Created blob"
    return _200_response(message, id, image_file_name, presign_url)

def create_presigned_post(bucket_name, object_name, fields=None, conditions=None, expiration=3600):
    s3_client = boto3.client('s3')
    try:
        response = s3_client.generate_presigned_post(bucket_name,object_name,Fields=fields,Conditions=conditions,ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    return response

def validate_image_file_name(img_id):
    if (img_id == None):
        return False
    regex = "([^\\s]+(\\.(?i)(jpe?g|png))$)"
    pattern = re.compile(regex)
    if(re.search(pattern, img_id)):
        return True
    return False

def _200_response(message, id, image_file_name, presign_url):
    body = {"message": message, "id": id, "image_file_name": image_file_name,"presign_url": presign_url}
    response = {"statusCode": 200, "body": json.dumps(body)}
    return response

def _400_response(message):
    body = {"message": message}
    response = {"statusCode": 400, "body": json.dumps(body)}
    return response

def _500_response(message):
    body = {"message": message}
    response = {"statusCode": 500, "body": json.dumps(body)}
    return response

def generate_unique_id():
    return str(uuid.uuid4())    
    
    

class DynamoDB:
    def __init__(self):
        self.dynamo_client = boto3.client('dynamodb')
        self.table_name = os.environ['tableName']

    def put_object(self, id, callback_url, image_file_name):
        dynamo_item = {'id': {'S': id}, 'callback_url': {'S': callback_url}, 'image_file_name': {'S': image_file_name}}
        response = self.dynamo_client.put_item(TableName=self.table_name, Item=dynamo_item)
        return response