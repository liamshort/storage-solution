variable "region" {
  type        = string
  description = "AWS Region for resource deployment"
}

variable "bucket_name" {
  description = ""
  type        = string
}

variable "bucket_acl" {
  description = ""
  type        = string
  default     = "private"
}

variable "bucket_versioning" {
  description = ""
  type        = bool
  default     = false
}

variable "bucket_ignore_public_acls" {
  description = ""
  type        = bool
  default     = true
}

variable "bucket_block_public_acls" {
  description = ""
  type        = bool
  default     = true
}

variable "bucket_block_public_policy" {
  description = ""
  type        = bool
  default     = true
}

variable "bucket_restrict_public_buckets" {
  description = ""
  type        = bool
  default     = true
}

variable "bucket_tags" {
  description = ""
  type        = map(string)
  default     = {}
}

variable "dynamodb_table_name" {
  description = ""
  type        = string
}

variable "dynamodb_tags" {
  description = ""
  type        = map(string)
  default     = {}
}