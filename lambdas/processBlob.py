import os
import json
import boto3

def handler(event, context):
    bucket = os.environ['bucketName']
    image = event['Records'][0]['s3']['object']['key']

    client = boto3.client("rekognition")
    labels_response = client.detect_labels(Image = {"S3Object": {"Bucket": bucket, "Name": image}}, MaxLabels=5,  MinConfidence=80)

    response = {"statusCode": 200, "body": json.dumps(labels_response)}

    return response