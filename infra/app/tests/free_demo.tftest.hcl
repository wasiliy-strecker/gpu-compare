mock_provider "aws" {
  mock_data "aws_caller_identity" {
    defaults = { account_id = "123456789012" }
  }
  mock_data "aws_rds_cluster" {
    defaults = {
      arn                                 = "arn:aws:rds:eu-north-1:123456789012:cluster:gpu-compare"
      engine                              = "aurora-postgresql"
      database_name                       = ""
      iam_database_authentication_enabled = true
      deletion_protection                 = true
      tags                                = { ManagedBy = "gpu-compare-free-demo" }
    }
  }
}

variables {
  image_uri           = "123456789012.dkr.ecr.eu-north-1.amazonaws.com/gpu-compare@sha256:0000000000000000000000000000000000000000000000000000000000000000"
  database_secret_arn = "arn:aws:secretsmanager:eu-north-1:123456789012:secret:gpu-compare/db-abcdef"
  session_secret_arn  = "arn:aws:secretsmanager:eu-north-1:123456789012:secret:gpu-compare/session-abcdef"
}

run "free_plan_defaults" {
  command = plan
  assert {
    condition     = length(aws_iam_openid_connect_provider.github) == 0 && length(aws_iam_role.deploy) == 0 && length(aws_iam_role_policy.deploy) == 0
    error_message = "Free Plan deployment must not request GitHub OIDC or a GitHub deployment role."
  }
  assert {
    condition     = alltrue([for fn in aws_lambda_function.functions : fn.reserved_concurrent_executions == -1]) && aws_lambda_event_source_mapping.jobs.scaling_config[0].maximum_concurrency == 2
    error_message = "Use unreserved Lambda concurrency with at most two SQS workers."
  }
  assert {
    condition     = aws_lambda_function.functions["worker"].environment[0].variables["DB_NAME"] == "gpu-compare" && aws_lambda_function.functions["worker"].environment[0].variables["DB_SECRET_ARN"] == var.database_secret_arn
    error_message = "Use the dedicated GPU Compare database and SQL secret."
  }
}

run "reject_frankfurt" {
  command = plan
  variables { region = "eu-central-1" }
  expect_failures = [var.region]
}

run "reject_foreign_secret" {
  command = plan
  variables {
    database_secret_arn = "arn:aws:secretsmanager:eu-north-1:999999999999:secret:gpu-compare/db-abcdef"
  }
  expect_failures = [aws_lambda_function.functions]
}

run "explicit_github_opt_in" {
  command = plan
  variables { enable_github_deploy = true }
  assert {
    condition     = length(aws_iam_openid_connect_provider.github) == 1 && length(aws_iam_role.deploy) == 1
    error_message = "Future authorized GitHub delivery must remain available as an explicit opt-in."
  }
}

run "gpu_admission_off_cleanup_on" {
  command = plan
  assert {
    condition     = aws_lambda_function.functions["api"].environment[0].variables["BENCHMARKS_ENABLED"] == "false" && aws_scheduler_schedule.gpu_watchdog.schedule_expression == "rate(1 minute)"
    error_message = "Admission must default off while the independent cleanup schedule remains present."
  }
  assert {
    condition     = aws_lambda_function.functions["migrate"].environment[0].variables["VAST_SECRET_ARN"] == ""
    error_message = "Migrations must not load Vast credentials."
  }
}

run "reject_unprepared_gpu_enablement" {
  command = plan
  variables { enable_gpu_benchmarks = true }
  expect_failures = [aws_lambda_function.functions]
}
