# coding: utf-8
"""
@File    :   dataworks_client.py
@Time    :   2023/10/13 15:30:08
@Author  :   lijc210@163.com
@Desc    :   None
"""

from alibabacloud_dataworks_public20200518.client import (
    Client as dataworks_public20200518Client,
)
from alibabacloud_tea_openapi import models as open_api_models


class DataworksClient:
    def __init__(self):
        pass

    @staticmethod
    def create_client(
        access_key_id: str,
        access_key_secret: str,
    ) -> dataworks_public20200518Client:
        """
        使用AK&SK初始化账号Client
        @param access_key_id:
        @param access_key_secret:
        @return: Client
        @throws Exception
        """
        config = open_api_models.Config(
            # 必填，您的 AccessKey ID,
            access_key_id=access_key_id,
            # 必填，您的 AccessKey Secret,
            access_key_secret=access_key_secret,
        )
        # Endpoint 请参考 https://api.aliyun.com/product/dataworks-public
        config.endpoint = "dataworks.cn-beijing.aliyuncs.com"
        return dataworks_public20200518Client(config)


if __name__ == "__main__":
    pass
