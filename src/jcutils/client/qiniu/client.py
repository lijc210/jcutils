import json

import requests

try:
    from qiniu import Auth, BucketManager, put_file_v2
except ImportError:
    raise ImportError("请先安装：pip install qiniu or uv add qiniu")


class QiniuClient:
    """
    need download boto3 module
    """

    def __init__(self, access_key="", secret_key=""):
        self.access_key = access_key
        self.secret_key = secret_key

        self.q = Auth(access_key, secret_key)

    def list_buckets(self, region="z2"):
        """ """
        bucket = BucketManager(self.q)
        # 指定需要列举的区域，填空字符串返回全部空间，为减少响应时间建议不为空
        # z0:只返回华东区域的空间
        # z1:只返回华北区域的空间
        # z2:只返回华南区域的空间
        # na0:只返回北美区域的空间
        # as0:只返回东南亚区域的空间

        ret, info = bucket.list_bucket(region)
        bucket_list = []
        for item in ret:
            bucket_list.append(item["id"])
        return bucket_list

    def list_objects(self, bucket_name, prefix, limit=10):
        """
        用来列举出该目录下的所有文件
        args:
            bucket_name: 桶名
            prefix: 要查询的文件夹路径
            limit: 每次查询的最大文件数
        returns:
            该目录下所有文件列表
        """
        bucket = BucketManager(self.q)
        marker = None
        delimiter = None
        ret, eof, info = bucket.list(bucket_name, prefix, marker, limit, delimiter)
        items = ret.get("items", [])
        file_list = []
        for item in items:
            file_list.append(item["key"])
        return file_list

    def upload_file(
        self,
        local_path,
        bucket_name,
        object_name,
    ):
        """
        上传文件到七牛
        args:
            local_path: 本地文件路径
            bucket_name: 桶名
            object_name: 上传到七牛后保存的文件名
        """
        token = self.q.upload_token(bucket_name, object_name, 3600)
        ret, info = put_file_v2(
            token,
            object_name,
            local_path,
            # metadata=object_metadata
        )
        # print(ret)
        # print(info)
        return True

    def download_file(self, bucket_name, object_name, local_path):
        bucket = BucketManager(self.q)

        ret, info = bucket.bucket_domain(bucket_name)
        print(info)
        # print(info.text_body[0])
        bucket_domain = json.loads(info.text_body)[0]

        base_url = "http://%s/%s" % (bucket_domain, object_name)
        # print(base_url)
        private_url = self.q.private_download_url(base_url, expires=3600)

        # print(private_url)
        r = requests.get(private_url)
        assert r.status_code == 200
        # 保存到本地
        with open(local_path, "wb") as f:
            f.write(r.content)
        return True


if __name__ == "__main__":
    import os

    access_key = ""
    secret_key = ""

    s3_buk = QiniuClient(access_key=access_key, secret_key=secret_key)

    file_list = s3_buk.list_buckets(region="z2")
    print(file_list)

    BUCKET_NAME = "backup-cloud-server"

    # file_list = s3_buk.list_objects(BUCKET_NAME, "")
    # print(file_list)

    # # # 上传
    # local_path1 = os.path.join(os.getcwd(), "src/jcutils/client/s3/qiniu_client.py")
    # # s3_buk.upload_file(local_path1, BUCKET_NAME, "qiniu_client.py")

    # 下载
    local_path2 = os.path.join(os.getcwd(), "src/jcutils/client/s3/qiniu_client_tmp.py")
    s3_buk.download_file(BUCKET_NAME, "qiniu_client.py", local_path2)
