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
class Report(object):
    def __init__(self, stuid, password, data_path, emer_person, relation, emer_phone):
        self.stuid = stuid
        self.password = password
        self.data_path = data_path
        self.emer_person = emer_person
        self.relation = relation
        self.emer_phone = emer_phone

    def report(self):
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

        # 自动出校报备
        ret = session.get("https://weixine.ustc.edu.cn/2020/apply/daliy/i")
        #print(ret.status_code)
        #print(ret.url)
        if (ret.status_code == 200):
        	#每日报备
        	print("开始例行报备.")
        	data = ret.text
        	data = data.encode('ascii','ignore').decode('utf-8','ignore')
        	soup = BeautifulSoup(data, 'html.parser')
        	token2 = soup.find("input", {"name": "_token"})['value']
        	start_date = soup.find("input", {"id": "start_date"})['value']
        	end_date = soup.find("input", {"id": "end_date"})['value']
        	
        	print("{}---{}".format(start_date, end_date))

        	REPORT_URL = "https://weixine.ustc.edu.cn/2020/apply/daliy/post"
        	REPORT_DATA = {
        		'_token': token2,
        		'start_date': start_date,
        		'end_date': end_date
        	}

        	ret = session.post(url=REPORT_URL, data=REPORT_DATA)
       		print(ret.status_code)
            #print(ret.text)

        elif(ret.status_code == 302):
        	print("你这周已经报备过了.")
        	#老页面的判定, 新页面已经不需要
        else:
        	print("error! code "+ret.status_code)
        	#出错



        data = getform.text
        data = data.encode('ascii','ignore').decode('utf-8','ignore')
        soup = BeautifulSoup(data, 'html.parser')
        token = soup.find("input", {"name": "_token"})['value']

        with open(self.data_path, "r+") as f:
            data = f.read()
            data = json.loads(data)
            data["jinji_lxr"]=self.emer_person
            data["jinji_guanxi"]=self.relation
            data["jiji_mobile"]=self.emer_phone
            data["_token"]=token
        #print(data)


        headers = {
            'authority': 'weixine.ustc.edu.cn',
            'origin': 'https://weixine.ustc.edu.cn',
            'upgrade-insecure-requests': '1',
            'content-type': 'application/x-www-form-urlencoded',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.100 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'referer': 'https://weixine.ustc.edu.cn/2020/home',
            'accept-language': 'zh-CN,zh;q=0.9',
            'Connection': 'close',
            'cookie': "PHPSESSID=" + cookies.get("PHPSESSID") + ";XSRF-TOKEN=" + cookies.get("XSRF-TOKEN") + ";laravel_session="+cookies.get("laravel_session"),
        }

        url = "https://weixine.ustc.edu.cn/2020/daliy_report"
        resp=session.post(url, data=data, headers=headers)
        print(resp)
        data = session.get("https://weixine.ustc.edu.cn/2020").text
        soup = BeautifulSoup(data, 'html.parser')
        pattern = re.compile("202[0-9]-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}")
        token = soup.find(
            "span", {"style": "position: relative; top: 5px; color: #666;"})
        flag = False
        if pattern.search(token.text) is not None:
            date = pattern.search(token.text).group()
            print("Latest report: " + date)
            date = date + " +0800"
            reporttime = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S %z")
            print("Reporttime : " + format(reporttime))
            timenow = datetime.datetime.now(pytz.timezone('Asia/Shanghai'))
            print("Nowtime : " + format(timenow))
            delta = timenow - reporttime
            delta_nega = reporttime - timenow
            print("Delta is ")
            print(delta)
            print("Delta_Negative is ")
            print(delta_nega)
            if delta.seconds < 120 or delta_nega.seconds < 120:
                flag = True
            if delta.seconds < delta_nega.seconds:
                print("{} second(s) before.".format(delta.seconds))
            else:
                print("{} second(s) before.".format(delta_nega.seconds))
        if flag == False:
            print("Report FAILED!")
        else:
            print("Report SUCCESSFUL!")
        return flag

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
    parser = argparse.ArgumentParser(description='URC nCov auto report script.')
    parser.add_argument('data_path', help='path to your own data used for post method', type=str)
    parser.add_argument('stuid', help='your student number', type=str)
    parser.add_argument('password', help='your CAS password', type=str)
    parser.add_argument('emer_person', help='emergency person', type=str)
    parser.add_argument('relation', help='relationship between you and he/she', type=str)
    parser.add_argument('emer_phone', help='phone number', type=str)
    args = parser.parse_args()
    autorepoter = Report(stuid=args.stuid, password=args.password, data_path=args.data_path, emer_person=args.emer_person, relation=args.relation, emer_phone=args.emer_phone)
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
