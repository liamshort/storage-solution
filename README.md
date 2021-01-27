# storage-solution

## Overview

This tool allows users Linux users to synchronise a local directory with an AWS S3 Bucket, providing a relatively cheap alternative to Cloud Storage Services such as OneDrive, DropBox or GoogleDrive when storing low volumes of data.

## Prerequisites

* Python3 installed
* `pip3 install -r requirements.txt`
* Terraform installed
* AWS Account
    * S3 Bucket
    * DynamoDB Table
* AWS Credentials configured for workstation

## AWS Infrastructure

The resources in AWS consist of the following:

* S3 Bucket used to store objects remotely.
* DynamoDB table used as an index to reflect the files stored both locally and in the S3 Bucket. Items within the Table have the following attributes:

    Attribute | Description
    | :--- | :--- |
    name | Original name of the file (with extension), prefixed with the formatted modified time
    path | The key for the file in S3 Bucket, which is also the relative path of the local storage directory
    modified_time | The time the file was modified
    state | Is the file raw (original state) or zip (compressed)

### Terraform deploy steps

* In `backend.tf`, define values to be used for the Terraform Backend
* Run `$ terraform init`
* Run `$ terraform plan --var "region=MY_REGION" --var "bucket_name=MY_BUCKET_NAME" --var "dynamodb_table_name=MY_TABLE_NAME"` -out=out.tfplan
* Run `$ terraform apply out.tfplan`

## Script Usage

### Flags

Flag Short | Flag Long | Description | Required | Type | Default Value
:--- | :--- | :--- | :--- | :--- | :--- |
-p | --profile | AWS Profile | False | string | N/A
-r | --region | AWS Region, should be the same region that was used for the Terraform deployments | False | string | N/A
-b | --bucket | S3 Bucket Name, should match the name of the S3 Bucket that was deployed via Terraform | True | string | N/A
-t | --table | DynamoDB Table Name, should match the name of the DynamoDB table that was deployed via Terraform | True | string | N/A
-s | --storage | Absolute path to Storage dir | True | string | N/A
-f | --frequency | Frequency for uploads in minutes | False | integer | 10
-m | --mode | Which mode to run purge / push / pull/ sync | True | string | sync
-z | --zip-path | List of paths to be compressed | False | string | N/A

### Modes

The tool can run in one of the following modes:

Mode | Description |
:--- | :--- |
purge | Delete all objects from S3 Bucket (use with care)
pull | Download any objects in S3 Bucket that are not in local directory
push | Upload any objects to S3 Bucket that are not already in S3 Bucket
sync | Download any objects in S3 Bucket that are not in local directory and upload any objects to S3 Bucket that are not already in S3 Bucket

### How to Run

Example:

* ```python3 /home/liamshort/Desktop/repos/liamshort-storage/script.py --profile my-profile --region eu-west-2 --bucket my-bucket --storage "/home/liamshort/Desktop/my-storage-dir/" --frequency 15 --table my-dynamodb-table --mode sync```

### Automate with Cron Job

Create a cron job to run the script at desired intervals. More info on Cron [here](https://man7.org/linux/man-pages/man5/crontab.5.html).

To do this run:

* ```crontab -u <USERNAME> -e```

Adding the below runs the script every 15 minutes: 

* ```*/15 * * * * python3 script.py ...```

NOTE: The frequency defined for the Cron Job must match the value provided for the `frequency` flag.

## Disclaimer

Please take caution when using this tool, I take no responsibility for any lost data.
