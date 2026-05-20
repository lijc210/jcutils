"""
@File    :   ldap_client.py
@Time    :   2024/01/01 00:00:00
@Author  :   lijc210@163.com
@Desc    :   LDAP 客户端
            提供 LDAP 认证、用户查询、用户信息获取等功能
            使用连接池管理 LDAP 连接，支持分页查询
"""

import logging
from typing import Any, Dict, Generator, List, Optional, Union, cast

try:
    from ldap3 import ALL, ALL_ATTRIBUTES, SUBTREE, Connection, Server
except ModuleNotFoundError:
    raise ImportError('请先安装：pip install ldap3 or uv add "ldap3"')
except Exception as e:
    raise ImportError(f"ldap3 导入失败: {e}")


class LdapClient:
    """
    LDAP 客户端类

    提供以下功能：
    - LDAP 用户认证
    - 用户信息查询
    - 批量获取用户列表（支持分页）
    """

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        admin_user: Optional[str] = None,
        admin_password: Optional[str] = None,
        base_search: Optional[str] = None,
        use_ssl: bool = False,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        """
        初始化 LDAP 客户端

        :param host: LDAP 服务器地址，默认从 CONFIG 读取
        :param port: LDAP 服务器端口，默认从 CONFIG 读取
        :param admin_user: 管理员账户用户名，默认从 CONFIG 读取
        :param admin_password: 管理员账户密码，默认从 CONFIG 读取
        :param base_search: 查询域，默认从 CONFIG 读取
        :param use_ssl: 是否使用 SSL 连接，默认 False
        :param logger: 日志记录器，如果为 None 则创建默认的 logger
        """
        self.host = host
        self.port = port
        self.admin_user = admin_user
        self.admin_password = admin_password
        self.base_search = base_search
        self.use_ssl = use_ssl

        # 初始化日志
        self.logger = logger or logging.getLogger("ldap_client")

        # 缓存 Server 对象
        self._server: Optional[Server] = None

    def _get_server(self) -> Server:
        """
        获取或创建 LDAP Server 对象（懒加载）

        :return: Server 对象
        """
        if self._server is None:
            if self.host is None:
                raise ValueError("host must be provided")
            if self.port is None:
                raise ValueError("port must be provided")
            self._server = Server(
                host=self.host,
                port=self.port,
                use_ssl=self.use_ssl,
                get_info=ALL,
            )
        return self._server

    def _get_admin_connection(self) -> Connection:
        """
        获取管理员连接

        :return: Connection 对象
        :raises Exception: 连接或认证失败时抛出
        """
        server = self._get_server()
        conn = Connection(
            server,
            user=self.admin_user,
            password=self.admin_password,
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

        # 连接后必须 bind 才能执行查询
        if not conn.bind():
            raise Exception(f"LDAP bind failed: {conn.result}")
        return conn

    def search(
        self,
        username: str,
        attributes: Optional[List[str]] = None,
        search_filter: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        搜索用户信息

        :param username: 用户名
        :param attributes: 要返回的属性列表，None 表示返回所有属性
        :param search_filter: 自定义搜索过滤器，None 表示使用默认的 sAMAccountName 过滤器
        :return: 用户属性字典，查询失败返回 None
        """
        try:
            with self._get_admin_connection() as conn:
                # 构建搜索过滤器
                if search_filter is None:
                    search_filter = f"(sAMAccountName={username})"

                # 设置返回属性
                if attributes is None:
                    attributes = ["*"]

                # 执行搜索
                if self.base_search is None:
                    raise ValueError("base_search must be provided")
                conn.search(
                    search_base=self.base_search,
                    search_filter=search_filter,
                    search_scope=SUBTREE,
                    attributes=attributes,
                )

                # 解析结果
                if conn.response and len(conn.response) > 0:
                    entry = conn.response[0]
                    return entry.get("attributes", {})
                return None
        except Exception as e:
            self.logger.error(f"LDAP search failed for user {username}: {e}")
            return None

    def ldap_auth(self, username: str, password: str) -> Dict[str, Any]:
        """
        LDAP 用户认证

        :param username: 用户名
        :param password: 密码
        :return: 认证成功返回用户属性字典，失败返回空字典
        """
        try:
            with self._get_admin_connection() as admin_conn:
                # 先搜索用户信息，获取用户的 DN
                search_filter = f"(sAMAccountName={username})"
                if self.base_search is None:
                    raise ValueError("base_search must be provided")
                admin_conn.search(
                    search_base=self.base_search,
                    search_filter=search_filter,
                    search_scope=SUBTREE,
                    attributes=["*"],
                )

                if not admin_conn.response:
                    self.logger.info(f"User {username} not found")
                    return {}

                entry = admin_conn.response[0]
                dn = entry["dn"]
                attr_dict = entry["attributes"]
                self.logger.info(f"User found: {attr_dict}")

                # 使用用户的 DN 和密码进行认证
                server = self._get_server()
                user_conn = Connection(
                    server,
                    user=dn,
                    password=password,
                    check_names=True,
                    lazy=False,
                    raise_exceptions=False,
                )
                user_conn.bind()

                # 检查认证结果
                if user_conn.result["description"] == "success":
                    self.logger.info(f"LDAP auth pass for user {username}!")
                    return attr_dict
                else:
                    self.logger.info(f"LDAP auth failed for user {username}: {user_conn.result['description']}")
                    return {}
        except Exception as e:
            self.logger.error(f"LDAP auth error for user {username}: {e}")
            return {}

    def get_users(
        self,
        search_filter: str = "(&(objectclass=person)(!(sAMAccountName=*)))",
        attributes: Optional[str] = ALL_ATTRIBUTES,
        page_size: int = 500,
    ) -> Generator[List[Union[str, int]], None, None]:
        """
        分页获取所有用户信息

        :param search_filter: 搜索过滤器，默认排除以 * 结尾的 sAMAccountName
        :param attributes: 要返回的属性，默认返回所有属性
        :param page_size: 每页的大小，默认 500
        :yield: 每批用户数据列表，每条记录包含：
                [name, displayName, ou1, ou2, ou3, ou4, ou5, whenCreated, whenChanged, is_leave]
        """
        try:
            with self._get_admin_connection() as conn:
                if self.base_search is None:
                    raise ValueError("base_search must be provided")
                search_parameters = {
                    "search_base": self.base_search,
                    "search_filter": search_filter,
                    "search_scope": SUBTREE,
                    "attributes": attributes,
                    "paged_size": page_size,
                }

                count = 0
                while True:
                    conn.search(**search_parameters)
                    batch_data = []

                    for entry in conn.entries:
                        if "displayName" not in entry:
                            continue

                        # 提取基本信息
                        displayName = entry["displayName"][0]
                        name = entry["name"][0]
                        distinguishedName = entry["distinguishedName"][0]
                        whenCreated = entry["whenCreated"][0].strftime("%Y-%m-%d %H:%M:%S")
                        whenChanged = entry["whenChanged"][0].strftime("%Y-%m-%d %H:%M:%S")

                        # 解析组织架构 (OU)
                        ou_list = []
                        for x in distinguishedName.split(","):
                            if x.startswith("OU="):
                                ou_list.append(x.replace("OU=", ""))
                        ou_list.reverse()

                        # 填充 5 级 OU
                        ou1 = ou_list[0] if len(ou_list) > 0 else ""
                        ou2 = ou_list[1] if len(ou_list) > 1 else ""
                        ou3 = ou_list[2] if len(ou_list) > 2 else ""
                        ou4 = ou_list[3] if len(ou_list) > 3 else ""
                        ou5 = ou_list[4] if len(ou_list) > 4 else ""

                        # 判断是否离职
                        is_leave = 0
                        if ou1 == "离职人员":
                            ou1 = ""
                            is_leave = 1
                        elif len(ou_list) == 1:
                            continue

                        count += 1
                        batch_data.append(
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

                    if batch_data:
                        yield batch_data

                    # 检查是否还有下一页
                    paged_control = conn.result["controls"].get("1.2.840.113556.1.4.319")
                    if paged_control:
                        cookie = paged_control["value"].get("cookie")
                        if cookie:
                            search_parameters["paged_cookie"] = cookie
                        else:
                            break
                    else:
                        break

                self.logger.info(f"Total users fetched: {count}")
        except Exception as e:
            self.logger.error(f"Get users error: {e}")
            raise

    def get_users_list(
        self,
        search_filter: str = "(&(objectclass=person)(!(sAMAccountName=*)))",
        attributes: Optional[str] = ALL_ATTRIBUTES,
        page_size: int = 500,
    ) -> List[List[Union[str, int]]]:
        """
        获取所有用户信息（非生成器版本）

        :param search_filter: 搜索过滤器
        :param attributes: 要返回的属性
        :param page_size: 每页的大小
        :return: 所有用户数据列表（每批一个子列表）
        """
        users_list: List[List[Union[str, int]]] = []
        for batch in self.get_users(search_filter, attributes, page_size):
            users_list.append(batch)
        return users_list


if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.INFO)

    # 创建 LDAP 客户端（使用配置文件中的默认值）
    ldap_client = LdapClient()

    # 示例 1: 搜索用户
    print("=== 搜索用户 ===")
    user_info = ldap_client.search("liuzhigang")
    print(f"用户信息: {user_info}")
    print()

    # 示例 2: LDAP 认证
    print("=== LDAP 认证 ===")
    # 注意：需要提供真实的用户名和密码
    # auth_result = ldap_client.ldap_auth("username", "password")
    # if auth_result:
    #     print(f"认证成功: {auth_result}")
    # else:
    #     print("认证失败")
    print()

    # 示例 3: 获取所有用户（使用生成器，节省内存）
    print("=== 获取所有用户（生成器）===")
    try:
        total_count = 0
        for batch in ldap_client.get_users():
            print(f"当前批次数量: {len(batch)}")
            for user in batch[:3]:  # 只打印每批的前 3 个用户
                user = cast(List[Union[str, int]], user)
                print(f"  - {user[1]} ({user[0]})")
            total_count += len(batch)
        print(f"总计用户数: {total_count}")
    except Exception as e:
        print(f"获取用户失败: {e}")
    print()

    # 示例 4: 获取所有用户（直接返回列表）
    print("=== 获取所有用户（列表）===")
    try:
        users_list = ldap_client.get_users_list(page_size=100)
        total_users = sum(len(batch) for batch in users_list)
        print(f"获取到 {total_users} 个用户（分 {len(users_list)} 批）")
        # 打印第一批的前 5 个用户
        if users_list and users_list[0]:
            for user in users_list[0][:5]:
                user = cast(List[Union[str, int]], user)
                print(f"  - {user[1]} ({user[0]}) - 部门: {user[2]}")
    except Exception as e:
        print(f"获取用户失败: {e}")
    print()

    # 示例 5: 使用自定义配置创建客户端
    print("=== 自定义配置 ===")
    custom_ldap = LdapClient(
        host="ldap.example.com",
        port=389,
        admin_user="cn=admin,dc=example,dc=com",
        admin_password="password",
        base_search="dc=example,dc=com",
        use_ssl=False,
    )
    print(f"自定义 LDAP 客户端已创建: {custom_ldap.host}:{custom_ldap.port}")
