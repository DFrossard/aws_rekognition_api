import os
import json
import logging
import boto3
import re
from botocore.exceptions import ClientError

def handler(event, context):
    logging.info("Starting createBlob")
    try:
        body = json.loads(event['body'])
        image_id = body['image_id']
    except KeyError:
        body = {"message": "Field image_id not detected in request body"}
        response = {"statusCode": 400, "body": json.dumps(body)}
        return response
    except:
        body = {"message": "Invalid request body. Please use {'callback_uri': your_callback_url, 'image_id': your_image_id}"}
        response = {"statusCode": 400, "body": json.dumps(body)}
        return response
    
    is_valid = validate_image_name(image_id)
    if not is_valid:
        body = {"message": "Field image_id is invalid. Must end with .jpg, .png, .jpeg"}
        response = {"statusCode": 400, "body": json.dumps(body)}

    if "callback_url" in body.keys():
        callback_url = body['callback_url']

    bucket = os.environ['bucketName']
    presign_url = create_presigned_post(bucket, image_id)

    body = {
        "message": "Created blob",
        "id": image_id,
        "presigned_url": presign_url
    }
    response = {"statusCode": 200, "body": json.dumps(body)}
    return response

def create_presigned_post(bucket_name, object_name, fields=None, conditions=None, expiration=3600):
    s3_client = boto3.client('s3')
    try:
        response = s3_client.generate_presigned_post(bucket_name,object_name,Fields=fields,Conditions=conditions,ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    return response

def validate_image_name(img_id):
    if (img_id == None):
        return False
    regex = "([^\\s]+(\\.(?i)(jpe?g|png))$)"
    pattern = re.compile(regex)
    if(re.search(pattern, img_id)):
        return True
    return False