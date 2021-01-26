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

  versioning = {
    enabled = var.bucket_versioning
  }
}

module "dynamodb_table" {
  source = "terraform-aws-modules/dynamodb-table/aws"

  name     = var.dynamodb_table_name
  hash_key = "name"

  attributes = [
    {
      name = "name"
      type = "S"
    }
  ]

  tags = var.dynamodb_tags
}