# CHANGELOG

## 0.3.0

### Removed

* Slack functionality

### Added

* Creates optional SNS Topic
* Lambda function will forward to an SNS Topic

## 0.2.2

### Fixed

* Default Cron expression for Cloudwatch Event Rule

### Updated

* Terraform command in README

## 0.2.1

### Fixed

* Permissions to allow Cloudwatch Events Rule to invoke Lambda Function

## 0.2.0

### Added

* Cloudwatch Event Rule to trigger Lambda function daily
* Lambda function that checks for any photos from that day on previous years and sends to Slack

## 0.1.4

### Added

* Pillow to requirements
* File extension stored in DynamoDB
* If file is an image, try to retrieve the date it was taken and store in DynamoDB

## 0.1.3

### Added

* Ability to pull all objects to a new empty directory
* When downloading files from S3, will create a local dir for path if not exists

## 0.1.2

### Added

* Count for pull, push, purge
* Log statements for counts
* Conditional API calls based on counts

## 0.1.1

### Updated

* Bucket Versioning default value from False to True
* Variable descriptions

### Added

* Bucket encryption variables
* DynamodDB default write capacity set to 5
* DynamodDB default read capacity set to 5
* DynamodDB default billing mode set to PROVISIONED

## 0.1.0

### Added

* Initial code
