import json
import logging
import requests
from commom.blob_dynamo_deserializer import BlobDeserializer

def handler(event, context):
    records = event['Records']

    for record in records:
        if record['eventName'] == "MODIFY":
            try:
                response = send_callback(record)
                print(f"Response from record {record['dynamodb']['Keys']['id']['S']}: {response.json()}")
                print(f"Data sent: {response.json()['json']}")
            except BaseException as error:
                callback_url = get_callback_url(record)
                logging.error(f"error while sending callback to {callback_url}. Error: {error}")

def send_callback(record):
    blob = deserialize_record(record['dynamodb']['NewImage'])
    response = send_callback_request(blob)
    return response

def send_callback_request(blob):
    url = blob['callback_url']
    data = blob
    try:
        request = requests.post(url= url, data= json.dumps(data))
    except BaseException as er:
        raise er
    return request
    
def deserialize_record(item):
    deserializer = BlobDeserializer()
    blob = deserializer.deserialize_dynamo_blob(item)
    return blob
    

def get_callback_url(record):
    return record['dynamodb']['NewImage']['callback_url']['S']