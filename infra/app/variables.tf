terraform {
  backend "s3" {}
  required_version = ">= 1.13, < 2.0"
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 6.0" }
  }
}
variable "region" {
  type    = string
  default = "eu-north-1"
  validation {
    condition     = var.region == "eu-north-1"
    error_message = "GPU Compare resources must use the project's selected Region eu-north-1."
  }
}
variable "name" {
  default = "gpu-compare"
  validation {
    condition     = var.name == "gpu-compare"
    error_message = "This test stack binds the explicitly prepared gpu-compare database and secrets."
  }
}
variable "image_uri" {
  type        = string
  description = "ECR image URI pinned with @sha256: digest, built for linux/amd64."
  validation {
    condition     = can(regex("^[0-9]{12}\\.dkr\\.ecr\\.eu-north-1\\.amazonaws\\.com/gpu-compare@sha256:[a-f0-9]{64}$", var.image_uri))
    error_message = "Use a Stockholm gpu-compare ECR image pinned to an immutable sha256 digest."
  }
}
variable "database_secret_arn" {
  type        = string
  description = "Secrets Manager ARN for the SQL user prepared by scripts/prepare_aws_demo.py. No secret value."
  validation {
    condition     = can(regex("^arn:aws:secretsmanager:eu-north-1:[0-9]{12}:secret:gpu-compare/db-", var.database_secret_arn))
    error_message = "Use the gpu-compare/db secret ARN in Stockholm."
  }
}
variable "session_secret_arn" {
  type = string
  validation {
    condition     = can(regex("^arn:aws:secretsmanager:eu-north-1:[0-9]{12}:secret:gpu-compare/session-", var.session_secret_arn))
    error_message = "Use the gpu-compare/session secret ARN in Stockholm."
  }
}
variable "enable_github_deploy" {
  type        = bool
  default     = false
  description = "Opt in only after GitHub publication and project OIDC permissions are separately approved."
}
variable "github_repository" { default = "wasiliy-strecker/gpu-compare" }
variable "existing_github_oidc_arn" {
  type    = string
  default = ""
}
variable "enable_gpu_benchmarks" {
  type    = bool
  default = false
}
variable "vast_secret_arn" {
  type    = string
  default = ""
  validation {
    condition     = var.vast_secret_arn == "" || can(regex("^arn:aws:secretsmanager:eu-north-1:[0-9]{12}:secret:gpu-compare/vast-", var.vast_secret_arn))
    error_message = "Use a server-side gpu-compare/vast secret in Stockholm."
  }
}
variable "gpu_operator_secret_arn" {
  type    = string
  default = ""
  validation {
    condition     = var.gpu_operator_secret_arn == "" || can(regex("^arn:aws:secretsmanager:eu-north-1:[0-9]{12}:secret:gpu-compare/gpu-operator-", var.gpu_operator_secret_arn))
    error_message = "Use a gpu-compare/gpu-operator secret in Stockholm."
  }
}
variable "gpu_runner_image" { default = "python@sha256:1faf2343e747208b2a36e5f2b5ff908ec3b2d0078a6a7bfe73b535698fe83909" }
variable "gpu_runner_artifact_key" { default = "" }
variable "gpu_runner_artifact_sha256" { default = "" }
provider "aws" {
  region = var.region
  default_tags { tags = { Project = var.name, Environment = "portfolio-demo" } }
}
data "aws_caller_identity" "current" {}
locals {
  account = data.aws_caller_identity.current.account_id
  functions = {
    api          = { handler = "gpu_compare.api.handler", timeout = 25, memory = 512 }
    worker       = { handler = "gpu_compare.worker.handler", timeout = 180, memory = 1024 }
    migrate      = { handler = "gpu_compare.migrate.handler", timeout = 180, memory = 512 }
    gpu_watchdog = { handler = "gpu_compare.benchmarks.lifecycle.handler", timeout = 120, memory = 512 }
  }
}
