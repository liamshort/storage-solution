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
