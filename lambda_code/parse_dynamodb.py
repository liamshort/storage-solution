import os
import boto3
import json
import urllib
from datetime import datetime
from dateutil.relativedelta import relativedelta
from botocore.vendored import requests


def lambda_handler(event, context):
    session = boto3.Session()
    
    s3_client = boto3.client("s3")
    dynamodb_client = session.resource("dynamodb")
    sns_client = session.client("sns")

    index_table = dynamodb_client.Table(os.environ["table_name"])
    response = index_table.scan()
    
    index_items_json = {}
    for item in response['Items']:
        index_items_json[item["name"]] = {
            "path": item["path"],
            "image_date": item["image_date"]
        }
    
    years = []
    for this_year in range(int(os.environ["years_back"])):
        years_ago_today = (datetime.now() - relativedelta(years=int(this_year))).strftime("%Y-%m-%d")
        years.append(years_ago_today)
    
    presigned_url_json = {}
    for key, value in index_items_json.items():
        if str(value["image_date"]) in str(years):
            presigned_url = s3_client.generate_presigned_url(
                'get_object', 
                Params = {
                    'Bucket': os.environ["s3_bucket"], 
                    'Key': value["path"]
                }, 
                ExpiresIn = os.environ["presigned_url_expiration"], 
                HttpMethod = None
            )
            
            presigned_url_json[key] = {"url": presigned_url}
        
    if presigned_url_json != {}:
        sns_client.publish(
            TopicArn = os.environ["sns_topic_arn"],
            Message = json.dumps({"default": str(presigned_url_json)}),
            Subject = "Daily Pic - " + str(datetime.now().strftime("%Y-%m-%d")),
            MessageStructure = "json"
        )
