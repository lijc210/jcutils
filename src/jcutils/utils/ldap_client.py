"""
@File    :   1.py
@Time    :   2020/12/30 15:37:06
@Author  :   lijc210@163.com
@Desc    :   None
"""

import logging

from ldap3 import ALL_ATTRIBUTES, SUBTREE, Connection, Server

from src.api.config import CONFIG

ldap_host = CONFIG.ldap_host  # ldap服务器地址
ldap_port = CONFIG.ldap_port  # 默认389
ldap_admin_user = CONFIG.ldap_admin_user  # ldap管理员账户用户名
ldap_admin_password = CONFIG.ldap_admin_password  # ldap管理员账户密码
ldap_base_search = CONFIG.ldap_base_search  # 查询域
logging.basicConfig()
logger = logging.getLogger("test")
logger.setLevel(logging.INFO)


def search(username):
    s = Server(host=ldap_host, port=ldap_port, use_ssl=False, get_info="ALL")
    # 连接ldap服务器
    ldapz_admin_connection = Connection(
        s,
        user=ldap_admin_user,
        password=ldap_admin_password,
        auto_bind="NONE",
        version=3,
        authentication="SIMPLE",
        client_strategy="SYNC",
        auto_referrals=True,
        check_names=True,
        read_only=False,
        lazy=False,
        raise_exceptions=False,
    )

    # 连上以后必须bind才能有值
    ldapz_admin_connection.bind()

    # 这个是为了查询你输入的用户名的入口搜索地址
    ldapz_admin_connection.search(
        search_base=ldap_base_search,
        search_filter="(sAMAccountName={})".format(username),
        search_scope=SUBTREE,
        # attributes=["cn", "givenName", "mail", "sAMAccountName"],
        attributes=["*"],
    )
    # print(res)
    response = ldapz_admin_connection.response
    print(response)


def ldap_auth(username, password):
    """
    ldap验证方法
    :param username: 用户名
    :param password: 密码
    :return:
    """
    s = Server(host=ldap_host, port=ldap_port, use_ssl=False, get_info="ALL")

    # 连接ldap服务器
    ldapz_admin_connection = Connection(
        s,
        user=ldap_admin_user,
        password=ldap_admin_password,
        auto_bind="NONE",
        version=3,
        authentication="SIMPLE",
        client_strategy="SYNC",
        auto_referrals=True,
        check_names=True,
        read_only=False,
        lazy=False,
        raise_exceptions=False,
    )

    # 连上以后必须bind才能有值
    ldapz_admin_connection.bind()

    # 这个是为了查询你输入的用户名的入口搜索地址
    res = ldapz_admin_connection.search(
        search_base=ldap_base_search,
        search_filter="(sAMAccountName={})".format(username),
        search_scope=SUBTREE,
        # attributes=["cn", "givenName", "mail", "sAMAccountName"],
        attributes=["*"],
    )
    # print(res)
    try:
        if res:
            response = ldapz_admin_connection.response
            if response:
                print(response)
                entry = response[0]
                logger.info(entry)
                dn = entry["dn"]
                attr_dict = entry["attributes"]
                logger.info("attr_dic:%s" % attr_dict)

                try:
                    # 这个connect是通过你的用户名和密码还有上面搜到的入口搜索来查询的
                    conn2 = Connection(
                        s,
                        user=dn,
                        password=password,
                        check_names=True,
                        lazy=False,
                        raise_exceptions=False,
                    )
                    conn2.bind()
                    # logger.info(conn2.result["description"])

                    # 正确-success 不正确-invalidCredentials
                    if conn2.result["description"] == "success":
                        logger.info("ldap auth pass!")
                        return attr_dict
                    else:
                        logger.info("username or password error!")
                        return {}
                except Exception as e:
                    logger.info("username or password error!")
                    logger.info(e)
                    return {}
    except KeyError as e:
        logger.info("username or password error!")
        logger.info(e)
        return {}


def get_users():
    """
    ldap验证方法
    :param username: 用户名
    :param password: 密码
    :return:
    """
    s = Server(host=ldap_host, port=ldap_port, use_ssl=False, get_info="ALL")

    # 连接ldap服务器
    ldapz_admin_connection = Connection(
        s,
        user=ldap_admin_user,
        password=ldap_admin_password,
        auto_bind="NONE",
        version=3,
        authentication="SIMPLE",
        client_strategy="SYNC",
        auto_referrals=True,
        check_names=True,
        read_only=False,
        lazy=False,
        raise_exceptions=False,
    )
    # 连上以后必须bind才能有值
    ldapz_admin_connection.bind()

    searchParameters = {
        "search_base": ldap_base_search,
        "search_filter": "(&(objectclass=person)(!(sAMAccountName=*$)))",
        "search_scope": SUBTREE,
        "attributes": ALL_ATTRIBUTES,
        "paged_size": 500,
    }

    data_list = []
    n = 0
    while True:
        ldapz_admin_connection.search(**searchParameters)
        for entry in ldapz_admin_connection.entries:
            if "displayName" in entry:
                displayName = entry["displayName"][0]
                name = entry["name"][0]
                distinguishedName = entry["distinguishedName"][0]
                whenCreated = entry["whenCreated"][0].strftime("%Y-%m-%d %H:%M:%S")
                whenChanged = entry["whenChanged"][0].strftime("%Y-%m-%d %H:%M:%S")
                ou_list = []
                for x in distinguishedName.split(","):
                    if x.startswith("OU="):
                        ou_list.append(x.replace("OU=", ""))
                ou_list.reverse()
                if len(ou_list) >= 1:
                    ou1 = ou_list[0]
                    ou2 = ou_list[1] if len(ou_list) > 1 else ""
                    ou3 = ou_list[2] if len(ou_list) > 2 else ""
                    ou4 = ou_list[3] if len(ou_list) > 3 else ""
                    ou5 = ou_list[4] if len(ou_list) > 4 else ""
                    is_leave = 0
                    if ou1 == "离职人员":
                        ou1 = ""
                        is_leave = 1
                    elif len(ou_list) == 1:
                        continue
                    n += 1
                    data_list.append(
                        [
                            name,
                            displayName,
                            ou1,
                            ou2,
                            ou3,
                            ou4,
                            ou5,
                            whenCreated,
                            whenChanged,
                            is_leave,
                        ]
                    )
                    # break
        cookie = ldapz_admin_connection.result["controls"]["1.2.840.113556.1.4.319"][
            "value"
        ]["cookie"]
        if cookie:
            searchParameters["paged_cookie"] = cookie
        else:
            break
        # break
    print(n)
    return data_list


if __name__ == "__main__":
    search("liuzhigang")
    # ldap_auth("lijicong", "")
    # get_users()
