import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
import urllib
from html2text import HTML2Text
from PIL import Image
import urllib.request
from urllib import request
import base64
import yaml
import datetime
import random
import threading
import shutil
import traceback
from source.utils import *
import argparse
from fake_useragent import UserAgent
from docx import Document


class Spider(object):
    
    def __init__(self,args):
        
        self.ua = UserAgent()
        self.PAGE_NUM = 1
        self.name = '芯智讯'
        self.driver_normal = True

        self.args = args
        self.args.name = self.name
        self.args.industry_name = self.args.industry
        self.args.industry_type = allinfo.get(self.args.industry_name, ['',''])[1]
        self.args.industry_ID = allinfo.get(self.args.industry_name, ['',''])[0]
        self.args.dom_or_int = 'DOM'
        self.args.source_name = '芯智讯'
        self.args.fuzeren = '' 

        try:
            self.args.start = datetime.datetime.strptime(self.args.start, "%Y-%m-%d %H:%M:%S")
            self.args.end = datetime.datetime.strptime(self.args.end, "%Y-%m-%d %H:%M:%S")
        except:
            self.args.start = ''
            self.args.end = ''
       
    
    #将文章链接保存为md
    def html2res(self, url, date='', i=1):
        response = requests.get(url, headers={'headers':self.ua.random}, verify=False)
        # 解析 HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        # 获取文章正文
        # print(soup)

        date = date
        print('日期:\t', date)
        
        title = soup.find('h3', {'class': 'elementor-heading-title'}).get_text().strip()
        title = rep_comma(title)
        print('题目:\t', title)

        # 热度、热词, 点赞，评论
        redu, reci, dianzan, pinglun, yuedu = '', '', '', '', ''

        dianzan = soup.find('span', {'class': 'count-box'}).get_text()
        # print(zan)
        html = soup.find('div', {'class': 'elementor-widget-theme-post-content'})
        start_words = []
        stop_words = []
        clean_md, clean_text, clean_doc = clean_html(self.args, i, html, element=['p'], start_words=start_words, stop_words=stop_words)

        return clean_md, clean_text, clean_doc, redu, reci, title, date, url, dianzan, pinglun, yuedu
    
    
    def run(self):
        url = 'https://www.icsmart.cn/'
        url2 = 'https://www.icsmart.cn/page/2/'
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

                soup = BeautifulSoup(resp.content, 'lxml')
                all_news_box = soup.find('div', {'class': 'entries'})
                all_news = all_news_box.find_all('article')
                for new in all_news:
                    detail_url = ''
                    try:
                        # 获取符合时间要求的链接地址 ：
                        date = new.find('time')['datetime']  #<time class="ct-meta-element-date" datetime="2024-04-02T14:13:28+08:00">2024年4月2日</time>
                        # print(new_time)
                        date = datetime.datetime.strptime(' '.join(date.split('+')[0].split('T')), "%Y-%m-%d %H:%M:%S")
                        if self.args.start <= date <= self.args.end:
                            detail_url = new.find('h2', {'class':'entry-title'}).find('a')['href']
                            print('链接:\t', detail_url)
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
                        print('单链接爬取失败', detail_url)
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

   