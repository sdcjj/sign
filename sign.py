import json
import time
import requests
from PyCookieCloud import PyCookieCloud


def load_config():
    with open("sign.json", "r", encoding="utf-8") as file:
        return json.load(file)

def load_clound(ccConfig):
    cookie_cloud = PyCookieCloud(ccConfig.get("domain"), ccConfig.get("uuid"), ccConfig.get("pwd"))
    the_key = cookie_cloud.get_the_key()
    if not the_key:
        print("Failed to get the key")
        return
    encrypted_data = cookie_cloud.get_encrypted_data()
    if not encrypted_data:
        print("Failed to get encrypted data")
        return
    decrypted_data = cookie_cloud.get_decrypted_data()
    if not decrypted_data:
        print("Failed to get decrypted data")
        return
    checkMap= {}

    for site in decrypted_data:
        cookies= decrypted_data.get(site)
        formatted_cookies = []
        for cookie in cookies:
            formatted_cookies.append(f"{cookie['name']}={cookie['value']}")

        result = ';'.join(formatted_cookies)
        checkMap[site]=result
    return checkMap

def is_check_in(resp):
    if "签到成功" in resp.text:
        return True
    if "签到获得" in resp.text:
        return True
    if "簽到獲得" in resp.text:
        return True
    if "已经签到" in resp.text:
        return True
    if "already attended" in resp.text:
        return True
    return False

def buildUrl(site):
    domain = site.get("domain", "").strip()
    if domain == "":
        return

    if("hdcity.city" in domain):
        return f"{domain}sign"
    
    path = site.get("path", "").strip()
    if path == "":
        checkin_url = f"{domain}attendance.php"
    else:
        checkin_url = f"{domain}{path}"
    return checkin_url

def get_response(site):
    domain = site.get("domain", "").strip()
    if domain == "":
        print(f"domain is empty {site}")
        return
    
    checkin_url = buildUrl(site)

    try:
        resp = requests.get(
            url=checkin_url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
                "Cookie": site.get("cookie"),
            },
            timeout=30,
        )

        return resp
    except Exception as e:
        print(f"{domain}访问失败")
        print(e)
    return None


conf = load_config()
sleep = conf["sleep"]

cookie_cloud = conf["cookie_cloud"]
checkMap= load_clound(cookie_cloud)

cloud_sites = conf["cloud_sites"]
for site in cloud_sites:
    chekcData={
        "domain":f"https://{site}/",
        "cookie":checkMap.get(site),
    }
    resp= get_response(chekcData)
    if(not is_check_in(resp)):
        print(f"{site}签到失败")
        print(resp.text)
    else:
        print(f"{site}签到成功")
    time.sleep(sleep)


path_sites = conf["path_sites"]
for path_site in path_sites:
    site = path_site.get("domain")
    chekcData={
        "domain":f"{path_site.get("scheme")}://{site}/",
        "path":path_site.get("path"),
        "cookie":checkMap.get(site),
    }
    get_response(chekcData)
    time.sleep(sleep)
