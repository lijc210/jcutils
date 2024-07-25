import json

from src.pyutils.utils.dingtalk import Dingtalk

corpid = "dingjzmhqbmtr9pkmofb"
corpsecret = "ynt53bZOsXrVefVpI5BFviOmjDKdTMfpjeyQOqEGI7BtJjQ1Gtwuv5yrS51RgQpI"
dingtalk = Dingtalk(corpid=corpid, corpsecret=corpsecret)
# res = dingtalk.get_userVisibilities_templates()

# print(json.dumps(res, indent=4))


resp_dict = dingtalk.get_processInstances(
    processInstanceId="wK_Ah4NTTouNnfiIeKomQg08261720162976"
)
print(json.dumps(resp_dict, indent=4, ensure_ascii=False))


# res = dingtalk.download_attachment(processInstanceId="iTLZ9VKERfO3EqVAxdYieA08261719957652", fileId="145257729571")
# print(json.dumps(res, indent=4))
