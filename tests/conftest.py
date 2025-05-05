import pytest
import boto3
from services.config import AWS_ENDPOINT_URL, AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, SHIPPING_TABLE_NAME, \
    SHIPPING_QUEUE


@pytest.fixture(scope="session", autouse=True)
def setup_localstack_resources():
    dynamo_client = boto3.client(
        "dynamodb",
        endpoint_url=AWS_ENDPOINT_URL,
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )

    existing_tables = dynamo_client.list_tables()["TableNames"]
    if SHIPPING_TABLE_NAME not in existing_tables:
        dynamo_client.create_table(
            TableName=SHIPPING_TABLE_NAME,
            KeySchema=[
                {"AttributeName": "shipping_id", "KeyType": "HASH"}
            ],
            AttributeDefinitions=[
                {"AttributeName": "shipping_id", "AttributeType": "S"}
            ],
            BillingMode="PAY_PER_REQUEST",
        )

    dynamo_client.get_waiter("table_exists").wait(TableName=SHIPPING_TABLE_NAME)

    sqs_client = boto3.client(
        "sqs",
        endpoint_url=AWS_ENDPOINT_URL,
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )

    response = sqs_client.create_queue(QueueName=SHIPPING_QUEUE)
    queue_url = response["QueueUrl"]

    yield  # Дочекайся завершення всіх тестів

    # Очистка після тестування
    dynamo_client.delete_table(TableName=SHIPPING_TABLE_NAME)
    sqs_client.delete_queue(QueueUrl=queue_url)


@pytest.fixture(scope="session")
def dynamo_resource():
    return boto3.resource(
        "dynamodb",
        endpoint_url=AWS_ENDPOINT_URL,
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )
