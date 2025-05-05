import boto3
from .config import AWS_ENDPOINT_URL, AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, SHIPPING_QUEUE

class ShippingPublisher:
    def __init__(self):
        self.client = boto3.client(
            "sqs",
            endpoint_url=AWS_ENDPOINT_URL,
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
        response = self.client.get_queue_url(QueueName=SHIPPING_QUEUE)
        self.queue_url = response['QueueUrl']


    def send_new_shipping(self, shipping_id: str):
        response = self.client.send_message(
            QueueUrl=self.queue_url,
            MessageBody=shipping_id
        )

        return response['MessageId']

    def poll_shipping(self, batch_size: int = 10):
        messages = self.client.receive_message(
            QueueUrl=self.queue_url,
            MessageAttributeNames=['All'],
            MaxNumberOfMessages=batch_size,
            WaitTimeSeconds=10
        )

        if 'Messages' not in messages:
            return []

        return [msg['Body'] for msg in messages['Messages']]
