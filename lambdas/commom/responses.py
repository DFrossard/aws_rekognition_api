import json

class Responses:

    def _200_response(self, message, **kwargs):
        body = {"message": message}
        for arg in kwargs:
            body[arg] = kwargs[arg]
        #body = {"message": message, "id": id, "image_file_name": image_file_name,"presign_url": presign_url}
        response = {"statusCode": 200, "body": json.dumps(body)}
        return response

    def _400_response(self, message):
        body = {"message": message}
        response = {"statusCode": 400, "body": json.dumps(body)}
        return response

    def _404_response(self, id):
        body = {"message": f"id {id} not found"}
        response = {"statusCode": 404, "body": json.dumps(body)}
        return response

    def _500_response(self, message):
        body = {"message": message}
        response = {"statusCode": 500, "body": json.dumps(body)}
        return response
    