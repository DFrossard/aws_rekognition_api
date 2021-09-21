import os
import uuid
import json
import logging
import boto3
import re
from botocore.exceptions import ClientError
from commom.dynamodb import DynamoDB
from commom.responses import Responses

def handler(event, context):
    responses = Responses()
    logging.info("Starting createBlob")
    try:
        body = json.loads(event['body'])
        image_file_name = body['image_file_name']
    except KeyError:
        return responses._400_response("Field image_file_name not detected in request body")
    except:
        return responses._400_response('Invalid request body. Please use {"callback_uri": your_callback_url, "image_file_name": your_image_file_name}')
    
    is_valid = validate_image_file_name(image_file_name)
    if not is_valid:
        return responses._400_response("Field image_file_name is invalid. Must end with .jpg, .png, .jpeg")

    if "callback_url" in body.keys():
        callback_url = body['callback_url']
    else:
        callback_url = ""

    id = generate_unique_id()
    img_bucket_path = id + '/' + image_file_name
    bucket = os.environ['bucketName']

    presign_url = create_presigned_post(bucket, img_bucket_path)

    dynamo = DynamoDB()
    dynamo_item = create_dynamo_item(id, callback_url, image_file_name)
    dynamo_response = dynamo.put_item(dynamo_item)

    response_status_code = dynamo_response['ResponseMetadata']['HTTPStatusCode']
    if response_status_code != 200:
        return responses._500_response("Failed to save to database.")

    body = {"message": "Created blob", "id": id, "image_file_name": image_file_name, "presign_url": presign_url}
    return responses._200_response(body)

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

def generate_unique_id():
    return str(uuid.uuid4())

def create_dynamo_item(id, callback_url, image_file_name):
    dynamo_item = {'id': {'S': id}, 'callback_url': {'S': callback_url}, 'image_file_name': {'S': image_file_name}}
    return dynamo_item