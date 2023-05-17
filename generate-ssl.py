import json
import base64
import os
from time import time, sleep
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.ssl.v20191205 import ssl_client, models


start = time()
# 请使用环境变量获取。不要硬编码
# secretId = os.getenv('TENCENT_CLOUD_SECRET_ID')
# secretKey = os.getenv('TENCENT_CLOUD_SECRET_KEY')

secretId = input('请输入 SecretId：')

if secretId == '':
    exit

secretKey = input('请输入 SecretKey: ')
if secretKey == '':
    exit

cred = credential.Credential(secretId, secretKey)
httpProfile = HttpProfile()
httpProfile.endpoint = "ssl.tencentcloudapi.com"
clientProfile = ClientProfile()
clientProfile.httpProfile = httpProfile
domain_name = []
while True:
    domain = input('要申请证书的域名：')  # 输入您需要申请的证书绑定的域名，如不需要继续申请，请直接按回车键
    if domain == '':
        break
    else:
        domain_name.append(domain)


for i in range(len(domain_name)):
    client = ssl_client.SslClient(cred, "", clientProfile)
    try:

        req = models.ApplyCertificateRequest()
        params = {
            "DvAuthMethod": "DNS_AUTO",
            "DomainName": domain_name[i]
        }
        req.from_json_string(json.dumps(params))

        resp = client.ApplyCertificate(req)
        response = json.loads(resp.to_json_string())
        print('域名：{0}资料已提交，五秒钟后自动验证'.format(domain_name[i]))
        certid = response['CertificateId']
        sleep(5)
        try:
            req1 = models.CompleteCertificateRequest()
            params1 = {
                "CertificateId": certid
            }
            req1.from_json_string(json.dumps(params1))

            resp1 = client.CompleteCertificate(req1)
            response1 = json.loads(resp1.to_json_string())
            print('域名：{0}验证成功！准备下载证书'.format(domain_name[i]))
            try:
                req2 = models.DownloadCertificateRequest()
                params2 = {
                    "CertificateId": certid
                }
                req2.from_json_string(json.dumps(params2))

                resp2 = client.DownloadCertificate(req2)
                response2 = json.loads(resp2.to_json_string())
                # print(response2['Content'])
                content = response2['Content']
                with open("{0}.zip".format(domain_name[i]), "wb") as f:

                    f.write(base64.b64decode(content))
                    f.close()
            except TencentCloudSDKException as err:
                print(err)
        except TencentCloudSDKException as err:
            print(err)
    except TencentCloudSDKException as err:
        print(err)
end = time()
print('本次代码执行共耗时：', round(end - start, 2), 's')
