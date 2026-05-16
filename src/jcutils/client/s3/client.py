import hashlib
import math
import os

try:
    import boto3
    from boto3.s3.transfer import TransferConfig
    from botocore.exceptions import ClientError
except ImportError:
    raise ImportError("请先安装：pip install boto3 or uv add boto3")


class S3Bucket:
    """
    need download boto3 module
    """

    def __init__(self, access_key="", secret_key="", endponint=""):
        self.access_key = access_key
        self.secret_key = secret_key
        self.endponint = endponint

        # 连接s3
        self.s3 = boto3.client(
            service_name="s3",
            region_name=None,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            endpoint_url=self.endponint,
        )

    def list_buckets(self):
        """ """
        response = self.s3.list_buckets()
        Buckets = response["Buckets"]
        bucket_list = []
        for bucket in Buckets:
            bucket_list.append(bucket["Name"])
        return bucket_list

    def list_objects(self, bucket_name, obj_floder_path):
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

    def upload_file(
        self,
        local_path,
        bucket_name,
        object_name,
    ):
        """
        ##小文件上传-上传本地文件到s3指定文件夹下
        """
        GB = 1024**3
        # default config
        config = TransferConfig(
            multipart_threshold=5 * GB, max_concurrency=10, use_threads=True
        )  # 10默认，增加数值增加带宽

        print("-----begin to upload!----")
        try:
            self.s3.upload_file(local_path, bucket_name, object_name, Config=config)
        except ClientError as e:
            print("error happend!" + str(e))
            return False
        print("upload done!")
        return True

    def upload_files(self, bucket_name, path_bucket, local_path):
        """
        ##大文件上传
        args:
          path_bucket: bucket桶下的路径，文件上传dir
          path_local: 待上传文件的绝对路径
        """
        # multipart upload
        chunk_size = 52428800
        source_size = os.stat(local_path).st_size
        print("source_size=", source_size)
        chunk_count = int(math.ceil(source_size / float(chunk_size)))
        mpu = self.s3.create_multipart_upload(Bucket=bucket_name, Key=path_bucket)
        part_info = {"Parts": []}
        with open(local_path, "rb") as fp:
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
                print("uploading {} {}".format(local_path, str(i / chunk_count)))
                parts = {"PartNumber": i + 1, "ETag": new_etag}
                part_info["Parts"].append(parts)
        print("%s uploaded!" % (local_path))
        self.s3.complete_multipart_upload(
            Bucket=bucket_name,
            Key=path_bucket,
            UploadId=mpu["UploadId"],
            MultipartUpload=part_info,
        )
        print("%s uploaded success!" % (local_path))
        return True

    def download_file(self, bucket_name, object_name, local_path):
        """
        download the single file from s3 to local dir
        """
        GB = 1024**3
        config = TransferConfig(multipart_threshold=2 * GB, max_concurrency=10, use_threads=True)
        suffix = object_name.split(".")[-1]
        if local_path[-len(suffix) :] == suffix:
            file_name = local_path
            dir_name = os.path.dirname(file_name)
            if not os.path.exists(dir_name):
                os.mkdir(dir_name)
        else:
            if not os.path.exists(local_path):
                os.mkdir(local_path)
            file_name = os.path.join(local_path, os.path.basename(object_name))
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


if __name__ == "__main__":
    BUCKET_NAME = "file"
    access_key = ""
    secret_key = ""
    endpoint_url = ""
    s3_buk = S3Bucket(access_key=access_key, secret_key=secret_key, endponint=endpoint_url)
    print(s3_buk.list_buckets())

    file_list = s3_buk.list_objects(BUCKET_NAME, "")
    print(file_list)

    # # # 上传
    # local_path = os.path.join(os.getcwd(), "src/jcutils/client/s3/client.py")
    # s3_buk.upload_file(local_path, BUCKET_NAME, "client.py")

    # # # 下载
    # s3_buk.download_file(BUCKET_NAME, "client.py", local_path)
