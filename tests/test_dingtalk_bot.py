"""
钉钉机器人单元测试
"""

import os
import unittest
from unittest.mock import MagicMock, patch

from jcutils.client.dingtalk import DingTalkBot


class TestDingTalkBot(unittest.TestCase):
    """钉钉机器人测试类"""

    def setUp(self):
        """测试前准备"""
        self.access_token = "test_access_token"
        self.secret = "test_secret"
        self.bot = DingTalkBot(access_token=self.access_token, secret=self.secret)

    def test_init(self):
        """测试初始化"""
        self.assertEqual(self.bot.access_token, self.access_token)
        self.assertEqual(self.bot.secret, self.secret)
        self.assertEqual(self.bot.base_url, "https://oapi.dingtalk.com")

    def test_get_sign(self):
        """测试签名生成"""
        timestamp, sign = self.bot._get_sign()
        self.assertIsInstance(timestamp, str)
        self.assertIsInstance(sign, str)
        self.assertTrue(len(timestamp) > 0)
        self.assertTrue(len(sign) > 0)

    def test_get_webhook_url_with_secret(self):
        """测试带密钥的Webhook URL生成"""
        url = self.bot._get_webhook_url()
        self.assertIn("access_token=test_access_token", url)
        self.assertIn("timestamp=", url)
        self.assertIn("sign=", url)
        self.assertTrue(url.startswith("https://oapi.dingtalk.com/robot/send?"))

    def test_get_webhook_url_without_secret(self):
        """测试不带密钥的Webhook URL生成"""
        bot = DingTalkBot(access_token=self.access_token)
        url = bot._get_webhook_url()
        self.assertEqual(url, f"https://oapi.dingtalk.com/robot/send?access_token={self.access_token}")

    def test_encode_image(self):
        """测试图片编码"""
        # 创建一个临时图片文件用于测试
        test_file = "test_image.png"
        try:
            # 创建一个简单的PNG文件（1x1像素）
            with open(test_file, "wb") as f:
                # PNG文件头
                f.write(b"\x89PNG\r\n\x1a\n")
                # IHDR块
                f.write(b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde")
                # IDAT块
                f.write(b"\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N")
                # IEND块
                f.write(b"\x00\x00\x00\x00IEND\xaeB`\x82")

            base64_data, md5 = DingTalkBot.encode_image(test_file)
            self.assertIsInstance(base64_data, str)
            self.assertIsInstance(md5, str)
            self.assertTrue(len(base64_data) > 0)
            self.assertEqual(len(md5), 32)  # MD5是32位十六进制字符串
        finally:
            # 清理临时文件
            if os.path.exists(test_file):
                os.remove(test_file)

    @patch("jcutils.client.dingtalk.bot.requests.post")
    def test_send_text_success(self, mock_post):
        """测试发送文本消息成功"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"errcode": 0, "errmsg": "ok"}
        mock_post.return_value = mock_response

        result = self.bot.send_text("测试消息", ["@all"])

        self.assertEqual(result["errcode"], 0)
        mock_post.assert_called_once()

    @patch("jcutils.client.dingtalk.bot.requests.post")
    def test_send_markdown_success(self, mock_post):
        """测试发送Markdown消息成功"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"errcode": 0, "errmsg": "ok"}
        mock_post.return_value = mock_response

        result = self.bot.send_markdown("# 测试标题\n测试内容", title="测试")

        self.assertEqual(result["errcode"], 0)
        mock_post.assert_called_once()

    @patch("jcutils.client.dingtalk.bot.requests.post")
    def test_send_image_success(self, mock_post):
        """测试发送图片消息成功"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"errcode": 0, "errmsg": "ok"}
        mock_post.return_value = mock_response

        result = self.bot.send_image("base64_data", "md5_hash")

        self.assertEqual(result["errcode"], 0)
        mock_post.assert_called_once()

    @patch("jcutils.client.dingtalk.bot.requests.post")
    def test_send_action_card_success(self, mock_post):
        """测试发送ActionCard消息成功"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"errcode": 0, "errmsg": "ok"}
        mock_post.return_value = mock_response

        result = self.bot.send_action_card(
            title="测试标题", text="测试内容", btns=[{"title": "按钮1", "actionURL": "https://example.com"}]
        )

        self.assertEqual(result["errcode"], 0)
        mock_post.assert_called_once()

    @patch("jcutils.client.dingtalk.bot.requests.post")
    def test_send_feed_card_success(self, mock_post):
        """测试发送FeedCard消息成功"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"errcode": 0, "errmsg": "ok"}
        mock_post.return_value = mock_response

        result = self.bot.send_feed_card(
            title="测试标题",
            links=[{"title": "链接1", "messageURL": "https://example.com", "picURL": "https://example.com/image.jpg"}],
        )

        self.assertEqual(result["errcode"], 0)
        mock_post.assert_called_once()

    @patch("jcutils.client.dingtalk.bot.requests.post")
    def test_handle_response_rate_limit(self, mock_post):
        """测试处理接口调用超过限制错误"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"errcode": 45009, "errmsg": "interface调用超出限制"}
        mock_post.return_value = mock_response

        with self.assertRaises(ValueError):
            self.bot._handle_response(mock_response)

    @patch("jcutils.client.dingtalk.bot.requests.post")
    def test_handle_response_other_error(self, mock_post):
        """测试处理其他错误"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"errcode": 10001, "errmsg": "签名不正确"}
        mock_post.return_value = mock_response

        # 应该不抛出异常，而是发送错误信息
        result = self.bot._handle_response(mock_response)
        self.assertEqual(result["errcode"], 10001)
        # 应该调用两次post：一次原始请求，一次错误回退
        # 注意：由于_get_webhook_url()也会调用_get_sign()，而_get_sign()中使用了hmac和base64，
        # 这些在mock环境中也会被调用，所以需要检查call_count
        # 在错误回退中，我们会调用_get_webhook_url()，这会调用_get_sign()，
        # 但_get_sign()不是HTTP调用，所以不会被mock
        # 因此，mock_post应该被调用一次（错误回退）
        self.assertEqual(mock_post.call_count, 1)


if __name__ == "__main__":
    unittest.main()
