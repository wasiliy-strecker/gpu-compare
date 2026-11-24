import json
import logging
import time

from gpu_compare import storage
from gpu_compare.benchmarks.lifecycle import process
from gpu_compare.config import settings
from gpu_compare.db import dumps

logger = logging.getLogger(__name__)


def handler(event, context):
    failures = []
    for record in event.get("Records", []):
        try:
            dispatch(json.loads(record["body"]))
        except Exception:
            # Infrastructure errors before/after the durable claim can be redelivered.
            failures.append({"itemIdentifier": record["messageId"]})
    return {"batchItemFailures": failures}


def dispatch(message):
    process(message["benchmark_lease_id"])


def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    queue = storage.client("sqs")
    while True:
        try:
            response = queue.receive_message(
                QueueUrl=settings().sqs_queue_url, WaitTimeSeconds=10, MaxNumberOfMessages=1
            )
            for item in response.get("Messages", []):
                dispatch(json.loads(item["Body"]))
                queue.delete_message(
                    QueueUrl=settings().sqs_queue_url, ReceiptHandle=item["ReceiptHandle"]
                )
        except KeyboardInterrupt:
            return
        except Exception as exc:
            logger.warning(dumps({"event": "worker.unavailable", "error_type": type(exc).__name__}))
            time.sleep(3)


if __name__ == "__main__":
    main()
