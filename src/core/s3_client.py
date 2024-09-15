import json

import boto3
from bson import ObjectId  # Make sure you have this installed

from src.core.settings import settings


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super(JSONEncoder, self).default(obj)


class S3Client:
    def __init__(self) -> None:
        '''
        Initializes the S3Client instance and establishes a connection
        to AWS S3.

        Sets up the boto3 S3 client using the AWS region, access key ID, and
        secret access key specified in the settings. If the connection
        to AWS S3 fails, prints an error message and raises the exception.

        Raises:
            Exception: If there is an error during the connection setup.
        '''

        try:
            self.client = boto3.client(
                service_name='s3',
                region_name=settings.AWS_REGION,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
            )
        except Exception as e:
            print(
                'An error occurred while trying to connect '
                f'to AWS S3: {e}'
            )
            raise

    def upload_file(self, data: list[dict], file_name: str) -> None:
        '''
        Uploads a JSON file to an AWS S3 bucket.

        Converts the provided list of dictionaries to JSON format and uploads
        it to the specified S3 bucket under the provided file name.

        Args:
            data (list[dict]): The list of dictionaries to be converted to
            JSON and uploaded.
            file_name (str): The name of the file to be created in the
            S3 bucket.

        Raises:
            Exception: If there is an error during the file upload process.
        '''

        json_data = json.dumps(data, cls=JSONEncoder)

        try:
            self.client.put_object(
                Bucket=settings.AWS_BUCKET_NAME,
                Key=file_name,
                Body=json_data,
                ContentType='application/json'
            )
            print(
                f'JSON uploaded to AWS S3 bucket "{settings.AWS_BUCKET_NAME}"'
                f' as "{file_name}"'
            )
        except Exception as e:
            print(
                'An error occurred while trying to upload the JSON file'
                f'to the AWS S3 bucket: {e}'
            )
            raise
