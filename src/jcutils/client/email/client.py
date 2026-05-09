import imaplib


class ImaplibClient:
    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    def connect(self) -> None:
        self.client = imaplib.IMAP4_SSL(self.host, self.port)
        self.client.login(self.username, self.password)

    def disconnect(self):
        self.client.logout()

    def get_mailboxes(self):
        status, mailboxes = self.client.list()
        if status == "OK":
            return mailboxes
        else:
            return None

    def get_messages(self, mailbox):
        """_summary_

        Args:
            mailbox (_type_): 选择一个邮箱

        Returns:
            _type_: 返回此邮箱邮件总数
        """
        status, messages = self.client.select(mailbox, readonly=False)
        if status == "OK":
            return messages
        else:
            return None

    def search_messages(self, mailbox, criteria):
        """_summary_

        Args:
            mailbox (_type_): 选择一个邮箱
            criteria (_type_): 搜索条件

        Returns:
            _type_: 返回符合条件的邮件总数
        """
        status, messages = self.client.select(mailbox, readonly=False)
        if status == "OK":
            status, messages = self.client.search("utf-8", criteria)
            if status == "OK":
                return messages
            else:
                return None
        else:
            return None

    def get_message(self, mailbox, message_id):
        status, message = self.client.fetch(message_id, "(RFC822)")
        if status == "OK":
            return message
        else:
            return None


if __name__ == "__main__":
    client = ImaplibClient("pop.exmail.qq.com", 993, "xxxx@example.com", "xxxxxxx")
    client.connect()
    # 列出邮箱
    mailboxes = client.get_mailboxes()
    # 获取总数
    print(mailboxes)
    if mailboxes:
        for x in mailboxes:
            print(x)
    print(client.get_messages("INBOX"))
    # 获取所有邮件
    messages = client.search_messages("INBOX", "(ALL)")
    if messages:
        print(messages[0].split()[-30:])  # 打印最后三十封
    # 搜索所有标题为"#华东实时数据#"
    # messages = client.search_messages("INBOX", '(SUBJECT "#华东实时数据#")'.encode("utf-8"))
    messages = client.search_messages("INBOX", '(SUBJECT "Example message 2")')
    print(messages)
    # print(client.get_message("INBOX", 1))
    # client.disconnect()
