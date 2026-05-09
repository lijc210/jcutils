"""
Created on 2016/6/12
@author: lijc210@163.com
Desc: kafka-python 工具类

"""

from datetime import datetime

from kafka import KafkaAdminClient, KafkaConsumer, KafkaProducer, TopicPartition
from kafka.errors import KafkaError


class KafkaClient:
    def __init__(self, bootstrap_servers):
        self.bootstrap_servers = bootstrap_servers
        self.admin_client = KafkaAdminClient(bootstrap_servers=self.bootstrap_servers)
        self.producer = KafkaProducer(bootstrap_servers=self.bootstrap_servers)
        self.consumer = None

    def list_topics(self):
        """列出所有主题"""
        topics = self.admin_client.list_topics()
        return topics

    def describe_topic(self, topic_name):
        """查看主题的详细信息"""
        partitions = self.admin_client.describe_topics([topic_name])
        return partitions

    def produce_message(self, topic_name, message, key=None):
        """向指定主题写入消息"""
        try:
            self.producer.send(topic_name, value=message, key=key)
            self.producer.flush()
        except KafkaError as e:
            print(f"Failed to send message: {e}")

    def consume_messages(
        self, topic_name, group_id, auto_offset_reset="earliest", consumer_timeout_ms=60000, offset=None, dtime=None
    ):
        """从指定主题消费消息"""
        if offset is not None:
            """从指定的偏移量开始消费"""
            print(f"从指定的偏移量{offset}开始消费")
            consumer = KafkaConsumer(
                bootstrap_servers=self.bootstrap_servers,
                auto_offset_reset=auto_offset_reset,
                enable_auto_commit=False,  # 禁用自动提交，以便手动控制
                consumer_timeout_ms=consumer_timeout_ms,  # 如果10秒内kafka中没有可供消费的数据，自动退出
            )

            # 获取所有分区
            partitions = consumer.partitions_for_topic(topic_name)
            if not partitions:
                print(f"主题 {topic_name} 未找到分区")
                consumer.close()
                return

            # 获取所有分区
            partitions = consumer.partitions_for_topic(topic_name)

            # 如果主题存在分区，则设置 offsets
            if partitions:
                # 将所有分区的 offset 设置为 0 或指定的 offset
                offsets = {partition: offset for partition in partitions}
            print("offsets:", offsets)

            # 为每个分区分配 TopicPartition
            partitions = [TopicPartition(topic_name, p) for p in offsets.keys()]
            consumer.assign(partitions)

            print(f"设置所有分区的偏移量为{offset}")
            # 设置每个分区的起始 offset
            for partition, offset in offsets.items():
                consumer.seek(TopicPartition(topic_name, partition), offset)

            # 消费消息
            for message in consumer:
                if message.value:
                    yield message.value.decode("utf-8")

        if dtime is not None:
            """从指定的时间开始消费"""
            print(f"从指定的时间{dtime}开始消费")

            # 将时间转换为时间戳（毫秒）
            timestamp = int(datetime.strptime(dtime, "%Y-%m-%d %H:%M:%S").timestamp() * 1000)

            # 创建消费者
            consumer = KafkaConsumer(
                bootstrap_servers=self.bootstrap_servers,
                auto_offset_reset=auto_offset_reset,
                enable_auto_commit=False,  # 禁用自动提交，以便手动控制
                consumer_timeout_ms=consumer_timeout_ms,  # 如果10秒内kafka中没有可供消费的数据，自动退出
                group_id=group_id,
            )

            # 获取所有分区
            partitions = consumer.partitions_for_topic(topic_name)
            if not partitions:
                print(f"主题 {topic_name} 未找到分区")
                consumer.close()
                return

            # 获取每个分区的偏移量
            offsets_for_times = consumer.offsets_for_times(
                {TopicPartition(topic_name, p): timestamp for p in partitions}
            )

            if offsets_for_times:
                tp_list = []
                offset_list = []
                for tp in offsets_for_times:
                    offset = offsets_for_times[tp]
                    if offset:
                        tp_list.append(tp)
                        offset_list.append(offset.offset)
                    else:
                        print(f"分区 {tp.partition} 未找到时间 {timestamp} 的偏移量")

                # 明确分配分区
                consumer.assign(tp_list)
                for i, tp in enumerate(tp_list):
                    offset = offset_list[i]
                    print(f"分区 {tp.partition} 的偏移量为 {offset}")
                    consumer.seek(tp, offset)

                # 消费消息
                for message in consumer:
                    if message.value:
                        yield message.value.decode("utf-8")
            else:
                assert False, "未找到任何分区的偏移量"

            consumer.close()

        # 默认情况，使用 auto_offset_reset 设置
        consumer = KafkaConsumer(
            topic_name,
            group_id=group_id,
            bootstrap_servers=self.bootstrap_servers,
            auto_offset_reset=auto_offset_reset,
            enable_auto_commit=False,  # 禁用自动提交，以便手动控制
            consumer_timeout_ms=consumer_timeout_ms,  # 如果10秒内kafka中没有可供消费的数据，自动退出
        )
        for message in consumer:
            if message.value:
                yield message.value.decode("utf-8")

    def close(self):
        """关闭生产者"""
        if self.producer:
            self.producer.close()


# 示例用法
if __name__ == "__main__":
    pass
    # kafka_client = KafkaClient(bootstrap_servers=CONFIG.BOOTSTRAP_SERVERS)

    # topic_name = "test"
    # group_id = "my_group" + "_" + topic_name + "_tmp6"

    # # 列出主题
    # topics = kafka_client.list_topics()
    # print(json.dumps(topics, ensure_ascii=False))

    # # 查看主题信息
    # partitions = kafka_client.describe_topic(topic_name)
    # print(json.dumps(partitions, ensure_ascii=False))

    # # 发送消息
    # kafka_client.produce_message(topic_name, b"Hello Kafka")

    # # 消费消息（从最早的偏移量开始）
    # for message in kafka_client.consume_messages(topic_name, group_id=group_id, auto_offset_reset="earliest"):
    #     print(message)

    # # 消费消息（从最新的偏移量开始）
    # for message in kafka_client.consume_messages(topic_name, group_id=group_id, auto_offset_reset="latest"):
    #     print(message)

    # # 消费消息（从指定的偏移量开始）有bug,只有第一个分区的 ofset 生效了
    # for message in kafka_client.consume_messages(topic_name, group_id=group_id, offset=5):
    #     print(message)

    # # 消费消息（从指定的时间戳开始）
    # for message in kafka_client.consume_messages(topic_name, group_id=group_id, dtime="2024-08-16 13:50:00"):
    #     print(message)

    # # 关闭连接
    # kafka_client.close()
