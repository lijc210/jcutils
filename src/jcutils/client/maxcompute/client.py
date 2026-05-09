# coding: utf-8
"""
@File    :   maxcompute_client.py
@Time    :   2023/10/13 15:30:08
@Author  :   lijc210@163.com
@Desc    :   None
"""

from alibabacloud_maxcompute20220104.client import Client as MaxCompute20220104Client
from alibabacloud_tea_openapi import models as open_api_models


class MaxComputeClient:
    def __init__(self):
        pass

    @staticmethod
    def create_client(access_key_id, access_key_secret) -> MaxCompute20220104Client:
        """
        使用AK&SK初始化账号Client
        @return: Client
        @throws Exception
        """
        # 工程代码泄露可能会导致 AccessKey 泄露，并威胁账号下所有资源的安全性。以下代码示例仅供参考。
        # 建议使用更安全的 STS 方式，更多鉴权访问方式请参见：https://help.aliyun.com/document_detail/378659.html。
        config = open_api_models.Config(
            # 必填，请确保代码运行环境设置了环境变量 ALIBABA_CLOUD_ACCESS_KEY_ID。,
            access_key_id=access_key_id,
            # 必填，请确保代码运行环境设置了环境变量 ALIBABA_CLOUD_ACCESS_KEY_SECRET。,
            access_key_secret=access_key_secret,
        )
        # Endpoint 请参考 https://api.aliyun.com/product/MaxCompute
        config.read_timeout = 60000
        config.endpoint = "maxcompute.cn-beijing.aliyuncs.com"
        return MaxCompute20220104Client(config)


if __name__ == "__main__":
    pass
