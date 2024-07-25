"""
Created on 2016/6/12
@author: lijc210@163.com
Desc: 功能描述。

auto_offset_reset参数:
earliest
当各分区下有已提交的offset时，从提交的offset开始消费；无提交的offset时，从头开始消费
latest
当各分区下有已提交的offset时，从提交的offset开始消费；无提交的offset时，消费新产生的该分区下的数据
none
topic各分区都存在已提交的offset时，从offset后开始消费；只要有一个分区不存在已提交的offset，则抛出异常

auto_commit_enable参数
在kafka拉取到数据之后就直接提交offset
设置为Flase的时候不需要添加 consumer_group

reset_offset_on_start参数：
为false，那么消费会从上一次消费的偏移量之后开始进行（比如上一次的消费偏移量为4，那么消费会从5开始）
为true，会自动从 auto_offset_reset 指定的位置开始消费


目前是配置为：上一次的消费偏移量开始读
"""

from pykafka import KafkaClient
from pykafka.simpleconsumer import OffsetType


class PykafkaClient:
    def __init__(
        self,
        hosts="10.207.38.169:9092",
    ):
        self.hosts = hosts
        self.client = KafkaClient(hosts=self.hosts)

    def get_topics(self):
        return self.client.topics

    def get_partition_offsets(self, topic, earliest=False):
        topic_obj = self.client.topics[topic]
        offsets = (
            topic_obj.earliest_available_offsets()
            if earliest
            else topic_obj.latest_available_offsets()
        )
        return {k: v.offset[0] - 1 for k, v in offsets.items()}

    def get_consumer(
        self,
        topic,
        auto_offset_reset=OffsetType.EARLIEST,
        reset_offset_on_start=False,
        zookeeper_connect=None,
        offset=None,
        consumer_group=None,
    ):
        """
        # 从最开始读
        auto_offset_reset = OffsetType.EARLIEST
        # 从最新开始读
        auto_offset_reset = OffsetType.LATEST
        # 从指定 offset 读
        offset = 100
        """
        topic_obj = self.client.topics[topic]
        partitions = topic_obj.partitions
        earliest_offset = self.get_partition_offsets(topic, earliest=True)
        last_offset = self.get_partition_offsets(topic)
        print("分区 {}".format(partitions))
        print("最早可用offset {}".format(earliest_offset))
        print("最近可用offset {}".format(last_offset))

        # managed=True 设置后，使用新式reblance分区方法，不需要使用zk，
        # 而False是通过zk来实现reblance的需要使用zk
        balanced_consumer = topic_obj.get_balanced_consumer(
            consumer_group=consumer_group,
            auto_commit_enable=False,
            managed=True,
            auto_offset_reset=auto_offset_reset,
            reset_offset_on_start=reset_offset_on_start,
            fetch_message_max_bytes=1024 * 1024,
        )
        held_offset = balanced_consumer.held_offsets
        print("当前消费者分区offset情况{}".format(held_offset))

        if offset is not None:
            offset = [(partitions[k], offset) for k in partitions]
            balanced_consumer.reset_offsets(offset)

        while True:
            msg = balanced_consumer.consume()
            if msg:
                offset = balanced_consumer.held_offsets
                print("当前位移：{}".format(offset))
                print(msg.value)
                balanced_consumer.commit_offsets()  # commit一下
            else:
                print("没有数据")

    def produce_messages(self, topic, messages):
        topic = self.client.topics[topic]  # 指定topic,没有就新建
        producer = topic.get_producer()
        for msg in messages:
            producer.produce(msg)
            print("produce message: {}".format(msg))
        producer.stop()


if __name__ == "__main__":
    pykafka_client = PykafkaClient(hosts="10.194.6.80:9092,10.194.9.44:9092")
    topic = "AIS20201114183546.dbo.T_SAL_ORDER"

    # 获取主题列表
    topics = pykafka_client.get_topics()

    # 打印主题列表
    for topic in topics:
        print(topic)

    # 获取主题分区最新offset
    # topic = "AIS20201114183546.dbo.T_SAL_ORDER"
    # partitions = pykafka_client.get_partition_offsets(topic)
    # print(partitions)

    # 消费消息
    # pykafka_client.get_consumer(
    #     topic=topic, auto_offset_reset=OffsetType.EARLIEST, offset=None, consumer_group="test_group"
    # )

    # 生产消息
    # topic = "test_topic"
    # messages = [b"hello world", b"hello guoquan", b"hello kafka"]
    # pykafka_client.produce_messages(topic, messages)

    # 删除topic
    # kafka-topics.sh --bootstrap-server your_broker_list_here --delete --topic your_topic_name_here
