terraform {
  required_version = ">= 0.14"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.0"
    }
  }
}

provider "aws" {
  region = var.region
}

locals {
  dynamodb_table_arn        = "arn:aws:dynamodb:eu-west-2:${data.aws_caller_identity.current.account_id}:table/${var.dynamodb_table_name}"
  s3_bucket_arn             = "arn:aws:s3:::${var.bucket_name}/*"
  sns_topic_arn             = "arn:aws:sns:${var.region}:${data.aws_caller_identity.current.account_id}:${var.sns_topic_name}"
  cloudwatch_event_rule_arn = "arn:aws:events:${var.region}:${data.aws_caller_identity.current.account_id}:rule/${var.cloudwatch_event_rule_name}"
}

data "aws_caller_identity" "current" {}

################################################################
## S3 BUCKET
################################################################

module "s3_bucket" {
  source = "terraform-aws-modules/s3-bucket/aws"

  bucket                  = var.bucket_name
  acl                     = var.bucket_acl
  ignore_public_acls      = var.bucket_ignore_public_acls
  block_public_acls       = var.bucket_block_public_acls
  block_public_policy     = var.bucket_block_public_policy
  restrict_public_buckets = var.bucket_restrict_public_buckets
  tags                    = var.bucket_tags

  server_side_encryption_configuration = {
    rule = {
      apply_server_side_encryption_by_default = {
        kms_master_key_id = var.bucket_kms_master_key_id
        sse_algorithm     = var.bucket_sse_algorithm
      }
    }
  }

  versioning = {
    enabled = var.bucket_versioning
  }
}

################################################################
## DYNAMODB
################################################################

module "dynamodb_table" {
  source = "terraform-aws-modules/dynamodb-table/aws"

  name           = var.dynamodb_table_name
  hash_key       = "name"
  write_capacity = var.dynamodb_write_capacity
  read_capacity  = var.dynamodb_read_capacity
  billing_mode   = var.dynamodb_billing_mode

  attributes = [
    {
      name = "name"
      type = "S"
    }
  ]

  tags = var.dynamodb_tags
}

################################################################
## LAMBDA
################################################################

module "lambda_function" {
  source = "terraform-aws-modules/lambda/aws"
  count  = var.deploy_lambda ? 1 : 0

  function_name            = var.lambda_function_name
  description              = var.lambda_description
  handler                  = var.lambda_handler
  runtime                  = var.lambda_runtime
  timeout                  = var.lambda_timeout
  publish                  = true
  create_role              = true
  role_name                = var.iam_role_name
  attach_policy_statements = true
  policy_statements = {
    get_dynamodb = {
      effect = "Allow",
      actions = [
        "dynamodb:Scan"
      ],
      resources = [local.dynamodb_table_arn]
    },
    s3_read = {
      effect = "Allow",
      actions = [
        "s3:HeadObject",
        "s3:GetObject",
        "s3:ListBucket"
      ],
      resources = [local.s3_bucket_arn]
    },
    sns_publish = {
      effect = "Allow",
      actions = [
        "sns:Publish"
      ],
      resources = [local.sns_topic_arn]
    }
  }

  allowed_triggers = {
    OneRule = {
      principal  = "events.amazonaws.com"
      source_arn = local.cloudwatch_event_rule_arn
    }
  }

  source_path = "lambda_code/parse_dynamodb.py"

  store_on_s3 = true
  s3_bucket   = var.bucket_name

  environment_variables = {
    region                   = var.region
    s3_bucket                = module.s3_bucket.this_s3_bucket_id
    table_name               = module.dynamodb_table.this_dynamodb_table_id
    years_back               = var.lambda_years_back
    presigned_url_expiration = var.presigned_url_expiration
    sns_topic_arn            = local.sns_topic_arn
  }

  tags = var.lambda_tags

  depends_on = [
    module.s3_bucket
  ]
}

################################################################
## CLOUDWATCH EVENTS
################################################################

resource "aws_cloudwatch_event_rule" "this" {
  count = var.deploy_lambda ? 1 : 0

  name        = var.cloudwatch_event_rule_name
  description = var.cloudwatch_event_rule_description

  schedule_expression = var.cloudwatch_event_rule_expression
}

resource "aws_cloudwatch_event_target" "this" {
  count = var.deploy_lambda ? 1 : 0

  rule      = aws_cloudwatch_event_rule.this[0].name
  target_id = "SendToLambda"
  arn       = module.lambda_function[0].this_lambda_function_arn
}

################################################################
## SNS ENDPOINT
################################################################

module "sns_topic" {
  source = "terraform-aws-modules/sns/aws"
  count  = var.deploy_lambda ? 1 : 0

  name = var.sns_topic_name
}
