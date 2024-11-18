from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_sqs as sqs,
    aws_s3_notifications as s3_notifications,
    aws_lambda_event_sources as event_sources,
)
from constructs import Construct
import aws_cdk.aws_iam as iam

class SatelliteImagesStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        raw_images_bucket = s3.Bucket(self,
                                      "DataLakeSatelliteImagesRawBucket",
                                      versioned=True,
                                      bucket_name="data-lake-satellite-images-raw"
                                      )
        
        processed_images_bucket = s3.Bucket(self, 
                                            "DataLakeSatelliteImagesProcessedBucket",
                                            versioned=True,
                                            bucket_name="data-lake-satellite-images-processed"
                                            )
        
        image_processing_queue = sqs.Queue(self, "UserImageProcessingQueue")

        # Add S3 event notification to send events to SQS image_processing_queue
        raw_images_bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            s3_notifications.SqsDestination(image_processing_queue)
        )
        #Lambda Method
        image_processing_lambda = _lambda.Function(
            self,
            "ImageProcessorLambda",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="satellite_image_processor.lambda_handler",
            code=_lambda.Code.from_asset("data_lack_stack/lambda"),  # folder containing lambda code
            environment={
                "PROCESSED_IMAGES_BUCKET": processed_images_bucket.bucket_name
            }
        )
        #Permissions
        raw_images_bucket.grant_read(image_processing_lambda)  
        processed_images_bucket.grant_write(image_processing_lambda) 
        image_processing_queue.grant_consume_messages(image_processing_lambda) 
        
        # Add SQS as an event source for the Lambda function
        image_processing_lambda.add_event_source(event_sources.SqsEventSource(image_processing_queue))
        
        image_processing_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=["s3:GetObject", "s3:PutObject"],
                resources=[
                    raw_images_bucket.bucket_arn + "/*",
                    processed_images_bucket.bucket_arn + "/*"
                ]
            )
        )