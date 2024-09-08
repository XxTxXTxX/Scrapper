import os
import time
import requests
from bs4 import BeautifulSoup
# noinspection PyUnresolvedReferences
from urllib.parse import urlparse
# from logger import logger
import re
import urllib
from html2text import HTML2Text
from PIL import Image
import urllib.request
from urllib import request
import base64
import yaml
from datetime import datetime
from datetime import date
from datetime import timedelta
import random
import threading
import shutil
import traceback
import datetime
import argparse
from fake_useragent import UserAgent
from source.utils import *
from docx import Document


#全球半导体观察
class Spider(object):
    
    def __init__(self,args):
        
        self.ua = UserAgent()
        self.PAGE_NUM = 1
        self.name = '全球半导体观察'
        self.driver_normal = True

        self.args = args
        self.args.name = self.name
        self.args.industry_name = self.args.industry
        self.args.industry_type = allinfo.get(self.args.industry_name, ['',''])[1]
        self.args.industry_ID = allinfo.get(self.args.industry_name, ['',''])[0]
        self.args.dom_or_int = 'DOM'
        self.args.source_name = '全球半导体观察'
        self.args.fuzeren = '' 

        try:
            self.args.start = datetime.datetime.strptime(self.args.start, "%Y-%m-%d %H:%M:%S")
            self.args.end = datetime.datetime.strptime(self.args.end, "%Y-%m-%d %H:%M:%S")
        except:
            self.args.start = ''
            self.args.end = ''
        
     
     #将文章链接保存为md
    def html2res(self, url, date='', i=1):
        time.sleep(random.randint(1, 3))
        response = requests.get(url, headers={'headers':self.ua.random}, verify=False)
        # 解析 HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        # 获取文章正文
        # print(soup)
        
        if date != '':
            date = date 
        else:
            date = soup.find('div', {'class': 'newstitle-bottom'}).find('time').get_text().strip()
            date = datetime.datetime.strptime(str(date).split('.')[0], "%Y-%m-%d %H:%M:%S")
        print('日期:\t', date)
        
        title = soup.find('div', {'class': 'newspage-header'}).find('h1').get_text().strip()
        title = rep_comma(title)
        print('题目:\t', title)
        # new_tim = soup.find('div', {'class': 'newstitle-bottom'}).find('time').get_text().strip()
        # print(new_tim)
        # 热度、热词, 点赞，评论
        redu, reci, dianzan, pinglun, yuedu = '', '', '', '', ''
        html = soup.find('div', {'class': 'newspage-cont'})

        start_words = []
        stop_words = []
        clean_md, clean_text, clean_doc = clean_html(self.args, i, html, element=['p','h2','h3','h4'], start_words=start_words, stop_words=stop_words)

        return clean_md, clean_text, clean_doc, redu, reci, title, date, url, dianzan, pinglun, yuedu
            
    
    def run(self):
        url = 'https://www.dramx.com/News/'
        url2 = 'https://www.dramx.com/News/2.html'
        i = 0
        idd = 1
        try:
            flag = False
            while i<self.PAGE_NUM:
                if flag:
                    break
                # 随机暂停几秒，避免过快的请求导致过快的被查到
                time.sleep(random.randint(1, 5))
                resp = requests.get(url, headers={'headers':self.ua.random}, verify=False)
                # print('resp', resp.text)

                #获取近一天内文章网址
                soup = BeautifulSoup(resp.content, 'lxml')
                all_news_box = soup.find('div', {'id': 'divArticleList'})
                all_news = all_news_box.find_all('div', {'class': 'Article-box-cont clear'})
                for new in all_news:
                    detail_url = ''
                    try:
                        # 获取符合时间要求的链接地址 ：
                        detail_url = new.find('div', {'class':'Article-content'}).find('a')['href']
                        detail_url = 'https://www.dramx.com' + detail_url
                        print('链接:\t', detail_url)

                        new_resp = requests.get(detail_url, headers={'headers':self.ua.random}, verify=False)
                        new_soup = BeautifulSoup(new_resp.content, 'lxml')
                        date = new_soup.find('div', {'class': 'newstitle-bottom'}).find('time').get_text().strip()
                        date = datetime.datetime.strptime(str(date).split('.')[0], "%Y-%m-%d %H:%M:%S")
                        if self.args.start <= date <= self.args.end:
                            # 时间符合要求，开始爬取
                            clean_md, clean_text, clean_doc, redu, reci, title, date, url, dianzan, \
                                pinglun, yuedu = self.html2res(detail_url, date, str(idd))
                            if self.args.keyword == '' or self.args.keyword in clean_text:
                                save_file(self.args, idd, clean_md, clean_text, clean_doc, redu, reci, title, date, url, dianzan, pinglun, yuedu)
                                idd += 1
                            else:
                                print('该文章不包含关键词：{}！跳过！'.format(self.args.keyword))
                        elif date > self.args.end:
                            print('当前资讯比查找范围最新日期还要新，继续查找')
                            continue
                        else:
                            print('当前资讯过早，结束查找！')
                            flag = True
                            break           
                    except Exception as e:
                        print(e)
                        print(detail_url + '  download failure !!!')
                        continue
                print(f"第{i}页爬取成功\n")
                i += 1
        except Exception as e:
            print('整体网页爬取异常：%s' % e)
            print(traceback.format_exc())
            pass

        if os.path.exists("./tmp/img/"):
            shutil.rmtree("./tmp/img/")
        os.makedirs("./tmp/img/", exist_ok = True) 
        return



   