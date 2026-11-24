import boto3

from gpu_compare.config import settings


def client(service):
    config = settings()
    local_credentials = (
        {"aws_access_key_id": "local", "aws_secret_access_key": "local"}
        if config.aws_endpoint_url
        else {}
    )
    return boto3.client(
        service,
        region_name=config.aws_region,
        endpoint_url=config.aws_endpoint_url,
        **local_credentials,
    )
