import os

AWS_ENDPOINT_URL = os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "test")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "test")
SHIPPING_TABLE_NAME = os.getenv("SHIPPING_TABLE_NAME", "ShippingTable")
SHIPPING_QUEUE = os.getenv("SHIPPING_QUEUE", "ShippingQueue")
