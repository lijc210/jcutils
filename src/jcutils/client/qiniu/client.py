"""
@Time   : 2018/11/26
@author : lijc210@163.com
@Desc:  : 功能描述。
"""

import hashlib

import requests
from qiniu import put_data, put_file

from utils.Tool import retry

session = requests.Session()


class Qiniu:
    def __init__(self, baseUrl="https://imgmall.tg.com.cn/", session=session):
        """
        初始化 七牛 上传
        :param baseUrl:
        :param session:
        """
        self.baseUrl = baseUrl
        self.session = session

    def get_token(self):
        """
        目前因为测试服务器无法获取 token 所以 获取了一个 长时间的token 使用
        :return:
        """
        # token_url = 'http://qiniu-token.api.tg.local/applyUploadToken' # 生产的
        # token_url = 'http://192.168.100.46:10016/applyUploadToken' # 测试的
        # resp = requests.post(token_url, json={
        #     'category': 'weibojia',
        #     'fileType': "jpg|mp4",
        #     'tokenModel': 1,
        #     "expire": 3600 * 24 * 30 * 12 *10
        # })

        # 更换了10年的 七牛 key
        return (
            "jYBEGYtO48oyqsqxdAvhA12IRrYGsMMPbDVVtnUf:AntlxE_PsQzsUcILVtggkCQdtQg=:eyJjYWxsYmFja1VybCI"
            "6Imh0dHA6Ly9xLW9wZW4uamlhLmNvbS9hcGkvc3lzL3Fpbml1Q2xvdWQvY2FsbGJhY2siLCJzY29wZSI6ImltZy1tYWxsIiwiY2FsbG"
            "JhY2tCb2R5VHlwZSI6ImFwcGxpY2F0aW9uL2pzb24iLCJjYWxsYmFja0JvZHkiOiJ7XCJmaWxlSURcIjpcIiQoa2V5KVwiLFwiZmlsZU1"
            "ENVwiOlwiJChldGFnKVwiLFwiYnVja2V0XCI6XCIkKGJ1Y2tldClcIixcIm9yaWdpbk5hbWVcIjpcIiQoZm5hbWUpXCIsXCJpbWFnZUlu"
            "Zm9cIjokKGltYWdlSW5mbyksXCJtaW1lVHlwZVwiOlwiJChtaW1lVHlwZSlcIixcInNpemVcIjokKGZzaXplKX0iLCJkZWFkbGluZSI6MTg0NTk2MzYzOH0="
        )

    def put_file(self, key, localfile):
        """
        上传文件到七牛
        :param key: 上传到七牛后保存的文件名,可以带路径
        :param localfile: 本地文件路径
        :return:
        """
        _token = self.get_token()
        ret, info = put_file(_token, key, localfile)
        print(ret, info)

    @retry(num=3)
    # @time_limit(5)
    def put_data(self, key=None, url=None, data=None):
        """
        上传二进制流到七牛
        :param key:  上传到七牛后保存的文件名,可以带路径
        :param data: 二进制流
        :return:
        """
        _token = self.get_token()
        md5key = hashlib.md5(key.encode()).hexdigest()
        file_name = md5key + ".jpg"

        if url:
            resp = self.session.get(url)
            if resp.status_code == 200:
                data = resp.content
        new_url = ""
        if data:
            ret, info = put_data(_token, file_name, data)
            fileID = ret.get("fileID", None)
            if fileID:
                new_url = self.baseUrl + fileID
        return new_url


if __name__ == "__main__":
    url = "https://qhyxpicoss.kujiale.com/fpimgnew/2016/05/27/V0gCSQozG1MdaAg_800x800.jpg"
    qiniu = Qiniu()
    # qiniu.put_data(key="/fpimgnew/2016/05/27/V0gCSQozG1MdaAg_800x800",url=url)
    new_url = qiniu.put_data(key=url, url=url)
    print(new_url)
