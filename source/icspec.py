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
import datetime
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
        self.name = 'icspec'
        self.driver_normal = True

        self.args = args
        self.args.name = self.name
        self.args.industry_name = self.args.industry
        self.args.industry_type = allinfo.get(self.args.industry_name, ['',''])[1]
        self.args.industry_ID = allinfo.get(self.args.industry_name, ['',''])[0]
        self.args.dom_or_int = 'DOM'
        self.args.source_name = 'icspec'
        self.args.fuzeren = '' 

        try:
            self.args.start = datetime.datetime.strptime(self.args.start, "%Y-%m-%d %H:%M:%S")
            self.args.end = datetime.datetime.strptime(self.args.end, "%Y-%m-%d %H:%M:%S")
        except:
            self.args.start = ''
            self.args.end = ''
        

    
    #将文章链接保存为md
    def html2res(self, url, date='', i=1):
        del_list = []
        response = requests.get(url, headers={'headers':self.ua.random}, verify=False)
        # 解析 HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        # 获取文章正文
        title = soup.find('div', {'class': 'art_title'}).get_text()
        title = rep_comma(title)
        print('题目:\t', title)

        date_ori = soup.find('span', {'class': 'mar-r10'}).get_text().strip()
        #转化时间
        now_time = datetime.datetime.now()
        if '分钟' in str(date_ori):
            num = int(date_ori[:-3].strip())
            date = now_time - datetime.timedelta(minutes=num)
            date = str(date).split('.')[0]
            date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S") 
        elif '小时' in str(date_ori):
            num = int(date_ori[:-3].strip())
            date = now_time - datetime.timedelta(hours=num)
            date = str(date).split('.')[0]
            date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S") 
        else:
            date = now_time

        # 热度、热词, 点赞，评论
        redu, reci, dianzan, pinglun, yuedu = '', '', '', '', ''
        dianzan = soup.find('div', {'class': 'tc_c mar-t40'}).get_text()
        article = soup.find('div', {'class': 'art_content'})
       
        text_maker = HTML2Text()
        text_maker.body_width = 0
        text_maker.ignore_links = True
        text_maker.ignore_tables = True
        md_text = text_maker.handle(str(article))

        start_words = []
        stop_words = []
        clean_md, clean_text, clean_doc = clean_markdown(self.args, i, md_text, start_words=start_words, stop_words=stop_words)

        return clean_md, clean_text, clean_doc, redu, reci, title, date, url, dianzan, pinglun, yuedu
    
    def run(self):
        i = 0
        idd = 1
        try:
            flag = False
            while i<self.PAGE_NUM:
                if flag:
                    break
                url = 'https://www.icspec.com/news/index/{}'.format(i + 1)
                # 随机暂停几秒，避免过快的请求导致过快的被查到
                time.sleep(random.randint(1, 5))
                resp = requests.get(url, headers={'headers':self.ua.random}, verify=False)
                # print('resp', resp.text)

                #获取近一天内文章网址
                soup = BeautifulSoup(resp.content, 'html.parser')
                # all_news_box = soup.find('div', {'class': 'el-col el-col-17'})
                all_news_box = soup.select('.news_info')
                # print(all_news_box)
                for new_info in all_news_box:
                    detail_url = ''
                    try:
                        # 获取符合时间要求，来源要求（仅ictimes）的链接地址，阅读量：
                        date_ori = new_info.find('span', {'class': 'mar-r10'}).get_text().strip()
                        #转化时间
                        now_time = datetime.datetime.now()
                        if '分钟' in str(date_ori):
                            # print(date_ori)
                            # print(date_ori[:-3])
                            num = int(date_ori[:-3].strip())
                            date = now_time - datetime.timedelta(minutes=num)
                            date = datetime.datetime.strptime(str(date).split('.')[0], "%Y-%m-%d %H:%M:%S")
                        elif '小时' in str(date_ori):
                            num = int(date_ori[:-3].strip())
                            date = now_time - datetime.timedelta(hours=num)
                            date = datetime.datetime.strptime(str(date).split('.')[0], "%Y-%m-%d %H:%M:%S")
                        else:
                            continue

                        if self.args.start <= date <= self.args.end:
                            # 时间符合要求，开始爬取
                            detail_url = new_info.find('a')['href']
                            detail_url = 'https://www.icspec.com' + detail_url
                            print('链接:\t', detail_url)
                            #https://www.icspec.com      /news/article-details/2303943
                            # print(detail_url)
                            #获取阅读量
                            # yuedu = [r.get_text() for r in new_info.find_all('span')][-1].strip()
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
