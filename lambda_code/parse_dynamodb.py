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
    
    for key, value in index_items_json.items():
        if str(value["image_date"]) in str(years):
            presigned_url = s3_client.generate_presigned_url(
                'get_object', 
                Params={
                    'Bucket': os.environ["s3_bucket"], 
                    'Key': value["path"]
                }, 
                ExpiresIn=os.environ["presigned_url_expiration"], 
                HttpMethod=None
            )
            
            message = create_slack_message(presigned_url, value["image_date"])
            
            requests.post(
                os.environ["slack_webhook"], data= json.dumps(message),
                headers={"Content-Type": "application/json"},
            )


def create_slack_message(presigned_url, image_date):
    message = {
        "icon_url": "https://github.com/liamshort/assets/blob/master/images/cloud_black.png?raw=true",
        "username": "Storage-Solution",
        "channel": os.environ["slack_channel"],
        "attachments": [{
            "title": image_date,
            "image_url": presigned_url
            }
        ]}
    
    return(message)
