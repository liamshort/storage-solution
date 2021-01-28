import os
import boto3
import shutil
import argparse
import datetime
import time
import json
from datetime import datetime, timedelta
import logging
import zipfile
from PIL import Image
from PIL.ExifTags import TAGS

logFormatter = '%(asctime)s - %(message)s'
logging.basicConfig(format=logFormatter, level=logging.INFO)
logger = logging.getLogger(__name__)

image_extensions = ["jpeg", "jpg", "png"]


def _configure():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('-p', '--profile', help='AWS Profile', nargs='?', dest="aws_profile", required=False, type=str)
    parser.add_argument('-r', '--region', help='AWS Region', nargs='?', dest="aws_region", required=False, type=str)
    parser.add_argument('-b', '--bucket', help='S3 Bucket Name', nargs='?', dest="bucket_name", required=True, type=str)
    parser.add_argument('-t', '--table', help='DynamoDB Name', nargs='?', dest="table_name", required=True, type=str)
    parser.add_argument('-s', '--storage', help='Absolute path to Storage dir', nargs='?', dest="storage_path", required=True, type=str)
    parser.add_argument('-f', '--frequency', help='Frequency for uploads in minutes', nargs='?', dest="frequency", required=False, default=10, type=int)
    parser.add_argument('-m', '--mode', help='Which mode to run purge / push / pull/ sync', nargs='?', dest="mode", required=True, default='sync', type=str)
    parser.add_argument('-z', '--zip-path', help='List of paths to be compressed', nargs='?', dest="zip_path", required=False, type=str)
    args = vars(parser.parse_args())

    aws_profile = args["aws_profile"]
    aws_region = args["aws_region"]
    bucket_name = args["bucket_name"]
    table_name = args["table_name"]
    storage_path = args["storage_path"]
    frequency = args["frequency"]
    mode = args["mode"]
    zip_path = args["zip_path"]

    return aws_profile, aws_region, bucket_name, table_name, storage_path, frequency, mode, zip_path


def main(aws_profile, aws_region, bucket_name, table_name, storage_path, frequency, mode, zip_path):

    if aws_profile == "":
        session = boto3.Session()
    else:
        session = boto3.Session(profile_name=aws_profile)

    if aws_region == "":
        s3_client = session.client("s3")
        dynamodb_client = session.client("dynamodb")
    else:
        s3_client = session.client("s3", region_name=aws_region)
        dynamodb_client = session.resource("dynamodb", region_name=aws_region)

    index_table = dynamodb_client.Table(table_name)
    index_items_json = get_index_items_json(index_table)

    if mode == "purge":
        logger.info(f"Running {mode} mode")
        purge_object_count = run_purge(s3_client, index_items_json, bucket_name, index_table)
        logger.info(f"{purge_object_count} Deleted")

    if mode == "pull":
        logger.info(f"Running {mode} mode")
        exceptions, pull_object_count = run_pull(s3_client, index_table, index_items_json, bucket_name, storage_path, frequency)
        logger.info(f"{pull_object_count} Downloaded")

    if mode == "push":
        logger.info(f"Running {mode} mode")
        exceptions = []
        put_object_count, purge_object_count = run_push(storage_path, s3_client, index_table, bucket_name, frequency, index_items_json, zip_path, exceptions)
        logger.info(f"{put_object_count} Uploaded")
        logger.info(f"{purge_object_count} Deleted")
        
    if mode == "sync":
        logger.info(f"Running {mode} mode")
        exceptions, pull_object_count = run_pull(s3_client, index_table, index_items_json, bucket_name, storage_path, frequency)
        
        if pull_object_count != 0:
            index_items_json = get_index_items_json(index_table)
            
        put_object_count, purge_object_count = run_push(storage_path, s3_client, index_table, bucket_name, frequency, index_items_json, zip_path, exceptions)
        logger.info(f"{pull_object_count} Downloaded")
        logger.info(f"{put_object_count} Uploaded")
        logger.info(f"{purge_object_count} Deleted")

    logger.info("Run Complete")


def run_purge(s3_client, index_items_json, bucket_name, index_table):
    purge_object_count = 0
    
    for key, value in index_items_json.items():
        delete_remote_object(s3_client, bucket_name, value["path"])
        delete_index_item(index_table, key)
        purge_object_count = purge_object_count + 1
        
    return purge_object_count


def run_pull(s3_client, index_table, index_items_json, bucket_name, storage_path, frequency):
    index_items_list = []
    exceptions = []
    pull_object_count = 0
    
    for key, value in index_items_json.items():
        index_items_list.append(value["path"])
        
    s3_objects = s3_client.list_objects(
        Bucket=bucket_name
        )
    if "Contents" in s3_objects:
        original_storage_path_contents = len(os.listdir(storage_path))
        for s3_object in s3_objects["Contents"]:
            if (s3_object["Key"] not in index_items_list) or (original_storage_path_contents == 0):
                path_rel = s3_object["Key"]
                path_abs = storage_path + path_rel
                filename = os.path.basename(path_rel)
                file_extension = os.path.splitext(path_rel)[-1].replace(".","")
                exceptions.append(path_rel)
                dirname, fname = os.path.split(path_abs)
                if not os.path.exists(dirname):
                    os.makedirs(dirname)
                    
                get_remote_object(s3_client, bucket_name, path_rel, path_abs)
                modified_time, modified_within_time, modified_time_formatted = get_object_mod_times(os.path.getmtime(path_abs), frequency)
                unique_name = modified_time_formatted + filename
                create_index_item(index_table, unique_name, path_rel, modified_time, file_extension, image_date)
                pull_object_count = pull_object_count + 1
            
    return exceptions, pull_object_count


def run_push(storage_path, s3_client, index_table, bucket_name, frequency, index_items_json, zip_path, exceptions):
    local_objects_list = []
    put_object_count = 0
    purge_object_count = 0
    
    for (dirpath, dirs, files) in os.walk(storage_path, topdown=True):
        for filename in files:
            path_dir = os.path.relpath(dirpath, storage_path)
            path_rel = os.path.join(path_dir, filename).replace("./","")
            path_abs = os.path.join(dirpath, filename)
            file_extension = os.path.splitext(path_rel)[-1].replace(".","")
            
            local_objects_list.append(path_rel)
            
            modified_time, modified_within_time, modified_time_formatted = get_object_mod_times(os.path.getmtime(path_abs), frequency)
            unique_name = modified_time_formatted + filename
            
            original_name = ""
            for key, value in index_items_json.items():
                if path_rel == value["path"]:
                    original_name = datetime.strftime((datetime.strptime(value["modified_time"], "%Y-%m-%d %H:%M:%S")), "%d%m%Y%H%M%S") + filename
                    if (modified_within_time is True) and (path_rel not in exceptions):
                        if file_extension in image_extensions:
                            image_date = get_image_metadata(path_abs)
                        else:
                            image_date = None
                        delete_remote_object(s3_client, bucket_name, path_rel)
                        put_remote_object(s3_client, bucket_name, path_abs, path_rel)
                        delete_index_item(index_table, original_name)
                        create_index_item(index_table, unique_name, path_rel, modified_time, file_extension, image_date)
                        purge_object_count = purge_object_count + 1
                        put_object_count = put_object_count + 1
                    
            if (unique_name and original_name) not in index_items_json:
                if file_extension in image_extensions:
                    image_date = get_image_metadata(path_abs)
                else: 
                    image_date = None
                put_remote_object(s3_client, bucket_name, path_abs, path_rel)
                create_index_item(index_table, unique_name, path_rel, modified_time, file_extension, image_date)
                put_object_count = put_object_count + 1

    if put_object_count != 0:  
        index_items_json_updated = get_index_items_json(index_table)
        for key, value in index_items_json_updated.items():
            if (value["path"] not in local_objects_list) and (value["extension"] != "zip"):
                delete_remote_object(s3_client, bucket_name, value["path"])
                delete_index_item(index_table, str(key))
                purge_object_count = purge_object_count + 1
                
    return put_object_count, purge_object_count

    # ZIP FUNCTIONALITY IS WIP
    if zip_path is not None:
        zip_path_list = zip_path.split(",")
        for item in zip_path_list:
            if os.path.exists(storage_path + item):
                modified_time, modified_within_time, modified_time_formatted = get_object_mod_times(os.path.getmtime(storage_path + item), frequency)
                if modified_within_time is True:
                    zip_path, zip_path_abs, zip_path_rel, zip_name = put_zip_object(storage_path, item)
                    unique_zip_name = modified_time_formatted + zip_name
                    put_remote_object(s3_client, bucket_name, zip_path_abs, zip_path_rel)
                    create_index_item(index_table, unique_zip_name, zip_path_rel, modified_time_formatted, "zip", image_date)
                    os.remove(zip_path_abs)


def get_image_metadata(path_abs):
    date_captured_formatted = None
    image = Image.open(path_abs)
    exifdata = image.getexif()
    for tag_id in exifdata:
        tag = TAGS.get(tag_id, tag_id)
        if tag == "DateTimeOriginal":
            date_captured_raw = exifdata.get(tag_id)
            if isinstance(date_captured_raw, bytes):
                date_captured_raw = date_captured.decode()
            date_captured = datetime.strptime(date_captured_raw, "%Y:%m:%d %H:%M:%S")
            date_captured_formatted = date_captured.strftime("%Y-%m-%d %H:%M:%S")
            break
    
    return date_captured_formatted


def get_object_mod_times(abs_path, frequency):
    modified_time = datetime.strptime(time.ctime(abs_path), "%a %b %d %H:%M:%S %Y")
    anchor_time = datetime.now() - timedelta(minutes=frequency)
    modified_within_time = anchor_time < modified_time
    modified_time_formatted = modified_time.strftime("%d%m%Y%H%M%S") 

    return modified_time, modified_within_time, modified_time_formatted


def get_index_items_json(index_table):
    logger.info("Fetching Index Items")
    
    response = index_table.scan()
    index_items_json = {}
    for item in response['Items']:
        index_items_json[item["name"]] = {
            "path": item["path"],
            "modified_time": item["modified_time"],
            "extension": item["extension"],
            "image_date": item["image_date"]
        }

    return index_items_json


def delete_index_item(index_table, item):
    logger.info(f"Deleting Index - {item}")
    
    index_table.delete_item(
        Key={
            'name': item,
        }
    )


def create_index_item(index_table, item, path, modified_time, extension, image_date):
    logger.info(f"Creating Index - {item}")
    
    index_table.put_item(
        Item={
            "name": item,
            "path": path,
            "modified_time": str(modified_time),
            "extension": extension,
            "image_date": image_date
        }
    )


def put_remote_object(s3_client, bucket_name, path_abs, path_rel):
    logger.info(f"Uploading Object - {path_rel}")
    
    s3_client.upload_file(
        path_abs,
        bucket_name,
        path_rel
    )


def get_remote_object(s3_client, bucket_name, path_rel, filename):
    logger.info(f"Downloading Object - {path_rel}")
    
    s3_client.download_file(
        bucket_name,
        path_rel,
        filename
    )


def delete_remote_object(s3_client, bucket_name, path_rel):
    logger.info(f"Deleting Object - {path_rel}")
        
    s3_client.delete_object(
        Bucket=bucket_name,
        Key=path_rel
    )


def put_zip_object(path, item):
    zip_path = path + item
    zip_path_abs = os.path.splitext(zip_path)[0] + ".zip"
    zip_path_rel = os.path.splitext(item)[0] + ".zip"
    zip_name = os.path.basename(item).split(".")[0] + ".zip"
    logger.info(f"Zipping - {item}")
    zipfile.ZipFile(zip_path_abs, mode='w').write(zip_path)
    
    return zip_path, zip_path_abs, zip_path_rel, zip_name


if __name__ == "__main__":
    AWS_PROFILE, AWS_REGION, BUCKET_NAME, TABLE_NAME, STORAGE_PATH, FREQUENCY, MODE, ZIP_PATH = _configure()
    main(AWS_PROFILE, AWS_REGION, BUCKET_NAME, TABLE_NAME, STORAGE_PATH, FREQUENCY, MODE, ZIP_PATH)
