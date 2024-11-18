import os
import boto3
import json

s3_client = boto3.client('s3')
data_lake_bucket = os.environ['PROCESSED_IMAGES_BUCKET']

def lambda_handler(event, context):
    for record in event['Records']:
        # Get message from SQS
        message = record['body']
        s3_event = json.loads(message)
        
        # Extract bucket and object key from S3 event
        source_bucket = s3_event['Records'][0]['s3']['bucket']['name']
        object_key = s3_event['Records'][0]['s3']['object']['key']
        
        # Copy image from source bucket to data lake bucket
        copy_source = {'Bucket': source_bucket, 'Key': object_key}
        s3_client.copy_object(
            CopySource=copy_source,
            Bucket=data_lake_bucket,
            Key=object_key
        )

    return {
        "statusCode": 200,
        "body": "Image processed and copied successfully."
    }
