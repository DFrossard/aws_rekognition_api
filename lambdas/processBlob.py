import os
import json
import boto3
from commom.dynamodb import DynamoDB

def handler(event, context):
    bucket = os.environ['bucketName']
    image_key = event['Records'][0]['s3']['object']['key']

    labels = get_labels(bucket, image_key)
    formatted_labels = format_labels(labels)

    id = image_key.split('/')[0]
    save_response = save_labels(formatted_labels, id)
    status_code = save_response['ResponseMetadata']['HTTPStatusCode']
    response = {"statusCode": status_code, "body": json.dumps(save_response)}


    return response

def get_labels(bucket, image_key):
    client = boto3.client("rekognition")
    labels_response = client.detect_labels(Image = {"S3Object": {"Bucket": bucket, "Name": image_key}}, MaxLabels=5,  MinConfidence=80)
    return labels_response

def format_labels(labels):
    formatted_labels = labels
    formatted_labels.pop("LabelModelVersion")
    formatted_labels.pop("ResponseMetadata")
    for l in formatted_labels['Labels']:
        l.pop("Instances")
        l.pop("Parents")
    return formatted_labels

def save_labels(labels, id):
    dynamo = DynamoDB()
    updated_dynamo_item = generate_updated_dynamo_item(labels, id)
    dynamo_response = dynamo.put_item(updated_dynamo_item)
    return dynamo_response

def generate_updated_dynamo_item(labels, id):
    labels_dynamo_item = {'L': []}
    for l in labels["Labels"]:
        label_name = l['Name']
        label_confidence = str(l['Confidence'])
        label = {"M": {"label": {"S": label_name}, "Confidence": {"N": label_confidence}}}
        labels_dynamo_item["L"].append(label)
    return {'id': {'S': id}, 'labels': labels_dynamo_item}