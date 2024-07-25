"""
@Time   : 2019/1/8
@author : lijc210@163.com
@Desc:  : dingtalk新版 api

https://open.dingtalk.com/document/orgapp/dingtalk-openapi-overview
"""

import json

import requests
from retry import retry


class Dingtalk:
    def __init__(self, corpid=None, corpsecret=None):
        self.base_url = "https://api.dingtalk.com"
        self.corpid = corpid
        self.corpsecret = corpsecret
        self.access_token = self.gettoken()

    @retry(tries=3, delay=2)  # 报错重试
    def gettoken(self):
        """
        获取token
        :return:
        """
        url = self.base_url + "/gettoken?corpid={}&corpsecret={}".format(
            self.corpid, self.corpsecret
        )
        resp = requests.get(url, timeout=20)
        print(resp.text)
        access_token = resp.json()["access_token"]
        return access_token

    @retry(tries=3, delay=2)  # 报错重试
    def get_userVisibilities_templates(self, userid=None, maxResults=100, nextToken=0):
        """
        获取用户可见的审批模板
        https://open.dingtalk.com/document/orgapp/obtains-a-list-of-approval-forms-visible-to-the-specified
        :param userid: 用户id 可选，不传的话表示获取企业的所有模板
        :param maxResults:
        :param nextToken:
        :return:
        """
        params = f"?maxResults={maxResults}&nextToken={nextToken}"
        # print(params)
        headers = {
            "Content-Type": "application/json",
            "x-acs-dingtalk-access-token": self.access_token,
        }
        url = (
            self.base_url
            + "/v1.0/workflow/processes/userVisibilities/templates"
            + params
        )
        resp = requests.get(url, headers=headers, timeout=20)
        resp_dict = resp.json()
        code = resp_dict.get("code")
        if code == "InvalidAuthentication":
            self.access_token = self.gettoken()
            print(resp.text)
            raise Exception("InvalidAuthentication")
        # print(resp.text)
        return resp_dict

    @retry(tries=3, delay=2)  # 报错重试
    def get_processinstance_listids(
        self,
        process_code=None,
        start_time=0,
        end_time=0,
        nextToken=0,
        maxResults=20,
        userIds=None,
        statuses=None,
    ):
        """
        获取审批实例ID列表
        https://open.dingtalk.com/document/orgapp/obtain-an-approval-list-of-instance-ids
        :param processCode: 流程模板唯一标识，
        :param startTime: 开始时间。Unix时间戳
        :param endTime: 结束时间，默认取当前时间。Unix时间戳
        :param nextToken: 分页游标。
        :param maxResults: 分页参数，每页大小，最多传20。
        :param userIds: 发起人userId列表，最大列表长度为10。
        :param statuses: 流程实例状态：
        :return:
        """
        processinstance_list = []
        headers = {
            "Content-Type": "application/json",
            "x-acs-dingtalk-access-token": self.access_token,
        }
        while True:
            post_data = {
                "processCode": process_code,
                "startTime": start_time,
                "endTime": end_time,
                "nextToken": nextToken,
                "maxResults": maxResults,
                "userIds": userIds,
                "statuses": statuses,
            }

            url = self.base_url + "/v1.0/workflow/processes/instanceIds/query"
            res = requests.post(url, json=post_data, headers=headers, timeout=20)
            resp_dict = res.json()
            success = resp_dict.get("success")
            if success is False:
                self.access_token = self.gettoken()
                print(res.text)
                raise Exception(json.dumps(resp_dict))
            tmp_list = resp_dict["result"].get("list", [])
            nextToken = resp_dict["result"].get("nextToken", None)
            processinstance_list.extend(tmp_list)
            if nextToken is None:
                break
        return processinstance_list

    @retry(tries=3, delay=2)  # 报错重试
    def get_processInstances(self, processInstanceId=None):
        """
        获取单个审批实例详情
        https://open.dingtalk.com/document/orgapp/obtains-the-details-of-a-single-approval-instance-pop
        :param processInstanceId: 审批实例ID
        :return:
        """
        params = f"?processInstanceId={processInstanceId}"
        # print(params)
        headers = {
            "Content-Type": "application/json",
            "x-acs-dingtalk-access-token": self.access_token,
        }
        url = self.base_url + "/v1.0/workflow/processInstances" + params
        resp = requests.get(url, headers=headers, timeout=20)
        resp_dict = resp.json()
        code = resp_dict.get("code")
        if code == "InvalidAuthentication":
            self.access_token = self.gettoken()
            print(resp.text)
            raise Exception("InvalidAuthentication")
        # print(resp.text)
        return resp_dict

    @retry(tries=3, delay=2)  # 报错重试
    def download_attachment(self, processInstanceId="", fileId=""):
        """
        下载审批附件
        https://open.dingtalk.com/document/orgapp/download-an-approval-attachment
        :param processInstanceId: 审批实例ID
        :return:
        """
        data = {
            "processInstanceId": processInstanceId,
            "fileId": fileId,
            "withCommentAttatchment": False,
        }
        # print(params)
        headers = {
            "Content-Type": "application/json",
            "x-acs-dingtalk-access-token": self.access_token,
        }
        url = (
            self.base_url + "/v1.0/workflow/processInstances/spaces/files/urls/download"
        )
        resp = requests.post(url, headers=headers, json=data, timeout=20)
        resp_dict = resp.json()
        code = resp_dict.get("code")
        if code == "InvalidAuthentication":
            self.access_token = self.gettoken()
            print(resp.text)
            raise Exception("InvalidAuthentication")
        # print(resp.text)
        return resp_dict


if __name__ == "__main__":
    corpid = "xxxx"
    corpsecret = "OQq7kn5qa3Tmn5H0_YUxeOfmbQ4wG2Mi3f7Qv-nTNLuDD8POP7iDSbeU6LxDxxxx"
    dingtalk = Dingtalk(corpid=corpid, corpsecret=corpsecret)
