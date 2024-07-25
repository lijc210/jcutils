import imaplib

# def login():
#     M = imaplib.IMAP4_SSL(CONFIG.EMAIL_SERVER, ssl_context=None)
#     M.login(CONFIG.EMAIL_ADDR, CONFIG.EMAIL_PASSWORD)
#     M.select("INBOX", readonly=False)
#     return M


def login():
    M = imaplib.IMAP4_SSL("imap.189.cn", ssl_context=None)
    M.login("19901718151@189.cn", "qhU8ssvcER")
    M.select("INBOX", readonly=False)
    return M


m = login()
print(m.state)
