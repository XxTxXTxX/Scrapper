#!encoding=utf-8
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
import random
import threading
import shutil
import traceback
from source.utils import *
import argparse
import datetime
from fake_useragent import UserAgent
from docx import Document

#与非网
class Spider(object):
    
    def __init__(self,args):
        
        self.ua = UserAgent()
        self.PAGE_NUM = 1
        self.name = '与非网'
        self.driver_normal = True

        self.args = args
        self.args.name = self.name
        self.args.industry_name = self.args.industry
        self.args.industry_type = allinfo.get(self.args.industry_name, ['',''])[1]
        self.args.industry_ID = allinfo.get(self.args.industry_name, ['',''])[0]
        self.args.dom_or_int = 'DOM'
        self.args.source_name = '与非网'
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
        
        title = soup.find('div', {'class': 'title'}).get_text()
        title = rep_comma(title)
        print('题目:\t', title)

        # 转化时间
        if date != '':
            date = date 
        else:
            date_ori = soup.find('div',{'class':'left-part'}).find('span').get_text()    #分钟前，小时前
            now_time = datetime.datetime.now()
            if '分钟' in str(date_ori):
                num = int(date_ori[:-3])
                date = now_time - datetime.timedelta(minutes=num)
                date = datetime.datetime.strptime(str(date).split('.')[0], "%Y-%m-%d %H:%M:%S")
            elif '小时' in str(date_ori):
                num = int(date_ori[:-3])
                date = now_time - datetime.timedelta(hours=num)
                date = datetime.datetime.strptime(str(date).split('.')[0], "%Y-%m-%d %H:%M:%S")
            else:
                #时间在当前时间一天前    05/05 10:55    2023/12/21
                if len(date_ori.split()) == 2:
                    #当年
                    date_ori = '2024-' + date_ori.replace('/','-') + ':00'
                else:
                    #前一年
                    date_ori = date_ori.replace('/','-') + ' 00:00:00'
                date = datetime.datetime.strptime(str(date_ori).split('.')[0], "%Y-%m-%d %H:%M:%S")
        print('时间:\t', date)

        # 热度、热词, 点赞，评论
        redu, reci, dianzan, pinglun = '', '', '', ''

        yuedu = soup.find('div', {'class': 'hot-num'}).get_text()
        html = soup.find('div', {'class': 'article-content'})
       
        # text_maker = HTML2Text()
        # text_maker.body_width = 0
        # text_maker.ignore_links = True
        # text_maker.ignore_tables = True
        # md_text = text_maker.handle(str(html))
    
        start_words = []
        stop_words = []
        clean_md, clean_text, clean_doc = clean_html(self.args, i, html, start_words=start_words, stop_words=stop_words)

        return clean_md, clean_text, clean_doc, redu, reci, title, date, url, dianzan, pinglun, yuedu
    
    def run(self):
        #关键词集成电路，半导体，芯片
        urls = ['https://www.eefocus.com/article/']
        idd = 1
        try:
            for url in urls:
                i = 0
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
                    news_list = soup.find('div',{'class','information-list'}).find_all(name='li', attrs={'class': 'section-item'})
                    
                    for new in news_list:
                        try:
                            #查看当前新闻时间
                            date_ori = new.find('div',{'class','update-time'}).get_text()    #分钟前，小时前
                            #转化时间
                            now_time = datetime.datetime.now()
                            if '分钟' in str(date_ori):
                                # print(date_ori)
                                # print(date_ori[:-3])
                                num = int(date_ori[:-3])
                                date = now_time - datetime.timedelta(minutes=num)
                                date = datetime.datetime.strptime(str(date).split('.')[0], "%Y-%m-%d %H:%M:%S")
                            elif '小时' in str(date_ori):
                                num = int(date_ori[:-3])
                                date = now_time - datetime.timedelta(hours=num)
                                date = datetime.datetime.strptime(str(date).split('.')[0], "%Y-%m-%d %H:%M:%S")
                            else:
                                #时间在当前时间一天前    05/05 10:55    2023/12/21
                                if len(date_ori.split()) == 2:
                                    #当年
                                    date_ori = '2024-' + date_ori.replace('/','-') + ':00'
                                else:
                                    #前一年
                                    date_ori = date_ori.replace('/','-') + ' 00:00:00'
                                date = datetime.datetime.strptime(str(date_ori).split('.')[0], "%Y-%m-%d %H:%M:%S")

                            if self.args.start <= date <= self.args.end:
                                # 时间符合要求，开始爬取
                                detail_url = new.find('a')['href']
                                print('链接:\t', detail_url)
                                try:
                                    clean_md, clean_text, clean_doc, redu, reci, title, date, url, dianzan, \
                                        pinglun, yuedu = self.html2res(detail_url, date, str(idd))
                                    if self.args.keyword == '' or self.args.keyword in clean_text:
                                        if re.search('芯片|半导体|继承电路', clean_text):
                                            save_file(self.args, idd, clean_md, clean_text, clean_doc, redu, reci, title, date, url, dianzan, pinglun, yuedu)
                                            idd += 1
                                        else:
                                            print('该文章不属于集成电路领域：跳过！')
                                    else:
                                        print('该文章不包含关键词：{}！跳过！'.format(self.args.keyword))
                                            
                                except Exception as e:
                                    print(e)
                                    print(detail_url + '  download failure !!!')
                                    continue
                            elif date > self.args.end:
                                print('当前资讯比查找范围最新日期还要新，继续查找')
                                continue
                            else:
                                print('当前资讯过早，结束查找！')
                                flag = True
                                break           
                        except Exception as e:
                            print(e)
                            print('当前新闻html解析出错，下一条')
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

