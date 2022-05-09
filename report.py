#!/bin/python3
# encoding=utf8
import requests
import json
import time
import datetime
import pytz
import re
import sys
import argparse

import io
import os
from bs4 import BeautifulSoup
import PIL
import pytesseract
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
CAS_RETURN_URL = "https://weixine.ustc.edu.cn/2020/caslogin"
UPLOAD_PAGE_URL = "https://weixine.ustc.edu.cn/2020/upload/xcm"
UPLOAD_IMAGE_URL = "https://weixine.ustc.edu.cn/2020img/api/upload_for_student"
UPLOAD_INFO = [
    (1, "14-day Big Data Trace Card"),
    (2, "An Kang code"),
]
DEFAULT_PIC = ['https://raw.githubusercontent.com/pipixia244/South_Seven-AutoReport/master/14day.jpg',
               'https://raw.githubusercontent.com/pipixia244/South_Seven-AutoReport/master/ankang.jpg']


class Report(object):
    def __init__(self, stuid, password, data_path, emer_person, relation, emer_phone, dorm_building, dorm, _14days_pic, ankang_pic, gid, sign):
        self.stuid = stuid
        self.password = password
        self.data_path = data_path
        self.emer_person = emer_person
        self.relation = relation
        self.emer_phone = emer_phone
        self.dorm_building = dorm_building
        self.dorm = dorm
        self.pic = [_14days_pic, ankang_pic]
        self.gid = gid
        self.sign = sign

    def report(self):

        # 统一验证登录
        loginsuccess = False
        retrycount = 5
        while (not loginsuccess) and retrycount:
            session = self.login()
            cookies = session.cookies
            getform = session.get("https://weixine.ustc.edu.cn/2020")
            retrycount = retrycount - 1
            if getform.url != "https://weixine.ustc.edu.cn/2020/home":
                print("Login Failed! Retrying...")
            else:
                print("Login Successful!")
                loginsuccess = True
        if not loginsuccess:
            return False

        # 获取基本数据信息
        data = getform.text
        data = data.encode('ascii', 'ignore').decode('utf-8', 'ignore')
        soup = BeautifulSoup(data, 'html.parser')
        token = soup.find("input", {"name": "_token"})['value']

        with open(self.data_path, "r+") as f:
            data = f.read()
            data = json.loads(data)
            data["jinji_lxr"] = self.emer_person
            data["jinji_guanxi"] = self.relation
            data["jiji_mobile"] = self.emer_phone
            data["dorm_building"] = self.dorm_building
            data["dorm"] = self.dorm
            data["_token"] = token
        # print(data)

        # 自动健康打卡
        headers = {
            'authority': 'weixine.ustc.edu.cn',
            'origin': 'https://weixine.ustc.edu.cn',
            'upgrade-insecure-requests': '1',
            'content-type': 'application/x-www-form-urlencoded',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.100 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'referer': 'https://weixine.ustc.edu.cn/2020/home',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cookie': "PHPSESSID=" + cookies.get("PHPSESSID") + ";XSRF-TOKEN=" + cookies.get("XSRF-TOKEN") + ";laravel_session="+cookies.get("laravel_session"),
        }

        url = "https://weixine.ustc.edu.cn/2020/daliy_report"
        resp = session.post(url, data=data, headers=headers)
        print(resp)
        res = session.get("https://weixine.ustc.edu.cn/2020/apply/daliy/i?t=3")
        if(res.status_code < 400 and (res.url == "https://weixine.ustc.edu.cn/2020/upload/xcm" or res.url == "https://weixine.ustc.edu.cn/2020/apply/daliy/i?t=3")):
            print("report success!")
        elif(res.status_code < 400 and res.url != "https://weixine.ustc.edu.cn/2020/upload/xcm"):
            print(res.url)
            print("report failed")
            return False
        else:
            print("unknown error, code: "+str(res.status_code))

        # 自动上传健康码
        can_upload_code = 1
        r = session.get(UPLOAD_PAGE_URL)
        pos = r.text.find("每周可上报时间为周一凌晨0:00至周日中午12:00,其余时间将关闭相关功能。")
        #print("position: "+str(pos))
        if(pos != -1):
            print("当前处于不可上报时间，请换其他时间上传健康码。")
            can_upload_code = 0
        for idx, description in UPLOAD_INFO:
            if(can_upload_code == 0):
                print(f"ignore {description}.")
                continue
            if(self.pic[idx - 1] == ''):
                self.pic[idx - 1] = DEFAULT_PIC[idx - 1]
            #print(self.pic[idx - 1])
            ret = session.get(self.pic[idx - 1])
            blob = ret.content
            # print(len(blob))
            # print(ret.status_code)
            if blob == None or ret.status_code != 200:
                print(f"ignore {description}.")
                continue

            # print(r.text)
            r = session.get(UPLOAD_PAGE_URL)
            x = re.search(r"""<input.*?name="_token".*?>""", r.text).group(0)
            re.search(r'value="(\w*)"', x).group(1)

            url = UPLOAD_IMAGE_URL

            payload = {
                "_token": token,
                "gid": self.gid,
                "sign": self.sign,
                "t": idx,
                "id": f"WU_FILE_{idx-1}",
                "name": f"{description}.jpg",
                "type": "image/jepg",
                "lastModifiedDate": datetime.datetime.now().strftime("%a %b %d %Y %H:%M:%S GMT+0800 (China Standard Time)"),
                "size": f"{len(blob)}",
            }
            payload_files = {"file": (payload["name"], blob)}
            headers_upload = session.headers
            headers_upload['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.100 Safari/537.36'
            r = session.post(url, data=payload,
                             files=payload_files, headers=headers_upload)
            print(r)
            # print(r.text)
            r.raise_for_status()
            print(f"Uploaded {description}: {r.json()['status']}")

        # 自动出校报备
        ret = session.get("https://weixine.ustc.edu.cn/2020/apply/daliy/i?t=3")
        # print(ret.status_code)
        if (ret.url == "https://weixine.ustc.edu.cn/2020/upload/xcm"):
            print("未上传两码，请手动上传两码或杀了制定这个规则的壬的马。")
            return True
        if (ret.status_code == 200):
            # 每日报备
            print("开始例行报备.")
            data = ret.text
            data = data.encode('ascii', 'ignore').decode('utf-8', 'ignore')
            soup = BeautifulSoup(data, 'html.parser')
            token2 = soup.find("input", {"name": "_token"})['value']
            start_date = soup.find("input", {"id": "start_date"})['value']
            end_date = soup.find("input", {"id": "end_date"})['value']

            print("{}---{}".format(start_date, end_date))

            REPORT_URL = "https://weixine.ustc.edu.cn/2020/apply/daliy/ipost"
            RETURN_COLLEGE = {'东校区', '西校区', '中校区', '南校区', '北校区'}
            REPORT_DATA = {
                '_token': token2,
                'start_date': start_date,
                'end_date': end_date,
                'return_college[]': RETURN_COLLEGE,
                'reason': "上课/自习",
                't': 3,
            }

            ret = session.post(url=REPORT_URL, data=REPORT_DATA)
            print(ret.status_code)
            # print(ret.text)

        elif(ret.status_code == 302):
            print("你这周已经报备过了.")
            #老页面的判定, 新页面已经不需要
        else:
            print("error! code "+ret.status_code)
            # 出错
            return False
        return True

    def login(self):
        retries = Retry(total=5,
                        backoff_factor=0.5,
                        status_forcelist=[500, 502, 503, 504])
        s = requests.Session()
        s.mount("https://", HTTPAdapter(max_retries=retries))
        s.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36 Edg/92.0.902.67"
        url = "https://passport.ustc.edu.cn/login?service=http%3A%2F%2Fweixine.ustc.edu.cn%2F2020%2Fcaslogin"
        r = s.get(url, params={"service": CAS_RETURN_URL})
        x = re.search(r"""<input.*?name="CAS_LT".*?>""", r.text).group(0)
        cas_lt = re.search(r'value="(LT-\w*)"', x).group(1)

        CAS_CAPTCHA_URL = "https://passport.ustc.edu.cn/validatecode.jsp?type=login"
        r = s.get(CAS_CAPTCHA_URL)
        img = PIL.Image.open(io.BytesIO(r.content))
        pix = img.load()
        for i in range(img.size[0]):
            for j in range(img.size[1]):
                r, g, b = pix[i, j]
                if g >= 40 and r < 80:
                    pix[i, j] = (0, 0, 0)
                else:
                    pix[i, j] = (255, 255, 255)
        lt_code = pytesseract.image_to_string(img).strip()

        data = {
            'model': 'uplogin.jsp',
            'service': 'https://weixine.ustc.edu.cn/2020/caslogin',
            'username': self.stuid,
            'password': str(self.password),
            'warn': '',
            'showCode': '1',
            'button': '',
            'CAS_LT': cas_lt,
            'LT': lt_code
        }
        s.post(url, data=data)

        print("lt-code is {}, login...".format(lt_code))
        return s


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='URC nCov auto report script.')
    parser.add_argument(
        'data_path', help='path to your own data used for post method', type=str)
    parser.add_argument('stuid', help='your student number', type=str)
    parser.add_argument('password', help='your CAS password', type=str)
    parser.add_argument('emer_person', help='emergency person', type=str)
    parser.add_argument(
        'relation', help='relationship between you and he/she', type=str)
    parser.add_argument('emer_phone', help='phone number', type=str)
    parser.add_argument('dorm_building', help='dorm building num', type=str)
    parser.add_argument('dorm', help='dorm number', type=str)
    parser.add_argument(
        '_14days_pic', help='14 days Big Data Trace Card', type=str)
    parser.add_argument('ankang_pic', help='An Kang Health Code', type=str)
    parser.add_argument('gid', help="gid", type=str)
    parser.add_argument('sign', help="sign", type=str)
    args = parser.parse_args()
    autorepoter = Report(stuid=args.stuid, password=args.password, data_path=args.data_path, emer_person=args.emer_person,
                         relation=args.relation, emer_phone=args.emer_phone, dorm_building=args.dorm_building, dorm=args.dorm,
                         _14days_pic=args._14days_pic, ankang_pic=args.ankang_pic, gid=args.gid, sign=args.sign)
    count = 5
    while count != 0:
        ret = autorepoter.report()
        if ret != False:
            break
        print("Report Failed, retry...")
        count = count - 1
    if count != 0:
        exit(0)
    else:
        exit(-1)
