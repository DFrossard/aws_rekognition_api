from boto3.dynamodb.types import TypeDeserializer

class BlobDeserializer:

    def deserialize_dynamo_blob(self, item):
        d = TypeDeserializer()
        image_data = {k: d.deserialize(value=v) for k, v in item.items()}
        new_labels = []
        if 'labels' in image_data:
            labels_with_decimal = image_data['labels']
            for l in labels_with_decimal:
                new_labels.append({"Confidence": float(l['Confidence']), "label": l['label']})
            image_data['labels'] = new_labels
        return image_data