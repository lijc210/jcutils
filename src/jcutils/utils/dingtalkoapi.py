"""
@Time   : 2019/1/8
@author : lijc210@163.com
@Desc:  : 从钉钉接口获取数据。
"""

import json
import time

import requests
from retry import retry


@retry(tries=3, delay=2)  # 报错重试
def get(url):
    res = requests.get(url, timeout=20)
    # print (url,res.status_code)
    return res


@retry(tries=3, delay=2)  # 报错重试
def post(url, data=None, json=None):
    res = requests.post(url, data=data, json=json, timeout=20)
    # print (url,res.status_code)
    return res


def ts2dt(ts):
    """
    时间戳转时间
    :param ts: 1519960417
    :return: datetime str
    """
    if len(str(int(ts))) == 13:
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts / 1000))
    else:
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))


class Dingtalk:
    def __init__(self, corpid=None, corpsecret=None):
        self.corpid = corpid
        self.corpsecret = corpsecret
        self.access_token = self.gettoken()

    def gettoken(self):
        """
        获取token
        :return:
        """
        resp = get("https://oapi.dingtalk.com/gettoken?corpid={}&corpsecret={}".format(self.corpid, self.corpsecret))
        access_token = resp.json()["access_token"]
        return access_token

    def get_user(self, userid):
        """
        获取用户详情
        :param userid:
        :return:
        """
        resp_dict = get(
            "https://oapi.dingtalk.com/user/get?access_token={}&userid={}".format(self.access_token, userid)
        ).json()
        return resp_dict

    def get_department_list(self):
        """
        获取部门列表
        :return:
        """
        resp_dict = get("https://oapi.dingtalk.com/department/list?access_token={}".format(self.access_token)).json()
        # print (resp_dict)
        return resp_dict

    def get_simplelist(self, department_id):
        """
        获取部门用户
        :param department_id: 门列表接口返回的部门id(department_id)
        :return:
        """
        resp_dict = get(
            "https://oapi.dingtalk.com/user/simplelist?access_token={}&department_id={}".format(
                self.access_token, department_id
            )
        ).json()
        userlist = resp_dict["userlist"]
        return userlist

    def get_listbypage(self, department_id, offset=0, size=100):
        """
        获取部门用户详情
        :param department_id: 门列表接口返回的部门id(department_id)
        :return:
        """

        userlist_all = []
        hasMore = True
        while hasMore:
            resp_dict = get(
                "https://oapi.dingtalk.com/user/listbypage?access_token={}&department_id={}&offset={}&size={}".format(
                    self.access_token, department_id, offset, size
                ),
            ).json()
            hasMore = resp_dict.get("hasMore", False)
            recordresult = resp_dict["userlist"]
            userlist_all.extend(recordresult)
            offset = offset + size
        return userlist_all

    def get_attendance_listRecord(self, workDateFrom=None, workDateTo=None, userIdList=None):
        """
        获取打卡记录
        :param workDateFrom:查询考勤打卡记录的起始工作日。格式为“yyyy-MM-dd hh:mm:ss”，hh:mm:ss可以使用00:00:00，具体查询的时候不会起作用，最后将返回此日期从0点到24点的结果
        :param workDateTo:查询考勤打卡记录的结束工作日,注意，起始与结束工作日最多相隔7天
        :param userIdList:员工在企业内的UserID列表,最多不能超过50个
        :return:
        """
        post_data = {
            "userIds": userIdList,
            "checkDateFrom": workDateFrom,
            "checkDateTo": workDateTo,
            "isI18n": "false",
        }
        resp_dict = post(
            "https://oapi.dingtalk.com/attendance/listRecord?access_token={}".format(self.access_token),
            json=post_data,
        ).json()
        # print (json.dumps(resp_dict))
        return resp_dict

    def get_attendance_list(self, workDateFrom=None, workDateTo=None, userIdList=None, offset=0, limit=50):
        """
        获取打卡结果
        :param workDateFrom:查询考勤打卡记录的起始工作日。格式为“yyyy-MM-dd hh:mm:ss”，hh:mm:ss可以使用00:00:00，具体查询的时候不会起作用，最后将返回此日期从0点到24点的结果
        :param workDateTo:查询考勤打卡记录的结束工作日
        :param userIdList:员工在企业内的UserID列表,最多不能超过50个
        :param offset:表示获取考勤数据的起始点，第一次传0
        :param limit:表示获取考勤数据的条数，最大不能超过50条
        :return:
        """
        recordresult_all = []
        hasMore = True
        while hasMore:
            post_data = {
                "workDateFrom": workDateFrom,
                "workDateTo": workDateTo,
                "userIdList": userIdList,
                "offset": offset,
                "limit": limit,
            }
            resp_dict = post(
                "https://oapi.dingtalk.com/attendance/list?access_token={}".format(self.access_token),
                json=post_data,
            ).json()
            hasMore = resp_dict.get("hasMore", False)
            recordresult = resp_dict.get("recordresult", False)
            if recordresult is False:
                print("resp_dict", json.dumps(resp_dict, ensure_ascii=False))
            recordresult_all.extend(recordresult)
            offset = offset + limit
        return recordresult_all

    def get_processinstance(self, process_instance_id):
        """
        获取单个审批实例，获取请假、加班等审批有关的数据
        :param process_instance_id:审批实例id，从打卡结果数据中获取

        :return:
        """
        post_data = {"process_instance_id": process_instance_id}
        resp_dict = post(
            "https://oapi.dingtalk.com/topapi/processinstance/get?access_token={}".format(self.access_token),
            json=post_data,
        ).json()
        errcode = resp_dict.get("errcode")
        if errcode != 0:
            print(json.dumps(resp_dict))
        process_instance = resp_dict["process_instance"]
        return process_instance

    def get_process_listbyuserid(self, userid=None, offset=0, size=100):
        """
        获取用户可见的审批模板
        :param userid: 用户id 可选，不传的话表示获取企业的所有模板
        :param offset:
        :param size:
        :return:
        """

        post_data = {"offset": offset, "size": size}
        resp_dict = post(
            "https://oapi.dingtalk.com/topapi/process/listbyuserid?access_token={}".format(self.access_token),
            json=post_data,
        ).json()
        process_list = resp_dict["result"]["process_list"]
        return process_list

    def get_processinstance_listids(
        self,
        process_code=None,
        start_time=0,
        end_time=0,
        size=10,
        cursor=1,
        userid_list=None,
    ):
        """
        批量获取审批实例id
        :param process_code: 流程模板唯一标识，
        :param start_time: 开始时间。Unix时间戳
        :param end_time: 结束时间，默认取当前时间。Unix时间戳
        :param size: 分页参数，每页大小，最多传10，
        :param cursor: 分页查询的游标，最开始传0，0和1返回一样，
        :param userid_list:发起人用户id列表，用逗号分隔，最大列表长度：10
        :return:
        """
        next_cursor = cursor
        processinstance_list = []
        while next_cursor:
            post_data = {
                "process_code": process_code,
                "start_time": start_time,
                "end_time": end_time,
                "size": size,
                "cursor": next_cursor,
                "userid_list": userid_list,
            }
            resp_dict = post(
                "https://oapi.dingtalk.com/topapi/processinstance/listids?access_token={}".format(self.access_token),
                json=post_data,
            ).json()
            errcode = resp_dict.get("errcode")
            if errcode != 0:
                print(json.dumps(resp_dict))
            tmp_list = resp_dict["result"].get("list", [])
            next_cursor = resp_dict["result"].get("next_cursor", None)
            processinstance_list.extend(tmp_list)
        return processinstance_list


if __name__ == "__main__":
    # 测试账号
    # corpid='dingl1wocjyjz34fxxxx'
    # corpsecret='2VB26Ar7iwRx59iFDqZT0yDoeg8wOimumZr80HwFh0PuBY7EkLpR-RiHTDMwxxxx'
    corpid = "dingqhzfnaiwaxyzxxxx"
    corpsecret = "OQq7kn5qa3Tmn5H0_YUxeOfmbQ4wG2Mi3f7Qv-nTNLuDD8POP7iDSbeU6LxDxxxx"
    dingtalk = Dingtalk(corpid=corpid, corpsecret=corpsecret)
    # print (json.dumps(dingtalk.get_department_list()))
    # print (json.dumps(dingtalk.get_listbypage(80593557), ensure_ascii=False))
    # dingtalk.get_attendance_listRecord(workDateFrom='2019-01-16 00:00:00', workDateTo='2019-01-16 23:59:59',
    #                                    userIdList=['0721073702836798', '0126695528847013', '015443572021345707'])
    # print(json.dumps(dingtalk.get_user(userid="1517464824278718")))
    # print(json.dumps(dingtalk.get_process_listbyuserid()))
    dingtalk.get_processinstance_listids(
        process_code="PROC-CFYJOYWU-YVX05GBY0XEWD5X4YZYI2-DP8DZAPJ-A1",
        start_time=1547537195000,
        end_time=1547796395000,
        size=10,
        cursor=1,
        userid_list=None,
    )
