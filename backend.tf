terraform {
    backend "s3" {
        bucket         = "MY_BACKEND_BUCKET_NAME"
        key            = "MY_BACKEND_STATE_FILE"
        encrypt        = true
        region         = "MY_BACKEND_EGION"
        dynamodb_table = "MY_BACKEND_TABLE_NAME"
    }
}
