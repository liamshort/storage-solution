variable "region" {
  type        = string
  description = "AWS Region for resource deployment"
}

variable "bucket_name" {
  description = "The name of the bucket"
  type        = string
}

variable "bucket_acl" {
  description = "The canned ACL to apply"
  type        = string
  default     = "private"
}

variable "bucket_versioning" {
  description = "The canned ACL to apply"
  type        = bool
  default     = true
}

variable "bucket_ignore_public_acls" {
  description = "	Whether Amazon S3 should ignore public ACLs for this bucket"
  type        = bool
  default     = true
}

variable "bucket_block_public_acls" {
  description = "Whether Amazon S3 should block public ACLs for this bucket"
  type        = bool
  default     = true
}

variable "bucket_block_public_policy" {
  description = "Whether Amazon S3 should block public bucket policies for this bucket"
  type        = bool
  default     = true
}

variable "bucket_restrict_public_buckets" {
  description = "Whether Amazon S3 should restrict public bucket policies for this bucket"
  type        = bool
  default     = true
}

variable "bucket_kms_master_key_id" {
  type        = string
  description = "KMS Key to be used for this bucket"
  default     = ""
}
variable "bucket_sse_algorithm" {
  type        = string
  description = "SSE algorithm for this bucket"
  default     = "AES256"
}

variable "bucket_tags" {
  description = "A map of tags to add to S3 Bucket"
  type        = map(string)
  default     = {}
}

variable "dynamodb_table_name" {
  description = "Name of the DynamoDB table"
  type        = string
}

variable "dynamodb_write_capacity" {
  description = "The number of write units for this table"
  type        = number
  default     = 5
}

variable "dynamodb_read_capacity" {
  description = "The number of read units for this table"
  type        = number
  default     = 5
}

variable "dynamodb_billing_mode" {
  description = "Controls how you are billed for read/write throughput and how you manage capacity"
  type        = string
  default     = "PROVISIONED"
}

variable "dynamodb_tags" {
  description = "A map of tags to add to DynamoDB Table"
  type        = map(string)
  default     = {}
}

variable "deploy_lambda" {
  description = "Should the Lambda with Cloudwatch Events Rule be deployed"
  type        = bool
  default     = false
}

variable "lambda_function_name" {
  description = "Unique name for Lambda Function"
  type        = string
}

variable "lambda_description" {
  description = "Description for Lambda Function"
  type        = string
  default     = "Parse DynamoDB to get todays pictures and send to SNS"
}

variable "lambda_handler" {
  description = "Lambda Function entrypoint for code"
  type        = string
  default     = "parse_dynamodb.lambda_handler"
}

variable "lambda_runtime" {
  description = "Lambda Function runtime"
  type        = string
  default     = "python3.6"
}

variable "lambda_timeout" {
  description = "The amount of time the Lambda Function has to run in seconds"
  type        = string
  default     = 300
}

variable "lambda_years_back" {
  description = "Number of years back the Lambda Function will check for in DynamoDB"
  type        = number
  default     = 10
}

variable "lambda_tags" {
  description = "A map of tags to add to Lambda Function"
  type        = map(string)
  default     = {}
}

variable "cloudwatch_event_rule_name" {
  description = "The name of the Cloudwatch Event Rule"
  type        = string
  default     = "invoke-storage-solution-lambda"
}

variable "cloudwatch_event_rule_description" {
  description = "Description for the Cloudwatch Event Rule"
  type        = string
  default     = "Daily invocation of Storage Solution Lambda"
}

variable "cloudwatch_event_rule_expression" {
  description = "Cron expression for Cloudwatch Event Rule, Lambda Function invoked at this time"
  type        = string
  default     = "cron(0 9 * * ? *)"
}

variable "iam_role_name" {
  description = "Name of the Lambda Function IAM Role"
  type        = string
  default     = "storage-solution-role"
}

variable "slack_webhook" {
  description = "Webhook used by Lambda Function to forward messages to Slack"
  type        = string
  default     = ""
}

variable "slack_channel" {
  description = "Name of the Slack channel that Lambda Function forwards messages to"
  type        = string
  default     = "daily-pictures"
}

variable "presigned_url_expiration" {
  description = "Expiration time of presigned URLs"
  type        = string
  default     = 3600
}