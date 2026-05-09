"""
@Time   : 2019/1/8
@author : lijc210@163.com
@Desc   : 从钉钉旧版 API 获取数据
          DingTalk Open API (Old Version) client
          Documentation: https://open-doc.dingtalk.com/
"""

import json
import time
from typing import Any, Dict, List, Optional, Union

import requests
from retry import retry


@retry(tries=3, delay=2)  # 报错重试
def get(url: str) -> requests.Response:
    """
    发送 GET 请求，带重试机制

    :param url: 请求的 URL
    :return: requests.Response 对象
    """
    res = requests.get(url, timeout=20)
    # print (url,res.status_code)
    return res


@retry(tries=3, delay=2)  # 报错重试
def post(url: str, data: Optional[Dict[str, Any]] = None, json: Optional[Dict[str, Any]] = None) -> requests.Response:
    """
    发送 POST 请求，带重试机制

    :param url: 请求的 URL
    :param data: 表单数据
    :param json: JSON 数据
    :return: requests.Response 对象
    """
    res = requests.post(url, data=data, json=json, timeout=20)
    # print (url,res.status_code)
    return res


def ts2dt(ts: Union[int, float]) -> str:
    """
    时间戳转时间字符串

    :param ts: 时间戳，支持秒级（10位）和毫秒级（13位）
    :return: 格式化的时间字符串 "%Y-%m-%d %H:%M:%S"
    """
    if len(str(int(ts))) == 13:
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts / 1000))
    else:
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))


class Dingtalk:
    """
    钉钉旧版 API 客户端类

    提供访问钉钉企业应用相关接口的能力，包括：
    - 用户信息获取
    - 部门管理
    - 考勤记录
    - 审批流程
    """

    def __init__(self, corpid: Optional[str] = None, corpsecret: Optional[str] = None) -> None:
        """
        初始化钉钉 API 客户端

        :param corpid: 企业 ID
        :param corpsecret: 应用的密钥
        """
        self.corpid: Optional[str] = corpid
        self.corpsecret: Optional[str] = corpsecret
        self.access_token: Optional[str] = self.gettoken()

    def gettoken(self) -> Optional[str]:
        """
        获取访问令牌

        :return: access_token 字符串，失败返回 None
        """
        try:
            resp = get(
                "https://oapi.dingtalk.com/gettoken?corpid={}&corpsecret={}".format(self.corpid, self.corpsecret)
            )
            access_token: str = resp.json()["access_token"]
            return access_token
        except Exception:
            return None

    def get_user(self, userid: str) -> Optional[Dict[str, Any]]:
        """
        获取用户详情

        :param userid: 用户在企业的 UserID
        :return: 用户信息字典，失败返回 None
        """
        try:
            resp_dict: Dict[str, Any] = get(
                "https://oapi.dingtalk.com/user/get?access_token={}&userid={}".format(self.access_token, userid)
            ).json()
            return resp_dict
        except Exception:
            return None

    def get_department_list(self) -> Optional[Dict[str, Any]]:
        """
        获取部门列表

        :return: 部门列表字典，失败返回 None
        """
        try:
            resp_dict: Dict[str, Any] = get(
                "https://oapi.dingtalk.com/department/list?access_token={}".format(self.access_token)
            ).json()
            # print (resp_dict)
            return resp_dict
        except Exception:
            return None

    def get_simplelist(self, department_id: Union[int, str]) -> Optional[List[Dict[str, Any]]]:
        """
        获取部门成员（简化信息）

        :param department_id: 部门列表接口返回的部门 ID (department_id)
        :return: 用户列表，失败返回 None
        """
        try:
            resp_dict: Dict[str, Any] = get(
                "https://oapi.dingtalk.com/user/simplelist?access_token={}&department_id={}".format(
                    self.access_token, department_id
                )
            ).json()
            userlist: List[Dict[str, Any]] = resp_dict["userlist"]
            return userlist
        except Exception:
            return None

    def get_listbypage(self, department_id: Union[int, str], offset: int = 0, size: int = 100) -> List[Dict[str, Any]]:
        """
        获取部门成员详情（分页）

        :param department_id: 部门 ID
        :param offset: 分页偏移量
        :param size: 每页大小，最大 100
        :return: 用户列表
        """
        userlist_all: List[Dict[str, Any]] = []
        hasMore: bool = True
        while hasMore:
            resp_dict: Dict[str, Any] = get(
                "https://oapi.dingtalk.com/user/listbypage?access_token={}&department_id={}&offset={}&size={}".format(
                    self.access_token, department_id, offset, size
                ),
            ).json()
            hasMore = resp_dict.get("hasMore", False)
            recordresult: List[Dict[str, Any]] = resp_dict["userlist"]
            userlist_all.extend(recordresult)
            offset = offset + size
        return userlist_all

    def get_attendance_listRecord(
        self,
        workDateFrom: Optional[str] = None,
        workDateTo: Optional[str] = None,
        userIdList: Optional[List[str]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        获取打卡记录

        :param workDateFrom: 查询考勤打卡记录的起始工作日
                            格式为 "yyyy-MM-dd hh:mm:ss"，
                            hh:mm:ss 可以使用 00:00:00
        :param workDateTo: 查询考勤打卡记录的结束工作日
                          注意，起始与结束工作日最多相隔 7 天
        :param userIdList: 员工在企业内的 UserID 列表，最多不能超过 50 个
        :return: 打卡记录字典，失败返回 None
        """
        try:
            post_data: Dict[str, Any] = {
                "userIds": userIdList,
                "checkDateFrom": workDateFrom,
                "checkDateTo": workDateTo,
                "isI18n": "false",
            }
            resp_dict: Dict[str, Any] = post(
                "https://oapi.dingtalk.com/attendance/listRecord?access_token={}".format(self.access_token),
                json=post_data,
            ).json()
            # print (json.dumps(resp_dict))
            return resp_dict
        except Exception:
            return None

    def get_attendance_list(
        self,
        workDateFrom: Optional[str] = None,
        workDateTo: Optional[str] = None,
        userIdList: Optional[List[str]] = None,
        offset: int = 0,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        获取打卡结果（分页）

        :param workDateFrom: 查询考勤打卡记录的起始工作日
                            格式为 "yyyy-MM-dd hh:mm:ss"
        :param workDateTo: 查询考勤打卡记录的结束工作日
        :param userIdList: 员工在企业内的 UserID 列表，最多不能超过 50 个
        :param offset: 表示获取考勤数据的起始点，第一次传 0
        :param limit: 表示获取考勤数据的条数，最大不能超过 50 条
        :return: 打卡记录列表
        """
        recordresult_all: List[Dict[str, Any]] = []
        hasMore: bool = True
        while hasMore:
            post_data: Dict[str, Any] = {
                "workDateFrom": workDateFrom,
                "workDateTo": workDateTo,
                "userIdList": userIdList,
                "offset": offset,
                "limit": limit,
            }
            resp_dict: Dict[str, Any] = post(
                "https://oapi.dingtalk.com/attendance/list?access_token={}".format(self.access_token),
                json=post_data,
            ).json()
            hasMore = resp_dict.get("hasMore", False)
            recordresult: Union[bool, List[Dict[str, Any]]] = resp_dict.get("recordresult", False)
            if recordresult is False:
                print("resp_dict", json.dumps(resp_dict, ensure_ascii=False))
            elif isinstance(recordresult, list):
                recordresult_all.extend(recordresult)
            offset = offset + limit
        return recordresult_all

    def get_processinstance(self, process_instance_id: str) -> Optional[Dict[str, Any]]:
        """
        获取单个审批实例详情

        :param process_instance_id: 审批实例 ID，从打卡结果数据中获取
        :return: 审批实例详情字典，失败返回 None
        """
        try:
            post_data: Dict[str, str] = {"process_instance_id": process_instance_id}
            resp_dict: Dict[str, Any] = post(
                "https://oapi.dingtalk.com/topapi/processinstance/get?access_token={}".format(self.access_token),
                json=post_data,
            ).json()
            errcode: Optional[int] = resp_dict.get("errcode")
            if errcode != 0:
                print(json.dumps(resp_dict))
            process_instance: Dict[str, Any] = resp_dict["process_instance"]
            return process_instance
        except Exception:
            return None

    def get_process_listbyuserid(
        self, userid: Optional[str] = None, offset: int = 0, size: int = 100
    ) -> Optional[List[Dict[str, Any]]]:
        """
        获取用户可见的审批模板

        :param userid: 用户 ID，可选，不传的话表示获取企业的所有模板
        :param offset: 分页偏移量
        :param size: 每页大小
        :return: 审批模板列表，失败返回 None
        """
        try:
            post_data: Dict[str, int] = {"offset": offset, "size": size}
            resp_dict: Dict[str, Any] = post(
                "https://oapi.dingtalk.com/topapi/process/listbyuserid?access_token={}".format(self.access_token),
                json=post_data,
            ).json()
            process_list: List[Dict[str, Any]] = resp_dict["result"]["process_list"]
            return process_list
        except Exception:
            return None

    def get_processinstance_listids(
        self,
        process_code: Optional[str] = None,
        start_time: Union[int, float] = 0,
        end_time: Union[int, float] = 0,
        size: int = 10,
        cursor: Union[int, str] = 1,
        userid_list: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        批量获取审批实例 ID

        :param process_code: 流程模板唯一标识
        :param start_time: 开始时间，Unix 时间戳
        :param end_time: 结束时间，默认取当前时间，Unix 时间戳
        :param size: 分页参数，每页大小，最多传 10
        :param cursor: 分页查询的游标，最开始传 0，0 和 1 返回一样
        :param userid_list: 发起人用户 ID 列表，用逗号分隔，最大列表长度：10
        :return: 审批实例 ID 列表
        """
        next_cursor: Union[int, str, None] = cursor
        processinstance_list: List[Dict[str, Any]] = []
        while next_cursor:
            post_data: Dict[str, Any] = {
                "process_code": process_code,
                "start_time": start_time,
                "end_time": end_time,
                "size": size,
                "cursor": next_cursor,
                "userid_list": userid_list,
            }
            resp_dict: Dict[str, Any] = post(
                "https://oapi.dingtalk.com/topapi/processinstance/listids?access_token={}".format(self.access_token),
                json=post_data,
            ).json()
            errcode: Optional[int] = resp_dict.get("errcode")
            if errcode != 0:
                print(json.dumps(resp_dict))
            tmp_list: List[Dict[str, Any]] = resp_dict["result"].get("list", [])
            next_cursor = resp_dict["result"].get("next_cursor", None)
            processinstance_list.extend(tmp_list)
        return processinstance_list


if __name__ == "__main__":
    # 示例用法
    # 注意：需要提供有效的 corpid 和 corpsecret
    corpid = "your_corpid_here"
    corpsecret = "your_corpsecret_here"

    # 初始化客户端
    dingtalk = Dingtalk(corpid=corpid, corpsecret=corpsecret)

    # 测试获取部门列表
    # dept_list = dingtalk.get_department_list()
    # if dept_list:
    #     print("部门列表:", json.dumps(dept_list, ensure_ascii=False, indent=2))

    # 测试时间戳转换
    print("时间戳转换测试:")
    print(f"秒级时间戳: {ts2dt(1519960417)}")
    print(f"毫秒级时间戳: {ts2dt(1519960417000)}")

    # 测试当前时间
    current_ts = int(time.time())
    print(f"当前时间戳: {current_ts}")
    print(f"当前时间: {ts2dt(current_ts)}")
