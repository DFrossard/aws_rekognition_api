import os
import json
import logging
import uuid
import boto3
from botocore.exceptions import ClientError

def handler(event, context):
    logging.info("Starting createBlob")

    bucket = os.environ['bucketName']
    id = str(uuid.uuid4())
    presign_url = create_presigned_post(bucket, id)

    body = {
        "message": "Created blob",
        "id": id,
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