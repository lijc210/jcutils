from src.api.cron.other.get_email_imap import test
from src.api.cron.other.send_info import send_mail

test(zhuti="#广东实时门店数据", size=30)
send_mail()
