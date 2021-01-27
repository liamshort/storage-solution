terraform {
  required_version = ">= 0.14"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "3.11.0"
    }
  }
}

provider "aws" {
  region = var.region
}

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

module "dynamodb_table" {
  source = "terraform-aws-modules/dynamodb-table/aws"

  name           = var.dynamodb_table_name
  hash_key       = "name"
  write_capacity = var.dynamodb_write_capacity
  read_capacity = var.dynamodb_read_capacity
  billing_mode = var.dynamodb_billing_mode

  attributes = [
    {
      name = "name"
      type = "S"
    }
  ]

  tags = var.dynamodb_tags
}
