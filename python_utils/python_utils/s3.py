import boto3
import threading
import sys
import os
import yaml
from urllib.parse import urlparse
from python_utils.logger import logger_console
from python_utils.config import app_config


class ProgressPercentage(object):
    """
    Provides callback functionality to track download progress
    """

    def __init__(self, filename):
        self._filename = filename
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        # To simplify we'll assume this is hooked up
        # to a single filename.
        with self._lock:
            self._seen_so_far += bytes_amount
            sys.stdout.write(
                "\r%s --> %s bytes transferred" % (
                    self._filename, self._seen_so_far))
            sys.stdout.flush()


class S3Hook:
    """
    A very simple s3 hook, from airflow hooks. Stripped airflow components for minimal dependencies.
    """

    def __init__(self):
        self._a_key = app_config['s3']['access_key_id']
        self._s_key = app_config['s3']['secret_access_key']
        self._location = app_config['s3']['region']
        self.s3 = self.get_conn()

    def get_conn(self):
        """
               Returns the boto S3Connection object.
        """
        connection = boto3.client('s3',
                               aws_access_key_id=self._a_key,
                               aws_secret_access_key=self._s_key,
                               region_name=self._location)
        return connection

    def upload_file(self, filename: str, bucket_name: str, key_name: str):
        """

        Args:
            filename: name of local file to upload
            bucket_name:  name of S3 Bucket
            key_name:  Key name for file in S3 Bucket

        Returns:


        Example Usage:
            upload_file('tmp.txt','data','tmp_data.txt')

        """
        try:
            self.s3.upload_file(filename, bucket_name, key_name)
        except Exception as e:
            raise RuntimeError("Unable to upload file, reason: {}".format(e))

    def download_file(self, bucket_name: str, key_name: str, filename: str = None):
        """

        Args:
            bucket_name:  name of S3 Bucket
            key_name:  Key name for file in S3 Bucket
            filename: name of file to be downloaded as, defaults to key_name

        Returns:


        Example Usage:
            download_file('data','tmp_data.txt')

        """
        if not filename:
            filename = key_name
        try:
            # Uncomment if use of multi-threading is ok
            self.s3.download_file(bucket_name, key_name, filename, Callback=ProgressPercentage(filename))
        except Exception as e:
            logger_console.error(e)

    def download_all_files(self, bucket_name: str, folder_name: str, to_append: bool=True):
        """
        Download all files from a bucket with specified prefix folder
        :param bucket_name: name of the S3 Bucket to download
        :param folder_name: name of the folder to download (ends with '/', otherwise S3 does not match folder)
        :param to_append: whether to append or overwrite
        :return: the list of downloaded files
        """
        downloaded = []
        paginator = self.s3.get_paginator('list_objects')
        for result in paginator.paginate(Bucket=bucket_name, Delimiter='/', Prefix=folder_name):
            if result.get('Contents') is None:
                continue
            for filename in result.get('Contents'):
                local_file_name = '/tmp/' + filename.get('Key')
                if os.path.exists(local_file_name):
                    if to_append:
                        # if the file is downloaded, we assume it was successful
                        downloaded.append(local_file_name)
                        continue
                    else:
                        try:
                            os.remove(local_file_name)
                        except:
                            logger_console.error("Unable to remove the file {} to re-download"
                                                   .format(local_file_name))
                            return

                local_dir_name = '/tmp/' + folder_name
                if not os.path.exists(local_dir_name):
                    # create the folder
                    os.makedirs(local_dir_name)
                try:
                    self.s3.download_file(bucket_name, filename.get('Key'), local_file_name)
                except Exception as e:
                    if os.path.exists(local_file_name):
                        # we need to delete the failed file
                        try:
                            os.remove(local_file_name)
                        except:
                            logger_console.error("Unable to remove partially downloaded file {}"
                                                   .format(local_file_name))
                            return
                    logger_console.error("Unable to download file, reason: {}".format(e))
                    return
                downloaded.append(local_file_name)
        return downloaded

    def delete_local(self, bucket_name: str, folder_name: str):
        """
        Delete all files from a bucket with specified prefix folder in local cache
        :param bucket_name: name of the S3 Bucket to download
        :param folder_name: name of the folder to download (ends with '/', otherwise S3 does not match folder)
        :return: the list of deleted files
        """
        local_dir_name = '/tmp/' + folder_name
        if not os.path.exists(local_dir_name):
            return []

        deleted = []
        paginator = self.s3.get_paginator('list_objects')
        for result in paginator.paginate(Bucket=bucket_name, Delimiter='/', Prefix=folder_name):
            if result.get('Contents') is None:
                continue
            for filename in result.get('Contents'):

                local_file_name = '/tmp/' + filename.get('Key')

                if not os.path.exists(local_file_name):
                    continue
                try:
                    os.remove(local_file_name)
                    deleted.append(local_file_name)
                except:
                    logger_console.error("Unable to remove the file {}".format(local_file_name))
                    return
        return deleted

    def delete_remote(self, bucket_name: str, folder_name: str):
        """
        Delete all files from a bucket with specified prefix folder in S3
        :param bucket_name: name of the S3 Bucket to download
        :param folder_name: name of the folder to download (ends with '/', otherwise S3 does not match folder)
        :return: the list of deleted files
        """
        paginator = self.s3.get_paginator('list_objects')

        logger_console.info('bucket_name {}, folder_name {}'.format(bucket_name, folder_name))

        keys_to_delete = []
        for result in paginator.paginate(Bucket=bucket_name, Delimiter='/', Prefix=folder_name):
            if result.get('Contents') is None:
                continue
            for filename in result.get('Contents'):
                keys_to_delete.append({'Key': filename.get('Key')})

        logger_console.info('keys_to_delete : {}'.format(keys_to_delete))
        if not keys_to_delete:
            return []
        response = self.s3.delete_objects(Bucket=bucket_name, Delete={'Objects': keys_to_delete, 'Quiet': True})
        deleted = [elem['Key'] for elem in response.get('Deleted', [])]
        if len(deleted) != len(keys_to_delete):
            return response.get('Errors', [])
        return deleted
