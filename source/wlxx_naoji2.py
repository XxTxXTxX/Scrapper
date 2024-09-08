# -*- coding:utf-8 -*-
import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
# from logger import logger
import re
from html2text import HTML2Text
from PIL import Image
from urllib import request
from fake_useragent import UserAgent
import base64
import traceback
import shutil
import datetime
from selenium import webdriver
import time
import os
import random
import copy
import yaml
from source.utils import *
from docx import Document



class Spider(object):
    
    def __init__(self,args):
        
        self.ua = UserAgent()
        self.PAGE_NUM = 2
        self.name = '脑机接口社区'
        self.driver_normal = True

        self.args = args
        self.args.name = self.name
        self.args.industry_name = self.args.industry
        self.args.industry_type = allinfo.get(self.args.industry_name, ['',''])[1]
        self.args.industry_ID = allinfo.get(self.args.industry_name, ['',''])[0]
        self.args.dom_or_int = 'DOM'
        self.args.source_name = '脑机接口社区'
        self.args.fuzeren = '' 
        
        try:
            self.args.start = datetime.datetime.strptime(self.args.start, "%Y-%m-%d %H:%M:%S")
            self.args.end = datetime.datetime.strptime(self.args.end, "%Y-%m-%d %H:%M:%S")
        except:
            self.args.start = ''
            self.args.end = ''
    
            
            
    def html2res(self, url, date='', i=1):
        '''抓取单个网页'''
        # page_content = get_pages_content(url)
        # if not page_content:
        #     self.driver_normal = False
        #     raise ValueError("无法用浏览器打开{}".format(url))

        page = requests.get(url, headers={'headers':self.ua.random})
        soup1 = BeautifulSoup(page.content, 'lxml')

        title = soup1.find('h1', {'class': 'rich_media_title'}).text
        title = rep_comma(title)
        print('题目:\t', title)

        # 获取网址点赞量
        dianzan = ''
        print('点赞量:\t', dianzan)

        # 获取网址评论量
        pinglun = ''
        print('评论量:\t', pinglun)

        # 获取网址阅读量
        yuedu = ''
        print('阅读量:\t', yuedu)

        # 热度、热词
        redu, reci = '', ''

        html = soup1.find('div', {'class': 'rich_media_content'})
        
        start_words = []
        stop_words = ['—— End ——']
        clean_md, clean_text, clean_doc = clean_html(self.args, i, html, start_words=start_words, stop_words=stop_words)

        return clean_md, clean_text, clean_doc, redu, reci, title, date, url, dianzan, pinglun, yuedu
    
    
    def run(self):
        
        with open("./utils/naojijiekoushequ.yaml", "r", encoding="gbk") as file:
            file_data = file.read()
        config = yaml.safe_load(file_data)
        print('config', config)
        
        # 请求参数
        url = "https://mp.weixin.qq.com/cgi-bin/appmsg"
        begin = "0"
        
        headers = {
        "Cookie": config[0]['cookie'],
        "User-Agent": config[0]['user_agent']
        }
        
        params = {
            "action": "list_ex",
            "begin": begin,
            "count": "5",
            "fakeid": config[0]['fakeid'],
            "type": "9",
            "token": config[0]['token'],
            "lang": "zh_CN",
            "f": "json",
            "ajax": "1"
        }
        
        
        # 也方便重新运行时设置页数
        flag = False
        i = 1
        for k in range(0, self.PAGE_NUM):
            if flag:
                break
            try:
                begin = k * 5
                params["begin"] = str(begin)
                # 随机暂停几秒，避免过快的请求导致过快的被查到
                time.sleep(random.randint(1, 10))
                resp = requests.get(url, headers=headers, params=params, verify=False)
                # 微信流量控制, 退出
                if resp.json()['base_resp']['ret'] == 200013:
                    print("frequencey control, stop at {}".format(str(begin)))
                    time.sleep(3600)
                    continue

                # 如果返回的内容中为空则结束
                if 'app_msg_list' not in resp.json().keys() or len(resp.json()['app_msg_list']) == 0:
                    print("all ariticle parsed")
                    break

                msg = resp.json()

                if "app_msg_list" in msg:
                    for item in msg["app_msg_list"]:   #item为每篇文章的信息，包括create_time, link, title...
                        
                        aid = str(item['aid'])
                        print('id:\t', aid)
                        
                        detail_url = item['link']
                        print('链接:\t', detail_url)

                        date = datetime.datetime.fromtimestamp(item['create_time'])
                        print('时间:\t', date)
                        
                        try:
                            
                            if self.args.start < date < self.args.end:
                                
                                clean_md, clean_text, clean_doc, redu, reci, title, date, url, dianzan, pinglun, yuedu = self.html2res(detail_url, date, i)  
                                
                                if self.args.keyword == '' or self.args.keyword in clean_text:
                                    
                                    save_file(self.args, i, clean_md, clean_text, clean_doc, redu, reci, title, date, url, dianzan, pinglun, yuedu)
                                    
                                    i += 1
                                    
                                else:
                                    print('该文章不包含关键词：{}！跳过！'.format(self.args.keyword))
                                    
                            elif date < self.args.start:
                                print('文章时间小于起始时间！{}结束爬取！'.format(self.name))
                                flag = True
                                break
                            else:
                                print('文章时间{}不在起始时间{}~结束时间{}之间，跳过！'.format(date, self.args.start, self.args.end))
                                print('===================\n')
                                continue
                        
                        except Exception as e:
                            print('单个网页爬取异常：%s' % e)
                            print(traceback.format_exc())
                            pass
                        print('===================\n')
                            
            except Exception as e:
                print('整体网页爬取异常：%s' % e)
                print(traceback.format_exc())
                pass
            if flag:
                break
            print('第{}页爬取结束'.format(k+1))
            
        time.sleep(1)
 
        
        if os.path.exists("./tmp/img/"):
                shutil.rmtree("./tmp/img/")
        os.makedirs("./tmp/img/", exist_ok = True) 
        return