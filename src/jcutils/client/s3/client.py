import hashlib
import math
import os

import boto3
from boto3.s3.transfer import TransferConfig
from botocore.exceptions import ClientError


class S3Bucket:
    """
    need download boto3 module
    """

    def __init__(self, config=None):
        self.access_key = config.get("ACCESS_KEY")
        self.secret_key = config.get("SECRET_KEY")
        self.url = config.get("ENDPOINT_URL")

        # 连接s3
        self.s3 = boto3.client(
            service_name="s3",
            region_name=None,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            endpoint_url=self.url,
        )

    def list_buckets(self):
        """ """
        response = self.s3.list_buckets()
        Buckets = response["Buckets"]
        return Buckets

    def upload_normal(self, bucket_name, path_prefix, file_upload):
        """
        ##小文件上传-上传本地文件到s3指定文件夹下
        """
        GB = 1024**3
        # default config
        config = TransferConfig(
            multipart_threshold=5 * GB, max_concurrency=10, use_threads=True
        )  # 10默认，增加数值增加带宽
        file_name = os.path.basename(file_upload)
        object_name = os.path.join(path_prefix, file_name)
        print("-----begin to upload!----")
        try:
            self.s3.upload_file(file_upload, bucket_name, object_name, Config=config)
        except ClientError as e:
            print("error happend!" + str(e))
            return False
        print("upload done!")
        return True

    def upload_files(self, bucket_name, path_bucket, path_local):
        """
        ##大文件上传
        args:
          path_bucket: bucket桶下的路径，文件上传dir
          path_local: 待上传文件的绝对路径
        """
        # multipart upload
        chunk_size = 52428800
        source_size = os.stat(path_local).st_size
        print("source_size=", source_size)
        chunk_count = int(math.ceil(source_size / float(chunk_size)))
        mpu = self.s3.create_multipart_upload(Bucket=bucket_name, Key=path_bucket)
        part_info = {"Parts": []}
        with open(path_local, "rb") as fp:
            for i in range(chunk_count):
                offset = chunk_size * i
                bytes = min(chunk_size, source_size - offset)
                data = fp.read(bytes)
                md5s = hashlib.md5(data)
                new_etag = '"%s"' % md5s.hexdigest()
                try:
                    self.s3.upload_part(
                        Bucket=bucket_name,
                        Key=path_bucket,
                        PartNumber=i + 1,
                        UploadId=mpu["UploadId"],
                        Body=data,
                    )
                except Exception as exc:
                    print("error occurred.", exc)
                    return False
                print("uploading {} {}".format(path_local, str(i / chunk_count)))
                parts = {"PartNumber": i + 1, "ETag": new_etag}
                part_info["Parts"].append(parts)
        print("%s uploaded!" % (path_local))
        self.s3.complete_multipart_upload(
            Bucket=bucket_name,
            Key=path_bucket,
            UploadId=mpu["UploadId"],
            MultipartUpload=part_info,
        )
        print("%s uploaded success!" % (path_local))
        return True

    def download_file(self, bucket_name, object_name, path_local):
        """
        download the single file from s3 to local dir
        """
        GB = 1024**3
        config = TransferConfig(multipart_threshold=2 * GB, max_concurrency=10, use_threads=True)
        suffix = object_name.split(".")[-1]
        if path_local[-len(suffix) :] == suffix:
            file_name = path_local
            dir_name = os.path.dirname(file_name)
            if not os.path.exists(dir_name):
                os.mkdir(dir_name)
        else:
            if not os.path.exists(path_local):
                os.mkdir(path_local)
            file_name = os.path.join(path_local, os.path.basename(object_name))
        print(object_name, file_name)
        try:
            self.s3.download_file(bucket_name, object_name, file_name, Config=config)
        except Exception as exc:
            print("some wrong!")
            print("error occurred.", exc)
            return False
        print("downlaod ok", object_name)
        return True

    def download_files(self, bucket_name, path_prefix, path_local):
        """
        批量文件下载
        """
        GB = 1024**3
        config = TransferConfig(multipart_threshold=2 * GB, max_concurrency=10, use_threads=True)
        list = self.s3.list_objects_v2(Bucket=bucket_name, Prefix=path_prefix)["Contents"]
        for key in list:
            name = os.path.basename(key["Key"])
            object_name = key["Key"]
            print("-----", object_name, name)
            if not os.path.exists(path_local):
                os.makedirs(path_local)
            file_name = os.path.join(path_local, name)
            try:
                self.s3.download_file(bucket_name, object_name, file_name, Config=config)
            except Exception as exc:
                print("error occurred.", exc)
                return False
        return True

    def get_list_s3(self, bucket_name, obj_floder_path):
        """
        用来列举出该目录下的所有文件
        args:
            obj_floder_path: 要查询的文件夹路径
        returns:
            该目录下所有文件列表
        """
        # 用来存放文件列表
        file_list = []
        response = self.s3.list_objects_v2(
            Bucket=bucket_name,
            Prefix=obj_floder_path,
            # Delimiter='',
            MaxKeys=1000,
        )
        # print(response)
        for adict in response["Contents"]:
            file_list.append(adict["Key"])
        return file_list


if __name__ == "__main__":
    S3_FILE_CONF = {
        "ACCESS_KEY": "xxx",
        "SECRET_KEY": "xxxxxxx",
        "ENDPOINT_URL": "https://ea2399efdad8c26cba1f231fdeec938b.r2.cloudflarestorage.com",
    }
    BUCKET_NAME = "file"
    s3_buk = S3Bucket(S3_FILE_CONF)
    print(s3_buk.list_buckets())

    file_list = s3_buk.get_list_s3(BUCKET_NAME, "")
    print(file_list)

    # 上传
    s3_buk.upload_normal(BUCKET_NAME, "", "src/package/boto3_test/updown_s3.py")

    # 下载
    s3_buk.download_file(BUCKET_NAME, "520-happy_0.0.2_x64.dmg", "src/package/boto3_test/")
