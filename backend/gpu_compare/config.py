from decimal import Decimal
from functools import lru_cache
from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    app_mode: str = "local"
    database_url: SecretStr = SecretStr(
        "postgresql://gpu-compare:gpu-compare@localhost:55433/gpu-compare"
    )
    db_driver: str = "postgres"
    db_cluster_arn: str = ""
    db_secret_arn: str = ""
    db_name: str = "gpu-compare"
    session_secret: SecretStr = SecretStr("")
    session_secret_file: str = ""
    session_secret_arn: str = ""
    aws_region: str = "eu-north-1"
    aws_endpoint_url: str | None = None
    s3_bucket: str = "gpu-compare-local"
    sqs_queue_url: str = "http://localhost:55001/123456789012/gpu-compare-jobs"
    public_origin: str = "http://localhost:5180"
    max_sessions_per_hour: int = 100
    benchmarks_enabled: bool = False
    vast_api_key: SecretStr = SecretStr("")
    vast_secret_arn: str = ""
    benchmark_operator_password: SecretStr = SecretStr("")
    benchmark_operator_secret_arn: str = ""
    gpu_monthly_budget_eur: Decimal = Decimal("10")
    gpu_session_budget_eur: Decimal = Decimal("1")
    gpu_usd_to_eur: Decimal = Decimal("1.10")
    gpu_max_minutes: int = 30
    gpu_idle_seconds: int = 300
    gpu_startup_seconds: int = 600
    gpu_request_seconds: int = 120
    gpu_disk_gb: int = 30
    gpu_download_gb: Decimal = Decimal("25")
    gpu_upload_gb: Decimal = Decimal("1")
    gpu_runner_image: str = (
        "python@sha256:1faf2343e747208b2a36e5f2b5ff908ec3b2d0078a6a7bfe73b535698fe83909"
    )
    gpu_runner_artifact_key: str = ""
    gpu_runner_artifact_sha256: str = ""

    @property
    def public_demo(self) -> bool:
        return self.app_mode == "demo"


@lru_cache
def settings() -> Settings:
    config = Settings()
    secret_fields = {
        "session_secret": config.session_secret_arn,
        "vast_api_key": config.vast_secret_arn,
        "benchmark_operator_password": config.benchmark_operator_secret_arn,
    }
    if any(secret_fields.values()):
        import boto3

        client = boto3.client("secretsmanager", region_name=config.aws_region)
        for name, arn in secret_fields.items():
            if arn:
                value = client.get_secret_value(SecretId=arn)["SecretString"]
                setattr(config, name, SecretStr(value))
    if (
        config.session_secret_file
        and not config.public_demo
        and not config.session_secret.get_secret_value()
    ):
        config.session_secret = SecretStr(Path(config.session_secret_file).read_text().strip())
    if len(config.session_secret.get_secret_value()) < 32:
        raise RuntimeError("SESSION_SECRET must contain at least 32 characters")
    return config
