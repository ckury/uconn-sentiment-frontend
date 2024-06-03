'''
storage.py module for UCONN Sentiment Analysis

This module interfaces with GCP storage to do the following:

uploadFile -> Uploads file

Note: GCP credentials need to be set as environmental variable when running the python program

author: Charlie Kuryluk
date: 6/3/2024

'''
from google.cloud import storage

storageClient = storage.Client()

def uploadFile(bucket_name: storage.Bucket, file):
    ''' uploadFile() takes the following arguments:

        - bucket_name: String of name of bucket (required)
        - file: FileStorage object (required)

        Does not return value.

    '''
    
    bucket = storageClient.get_bucket(bucket_name)
    blob = bucket.blob(file.filename)

    blob.upload_from_file(file)

    return