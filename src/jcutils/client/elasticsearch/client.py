"""
Created on 2017/11/22 0022 17:31
@author: lijc210@163.com
Desc: Elasticsearch 客户端封装，支持旧版 API 的兼容层
"""

import traceback
from typing import Any, Dict, List, Optional, Tuple, Union

try:
    from elasticsearch import Elasticsearch, NotFoundError, helpers
except ModuleNotFoundError:
    raise ImportError('请先安装：pip install jcutils[elasticsearch] or uv add "jcutils[elasticsearch]"')
except Exception as e:
    raise ImportError(f"elasticsearch 导入失败: {e}")


class EsClient:
    def __init__(self, hosts: Optional[List[str]] = None, sniff_on_start: bool = True):
        """
        初始化 Elasticsearch 客户端

        :param hosts: ES 节点列表，例如 ["http://localhost:9200"]
        :param sniff_on_start: 启动时是否探测集群节点
        """
        self.hosts = hosts or []
        self.sniff_on_start = sniff_on_start
        self.es_client = self.conn()

    def conn(self) -> Elasticsearch:
        """
        创建 Elasticsearch 连接

        如果应用程序长时间运行，请考虑打开嗅探，以确保客户端在群集位置上是最新的,
        如果是测试环境，其中有些端口不通，请设置sniff_on_start=False

        :return: Elasticsearch 客户端实例
        """
        return Elasticsearch(
            self.hosts,
            retry_on_timeout=True,
            max_retries=3,
            request_timeout=30,
        )

    def get(
        self,
        index: Optional[str] = None,
        id: Optional[str] = None,
        doc_type: Optional[str] = None,  # noqa: ARG002
        _source: Optional[Union[List[str], str]] = None,
        params: Optional[Dict[str, Any]] = None,  # noqa: ARG002
    ) -> Any:
        """
        获取单条文档

        :param index: 索引名称
        :param id: 文档 ID
        :param doc_type: 文档类型（已废弃，仅用于兼容）
        :param _source: 返回的字段列表或字符串
        :param params: 额外参数
        :return: 文档内容，未找到返回 None
        """
        try:
            kwargs: Dict[str, Any] = {"index": index, "id": id}
            if _source is not None:
                kwargs["_source"] = _source

            response = self.es_client.get(**kwargs)
            return response
        except NotFoundError:
            return None
        except Exception:
            traceback.print_exc()
            return None

    def mget(
        self,
        index: Optional[str] = None,
        doc_type: Optional[str] = None,  # noqa: ARG002
        body: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,  # noqa: ARG002
    ) -> Any:
        """
        批量获取文档

        :param index: 索引名称
        :param doc_type: 文档类型（已废弃，仅用于兼容）
        :param body: 请求体，包含 ids 列表
        :param params: 额外参数（已废弃，仅用于兼容）
        :return: 响应结果
        """
        if body is None:
            body = {}

        try:
            response = self.es_client.mget(body=body, index=index)
            return response
        except Exception:
            traceback.print_exc()
            return None

    def search(
        self,
        index: Optional[str] = None,
        doc_type: Optional[str] = None,  # noqa: ARG002
        body: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        搜索文档

        :param index: 索引名称或列表
        :param doc_type: 文档类型（已废弃，仅用于兼容）
        :param body: 查询 DSL
        :param params: 额外参数
        :return: 搜索结果
        """
        try:
            kwargs: Dict[str, Any] = {"index": index}
            if body is not None:
                kwargs["body"] = body
            if params is not None:
                kwargs.update(params)

            response = self.es_client.search(**kwargs)
            return response
        except Exception:
            traceback.print_exc()
            return None

    def index(
        self,
        index: Optional[str] = None,
        doc_type: Optional[str] = None,  # noqa: ARG002
        body: Optional[Dict[str, Any]] = None,
        id: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,  # noqa: ARG002
    ) -> Any:
        """
        创建或覆盖文档

        :param index: 索引名称
        :param doc_type: 文档类型（已废弃，仅用于兼容）
        :param body: 文档内容
        :param id: 文档 ID
        :param params: 额外参数（已废弃，仅用于兼容）
        :return: 响应结果
        """
        try:
            kwargs: Dict[str, Any] = {"index": index, "body": body, "id": id}
            response = self.es_client.index(**kwargs)
            return response
        except Exception:
            traceback.print_exc()
            return None

    def update(
        self,
        index: Optional[str] = None,
        doc_type: Optional[str] = None,  # noqa: ARG002
        body: Optional[Dict[str, Any]] = None,
        id: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,  # noqa: ARG002
    ) -> Any:
        """
        更新文档内容

        :param index: 索引名称
        :param doc_type: 文档类型（已废弃，仅用于兼容）
        :param body: 更新内容，包含 doc 字段
        :param id: 文档 ID
        :param params: 额外参数（已废弃，仅用于兼容）
        :return: 响应结果
        """
        try:
            kwargs: Dict[str, Any] = {"index": index, "body": body, "id": id}
            response = self.es_client.update(**kwargs)
            return response
        except Exception:
            traceback.print_exc()
            return None

    def mtermvectors(
        self,
        index: Optional[str] = None,
        doc_type: Optional[str] = None,  # noqa: ARG002
        body: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,  # noqa: ARG002
    ) -> Any:
        """
        获取多个文档的词向量信息

        :param index: 索引名称
        :param doc_type: 文档类型（已废弃，仅用于兼容）
        :param body: 请求体
        :param params: 额外参数（已废弃，仅用于兼容）
        :return: 响应结果
        """
        try:
            kwargs: Dict[str, Any] = {"index": index, "body": body}
            response = self.es_client.mtermvectors(**kwargs)
            return response
        except Exception:
            traceback.print_exc()
            return None

    def bulk(
        self,
        actions: Optional[List[Dict[str, Any]]] = None,
        params: Optional[Dict[str, Any]] = None,  # noqa: ARG002
        request_timeout: int = 100,
        raise_on_error: bool = True,
    ) -> Tuple[int, List[Any]]:
        """
        批量操作文档

        actions 示例:
            [
                {
                    '_op_type': 'index',
                    '_index': 'test_index',
                    '_id': 1,
                    '_source': {'a': 'a', 'b': 'b'}
                },
                {
                    '_op_type': 'index',
                    '_index': 'test_index',
                    '_id': 2,
                    '_source': {'a': 'a', 'b': 'b'}
                },
            ]

        :param actions: 操作列表
        :param params: 额外参数（已废弃，仅用于兼容）
        :param request_timeout: 请求超时时间
        :param raise_on_error: 是否在出错时抛出异常
        :return: (成功数量, 错误列表)
        """
        if actions is None:
            actions = []

        try:
            success, errors = helpers.bulk(
                self.es_client,
                actions=actions,
                request_timeout=request_timeout,
                raise_on_error=raise_on_error,
            )
            # Ensure errors is always a list
            if isinstance(errors, int):
                errors_list: List[Any] = []
            else:
                errors_list = list(errors)  # type: ignore[arg-type]
            return (success, errors_list)
        except Exception:
            traceback.print_exc()
            return (0, [])

    def parallel_bulk(
        self,
        actions: Optional[List[Dict[str, Any]]] = None,
        params: Optional[Dict[str, Any]] = None,  # noqa: ARG002
        request_timeout: int = 100,
        raise_on_error: bool = True,
    ) -> Tuple[int, List[Any]]:
        """
        多线程批量操作文档（当前实现与 bulk 相同）

        actions 示例:
            [
                {
                    '_op_type': 'index',
                    '_index': 'test_index',
                    '_id': 1,
                    '_source': {'a': 'a', 'b': 'b'}
                },
                {
                    '_op_type': 'index',
                    '_index': 'test_index',
                    '_id': 2,
                    '_source': {'a': 'a', 'b': 'b'}
                },
            ]

        :param actions: 操作列表
        :param params: 额外参数（已废弃，仅用于兼容）
        :param request_timeout: 请求超时时间
        :param raise_on_error: 是否在出错时抛出异常
        :return: (成功数量, 错误列表)
        """
        # 注意：在新版本中，parallel_bulk 是一个生成器，返回结果的方式不同
        # 为了保持兼容性，这里使用 bulk 实现
        return self.bulk(actions=actions, request_timeout=request_timeout, raise_on_error=raise_on_error)

    def delete(
        self,
        index: Optional[str] = None,
        doc_type: Optional[str] = None,  # noqa: ARG002
        id: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,  # noqa: ARG002
    ) -> Any:
        """
        删除文档

        :param index: 索引名称
        :param doc_type: 文档类型（已废弃，仅用于兼容）
        :param id: 文档 ID
        :param params: 额外参数（已废弃，仅用于兼容）
        :return: 删除成功返回结果，失败返回 False
        """
        try:
            if index is None or id is None:
                raise ValueError("index and id must be provided")
            return self.es_client.delete(index=index, id=id)
        except NotFoundError:
            return False
        except Exception:
            traceback.print_exc()
            return False

    def delete_by_query(
        self,
        index: Optional[str] = None,
        doc_type: Optional[str] = None,  # noqa: ARG002
        body: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,  # noqa: ARG002
    ) -> bool:
        """
        根据查询条件删除文档

        :param index: 索引名称
        :param doc_type: 文档类型（已废弃，仅用于兼容）
        :param body: 查询条件
        :param params: 额外参数（已废弃，仅用于兼容）
        :return: 删除成功返回 True，失败返回 False
        """
        try:
            kwargs: Dict[str, Any] = {"index": index, "body": body}
            self.es_client.delete_by_query(**kwargs)
            return True
        except Exception:
            traceback.print_exc()
            return False

    def scan(
        self,
        index: Optional[str] = None,
        doc_type: Optional[str] = None,  # noqa: ARG002
        body: Optional[Dict[str, Any]] = None,
        scroll: str = "5m",
        raise_on_error: bool = True,
        preserve_order: bool = False,
        size: int = 5000,
        request_timeout: Optional[int] = None,
        clear_scroll: bool = True,
        **kwargs: Any,
    ):
        """
        扫描所有文档

        :param index: 索引名称
        :param doc_type: 文档类型（已废弃，仅用于兼容）
        :param body: 查询条件
        :param scroll: 滚动超时时间
        :param raise_on_error: 是否在出错时抛出异常
        :param preserve_order: 是否保持顺序
        :param size: 每批返回的文档数量
        :param request_timeout: 请求超时时间
        :param clear_scroll: 是否清除滚动上下文
        :param kwargs: 其他参数
        :return: 文档生成器
        """
        response = helpers.scan(
            self.es_client,
            index=index,
            query=body,
            scroll=scroll,
            raise_on_error=raise_on_error,
            preserve_order=preserve_order,
            size=size,
            request_timeout=request_timeout,
            clear_scroll=clear_scroll,
            **kwargs,
        )
        return response

    def analyze(self, index: str, analyzer: str, text: str) -> Any:
        """
        分析文本

        :param index: 索引名称
        :param analyzer: 分析器名称
        :param text: 待分析文本
        :return: 分析结果
        """
        return self.es_client.indices.analyze(
            index=index,
            body={"text": text, "analyzer": analyzer},
        )


class EsClient6(EsClient):
    """Elasticsearch 6.x 及以上版本客户端"""

    def __init__(self, hosts: Optional[List[str]] = None):
        """
        初始化 ES 6.x 客户端

        :param hosts: ES 节点列表
        """
        super().__init__(hosts=hosts)

    def conn(self) -> Elasticsearch:
        """
        创建 Elasticsearch 6.x 连接

        :return: Elasticsearch 客户端实例
        """
        return Elasticsearch(
            hosts=self.hosts,
            retry_on_timeout=True,
            max_retries=3,
            request_timeout=30,
        )


if __name__ == "__main__":
    # 示例配置
    ES_HOST = ["http://localhost:9200"]
    SNIFF_ON_START = False

    es_client = EsClient(ES_HOST, sniff_on_start=SNIFF_ON_START)

    # #######get#######
    # response = es_client.get(index="zxtt", id="121246")
    # if response:
    #     print(json.dumps(response, ensure_ascii=False))

    #######search#######
    # body = {
    #     "query": {},
    #     "sort": [
    #         {
    #             "create_time": {
    #                 "order": "desc"
    #             }
    #         }
    #     ],
    #     "_source": ["title"]
    # }
    # response = es_client.search(index="aabb", body=body)
    # if response:
    #     print(json.dumps(response, ensure_ascii=False))

    # ######index#######
    # body = {
    #     "id": 21254600,
    #     "title": "兼具座椅与置物功能的脚凳，不仅样子小巧，在视觉上消减了家具体量...",
    #     "content": "测试内容",
    # }
    # response = es_client.index(index="zxtt", body=body, id="21254600")
    # if response:
    #     print(json.dumps(response, ensure_ascii=False))

    # #######bulk#######
    # actions = [
    #     {
    #         '_op_type': 'index',
    #         '_index': 'test_index',
    #         '_id': '1',
    #         '_source': {'a': 'a', 'b': 'b'}
    #     },
    #     {
    #         '_op_type': 'index',
    #         '_index': 'test_index',
    #         '_id': '2',
    #         '_source': {'a': 'a', 'b': 'b'}
    #     },
    # ]
    # success, errors = es_client.bulk(actions=actions)
    # print(f"成功: {success}, 错误: {len(errors)}")

    # #######scan#######
    # body = {
    #     "query": {
    #         "bool": {
    #             "must_not": [
    #                 {
    #                     "term": {
    #                         "check_status": {
    #                             "value": "-1"
    #                         }
    #                     }
    #                 }
    #             ],
    #             "filter": [
    #                 {
    #                     "range": {
    #                         "answer_count": {
    #                             "gt": 0
    #                         }
    #                     }
    #                 }
    #             ]
    #         }
    #     },
    #     "_source": ["id", "create_time", "answer_count"]
    # }
    # for resp in es_client.scan(index="zxtt", body=body):
    #     if "_source" in resp:
    #         print(resp["_source"])

    # #######delete_by_query#######
    # result = es_client.delete_by_query(index="cut_word_data", body={"query": {"match_all": {}}})
    # print(f"删除结果: {result}")

    # #######update#######
    # body = {"doc": {"up_time": 1541671205, "good_comment_num": 71}}
    # response = es_client.update(index="decoration_v1", body=body, id="281657")
    # if response:
    #     print(json.dumps(response, ensure_ascii=False))

    pass
