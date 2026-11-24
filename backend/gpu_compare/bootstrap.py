import os
import secrets
from pathlib import Path

from botocore.exceptions import ClientError

from gpu_compare.config import settings
from gpu_compare.migrate import migrate
from gpu_compare.storage import client


def bootstrap():
    if location := os.getenv("SESSION_SECRET_FILE"):
        path = Path(location)
        try:
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            pass
        else:
            with os.fdopen(fd, "w") as handle:
                handle.write(secrets.token_urlsafe(48))
    migrate()
    config = settings()
    # Cloud infrastructure is created only by Terraform, not by application startup.
    if config.aws_endpoint_url:
        try:
            client("s3").create_bucket(
                Bucket=config.s3_bucket,
                CreateBucketConfiguration={"LocationConstraint": config.aws_region},
            )
        except ClientError as exc:
            if exc.response["Error"]["Code"] != "BucketAlreadyOwnedByYou":
                raise
        client("sqs").create_queue(
            QueueName="gpu-compare-jobs", Attributes={"VisibilityTimeout": "1080"}
        )
    print("GPU Compare database and local services ready")


if __name__ == "__main__":
    bootstrap()
