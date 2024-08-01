"""
@author: lijc210@163.com
@file: 1.py
@time: 2020/05/22
@desc: 功能描述。
"""

from ftplib import FTP


class FtpClient:
    def __init__(self, host=None, port=None, username=None, password=None):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.ftp = self.connect()

    def connect(self):
        ftp = FTP()
        # 打开调试级别2，显示详细信息
        # ftp.set_debuglevel(2)
        ftp.connect(self.host, self.port)
        ftp.login(self.username, self.password)
        return ftp

    def nlst(self):
        """
        返回目录下的文件
        :param hdfs_path:
        :return:
        """
        return self.ftp.nlst()

    def download(self, remote_path=None, local_path=None):
        """
        从ftp下载文件
        :param remote_path:
        :param local_path:
        :return:
        """
        # 设置的缓冲区大小
        bufsize = 1024
        fp = open(local_path, "wb")
        self.ftp.retrbinary("RETR " + remote_path, fp.write, bufsize)
        self.ftp.set_debuglevel(0)  # 参数为0，关闭调试模式
        fp.close()

    def upload(self, local_path=None, remote_path=None):
        """
        上传
        :param hdfs_path:
        :param local_path:
        :return:
        """
        bufsize = 1024
        fp = open(local_path, "rb")
        self.ftp.storbinary("STOR " + remote_path, fp, bufsize)
        self.ftp.set_debuglevel(0)
        fp.close()


if __name__ == "__main__":
    ##### 连接
    ftp_client = FtpClient(host="127.0.0.1", port=21)

    ##### list
    print(ftp_client.nlst())

    ##### download
    ftp_client.download("1.txt", "1.txt")

    ##### upload
    ftp_client.upload("2.txt", "2.txt")
