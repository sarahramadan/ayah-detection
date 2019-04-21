#!/usr/bin/env python2
from os import environ as env
from os.path import basename
from os import stat as fstat
import argparse
from glob import glob
import boto3
from botocore.client import Config
import requests
from tqdm import tqdm


def parse_arguments():
  parser = argparse.ArgumentParser()
  parser.add_argument('--input_path', type=str, required=True,
                      help='''Path to input folder containing archives to upload to S3''')
  parser.add_argument('--aws_region_name', type=str, required=True,
                      help='''AWS region name''')
  parser.add_argument('--aws_s3_endpoint_url', type=str, required=False,
                      help='''AWS S3 endpoint URL, if different from the default (e.g. DigitalOcean)''')
  parser.add_argument('--aws_s3_public_base_url', type=str, required=True,
                      help='''Public URL prefix to verify uploaded archives''')
  parser.add_argument('--aws_s3_bucket', type=str, required=True,
                      help='''AWS S3 Bucket''')
  parser.add_argument('--aws_s3_object_prefix', type=str, required=True,
                      help='''AWS S3 object prefix (parent folder)''')

  return parser.parse_args()


def get_client(region_name, aws_access_key_id, aws_secret_access_key, endpoint_url=None):
  # Initialize a session using DigitalOcean Spaces
  session = boto3.session.Session()
  client = session.client('s3',
                          region_name=region_name,
                          endpoint_url=endpoint_url,
                          aws_access_key_id=aws_access_key_id,
                          aws_secret_access_key=aws_secret_access_key)
  return client


def upload_archive(client, bucket, object_key, file_name):
  # upload object printing progress, then set its ACL

  total_size = fstat(file_name).st_size
  pbar = tqdm(total=total_size, unit_scale=True, unit_divisor=1024, unit='B')

  with open(file_name, 'rb') as file:
    client.upload_fileobj(file, Bucket=bucket,
                          Key=object_key, Callback=pbar.update)
  pbar.close()
  client.put_object_acl(Bucket=bucket, Key=object_key, ACL='public-read')
  return total_size


def verify_archive(base_url, object_key, file_name, total_size):
  # verify upload:
  url = "%s/%s" % (base_url, object_key)
  response = requests.head(url)
  if response.status_code != 200:
    raise RuntimeError("File could not be publicly accessed, returned HTTP status code: %d" % response.status_code)
  content_size = int(response.headers['content-length'])
  if content_size != total_size:
    raise RuntimeError("Uploaded file size (%d) does not match original size (%d)" % (content_size, total_size))
  print("OK")

def loop_input_folder(client, base_url, prefix, bucket, input_path):
  for file_name in glob(input_path + "/*"):
    file_base_name = basename(file_name)
    object_key = "%s%s" % (prefix, file_base_name)
    print("Uploading %s:" % file_base_name)
    total_size = upload_archive(client, bucket, object_key, file_name)
    print("Verifying upload...")
    verify_archive(base_url, object_key, file_name, total_size)


if __name__ == "__main__":
  args = parse_arguments()
  client = get_client(region_name=args.aws_region_name,
                      aws_access_key_id=env['AWS_ACCESS_KEY_ID'],
                      aws_secret_access_key=env['AWS_SECRET_ACCESS_KEY'],
                      endpoint_url=args.aws_s3_endpoint_url)
  loop_input_folder(client=client,
                    base_url=args.aws_s3_public_base_url,
                    prefix=args.aws_s3_object_prefix,
                    bucket=args.aws_s3_bucket,
                    input_path=args.input_path)
