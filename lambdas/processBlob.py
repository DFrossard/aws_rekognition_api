import os
import json
import logging
import boto3
import botocore
from commom.dynamodb import DynamoDB
from commom.responses import Responses

def handler(event, context):
    responses = Responses()
    bucket = os.environ['bucketName']
    image_key = event['Records'][0]['s3']['object']['key']

    try:
        labels = get_labels(bucket, image_key)
    except:
        msg = f"Error while detecting image labels on image {image_key}"
        logging.error(msg)
        return responses._500_response(msg)

    formatted_labels = format_labels(labels)

    id = image_key.split('/')[0]
    try:
        blob = retrieve_item(id)
    except:
        msg = f"Error while retrieving item from database for image {image_key}"
        logging.error(msg)
        return responses._500_response(msg)

    
    blob_item = blob['Item']
    try:
        save_response = save_labels(formatted_labels, blob_item)
    except:
        msg = f"Error while detecting image labels on image {image_key}"
        logging.error(msg)
        return responses._500_response(msg)
    status_code = save_response['ResponseMetadata']['HTTPStatusCode']
    response = responses._200_response(f"Image {image_key} processed")


    return response

def get_labels(bucket, image_key):
    client = boto3.client("rekognition")
    try:
        labels_response = client.detect_labels(Image = {"S3Object": {"Bucket": bucket, "Name": image_key}}, MaxLabels=5,  MinConfidence=80)
    except botocore.exceptions.ClientError as error:
        raise error
    return labels_response

def format_labels(labels):
    formatted_labels = labels
    formatted_labels.pop("LabelModelVersion")
    formatted_labels.pop("ResponseMetadata")
    for l in formatted_labels['Labels']:
        l.pop("Instances")
        l.pop("Parents")
    return formatted_labels

def retrieve_item(id):
    dynamo = DynamoDB()
    blob = dynamo.get_item({'id': {'S': id}})
    return blob

def save_labels(labels, blob_item):
    dynamo = DynamoDB()
    updated_dynamo_item = generate_updated_dynamo_item(labels, blob_item)
    dynamo_response = dynamo.put_item(updated_dynamo_item)
    return dynamo_response

def generate_updated_dynamo_item(labels, blob_item):
    new_blob = blob_item
    labels_dynamo_item = {'L': []}
    for l in labels["Labels"]:
        label_name = l['Name']
        label_confidence = str(l['Confidence'])
        label = {"M": {"label": {"S": label_name}, "Confidence": {"N": label_confidence}}}
        labels_dynamo_item["L"].append(label)
    new_blob['labels'] = labels_dynamo_item
    return new_blob