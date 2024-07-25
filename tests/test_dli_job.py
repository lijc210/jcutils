import urllib3
from huaweicloudsdkcore.auth.credentials import BasicCredentials
from huaweicloudsdkcore.http.http_config import HttpConfig
from huaweicloudsdkdli.v1.dli_client import DliClient
from huaweicloudsdkdli.v1.model import ListFlinkJobsRequest, ShowFlinkJobRequest
from urllib3.exceptions import InsecureRequestWarning

from src.api.config import CONFIG

urllib3.disable_warnings(InsecureRequestWarning)

config = HttpConfig.get_default_config()
config.ignore_ssl_verification = True
credentials = BasicCredentials(CONFIG.DLI_AK, CONFIG.DLI_SK, CONFIG.DLI_project_id)

dli_client = (
    DliClient.new_builder()
    .with_http_config(config)
    .with_credentials(credentials)
    .with_endpoint(CONFIG.DLI_endpoint)
    .build()
)

request = ListFlinkJobsRequest(limit=100)
flink_jobs = dli_client.list_flink_jobs(request)
text = ""
for adict in flink_jobs.job_list.jobs:
    # print(adict.job_id, adict.name)
    request = ShowFlinkJobRequest(job_id=adict.job_id)
    flink_job = dli_client.show_flink_job(request)
    if "ads_pay_card_account" in flink_job.job_detail.sql_body:
        print("aaaaaaaaaa", adict.name)

if __name__ == "__main__":
    pass
