#!encoding=utf-8

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

#集微网
class Spider(object):
    
    def __init__(self,args):
        
        self.ua = UserAgent()
        self.PAGE_NUM = 1
        self.name = '集微网'
        self.driver_normal = True

        self.args = args
        self.args.name = self.name
        self.args.industry_name = self.args.industry
        self.args.industry_type = allinfo.get(self.args.industry_name, ['',''])[1]
        self.args.industry_ID = allinfo.get(self.args.industry_name, ['',''])[0]
        self.args.dom_or_int = 'DOM'
        self.args.source_name = '集微网'
        self.args.fuzeren = '' 

        try:
            self.args.start = datetime.datetime.strptime(self.args.start, "%Y-%m-%d %H:%M:%S")
            self.args.end = datetime.datetime.strptime(self.args.end, "%Y-%m-%d %H:%M:%S")
        except:
            self.args.start = ''
            self.args.end = ''
    
    
    def html2res(self, url, date='', i=1):
        response = requests.get(url, headers={'headers':self.ua.random}, verify=False)
        # 解析 HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        title = soup.find('h1', {'class': 'media-title'}).get_text().strip()
        title = rep_comma(title)
        print('题目:\t', title)

        date = date
        
        # 热度、热词, 点赞，评论
        redu, reci, dianzan, pinglun, yuedu = '', '', '', '', ''
        yuedu = soup.find('div', {'class': 'hot flex-row-center author-read'}).find('span').get_text().strip()

        news = soup.find('div', {'class': 'media-article-content'})

        
        text_maker = HTML2Text()
        text_maker.body_width = 0
        text_maker.ignore_links = True
        text_maker.ignore_tables = True
        md_text = text_maker.handle(str(news))

        start_words = []
        stop_words = []
        clean_md, clean_text, clean_doc = clean_markdown(self.args, i, md_text, start_words=start_words, stop_words=stop_words)

        return clean_md, clean_text, clean_doc, redu, reci, title, date, url, dianzan, pinglun, yuedu
        
        
    def run(self):
        # 待抓取的网页地址，集微网资讯全部最新
        urls = ['https://laoyaoba.com/jwnews/10007']
        idd = 1
        try:
            for url in urls:
                i = 0
                flag = False
                while i < self.PAGE_NUM:
                    if flag:
                        break
                    # 随机暂停几秒，避免过快的请求导致过快的被查到
                    time.sleep(random.randint(2, 5))
                    resp = requests.get(url, headers={'headers':self.ua.random}, verify=False)
                    # print('resp', resp.text)

                    #获取爬取时间范围内文章网址
                    soup = BeautifulSoup(resp.content, 'lxml')
                    all_news_box = soup.find('div', {'id': 'news-list'}).find('ul',{'class':'list-body'})
                    all_news = all_news_box.find_all('li', {'class': 'card'})
                    
                    for new in all_news:
                        # print(new)
                        #判断资讯时间是否符合要求
                        ori_new_time = soup.find('div', {'class': 'time flex-row-center'}).get_text().strip()
                        print(ori_new_time) #分钟前，小时前，  05-05 13:32
                        now_time = datetime.datetime.now()
                        print(now_time)
                        if '分钟' in str(ori_new_time):
                            # print(date_ori)
                            # print(date_ori[:-3])
                            num = int(ori_new_time[:-3].strip())
                            date = now_time - datetime.timedelta(minutes=num)
                            date = datetime.datetime.strptime(str(date).split('.')[0], "%Y-%m-%d %H:%M:%S")
                        elif '小时' in str(ori_new_time):
                            num = int(ori_new_time[:-3].strip())
                            date = now_time - datetime.timedelta(hours=num)
                            date = datetime.datetime.strptime(str(date).split('.')[0], "%Y-%m-%d %H:%M:%S")
                        elif '秒' in str(ori_new_time):
                            num = int(ori_new_time[:-3].strip())
                            date = now_time - datetime.timedelta(seconds=num)
                            date = datetime.datetime.strptime(str(date).split('.')[0], "%Y-%m-%d %H:%M:%S")
                        else:
                            #05-05 13:32
                            if len(ori_new_time.strip().split()) == 2 and len(ori_new_time.strip().split()[0].split('-')) == 2:
                                date = str(now_time.year) + '-' + ori_new_time.strip() + ':00'
                            else:
                                continue
                        print(date)
                        date = datetime.datetime.strptime(str(date), "%Y-%m-%d %H:%M:%S")
                    
                        if self.args.start <= date <= self.args.end:  #时间在爬取范围内，进行内容提取
                            print('资讯时间符合要求，开始处理文本、图片、markdown...')
                            new_url = new['data-href']
                            if not new_url.startswith('http'):
                                new_url = 'https://laoyaoba.com' + new_url
                            print('链接:\t', new_url)
                            try:
                                clean_md, clean_text, clean_doc, redu, reci, title, date, url, dianzan, \
                                    pinglun, yuedu = self.html2res(new_url, date, str(idd))
                                if self.args.keyword == '' or self.args.keyword in clean_text:
                                    save_file(self.args, idd, clean_md, clean_text, clean_doc, redu, reci, title, date, url, dianzan, pinglun, yuedu)
                                    idd += 1
                                else:
                                    print('该文章不包含关键词：{}！跳过！'.format(self.args.keyword))
                                
                            except Exception as e:
                                print(e)
                                print('单链接爬取失败', new_url)
                                continue
                        elif date > self.args.end:
                            print('当前资讯比查找范围最新日期还要新，继续查找')
                            continue
                        else:
                            print('当前资讯过早，结束查找！')
                            flag = True
                            break
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
        