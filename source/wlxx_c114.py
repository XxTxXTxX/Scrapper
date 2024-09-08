# -*- coding:utf-8 -*-
import os
import time
import requests
from bs4 import BeautifulSoup
# noinspection PyUnresolvedReferences
from urllib.parse import urlparse
from logger import logger
import re
from html2text import HTML2Text
from PIL import Image
from urllib import request
import base64
import traceback
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
from selenium import webdriver
from fake_useragent import UserAgent
import time
import datetime
import shutil
import os
import random
import copy
from source.utils import *
from docx import Document


class Spider(object):
    
    def __init__(self,args):
        
        self.ua = UserAgent()
        self.PAGE_NUM = 2
        self.name = 'c114'
        self.driver_normal = True
        self.args = args
        #self.args.start = datetime.datetime.strptime(self.args.start, "%Y-%m-%d %H:%M:%S")
        #self.args.end = datetime.datetime.strptime(self.args.end, "%Y-%m-%d %H:%M:%S")

        self.args.name = self.name
        self.args.industry_name = self.args.industry
        self.args.industry_type = 'SEI'
        self.args.industry_type = allinfo.get(self.args.industry_name, ['',''])[1]
        self.args.industry_ID = allinfo.get(self.args.industry_name, ['',''])[0]
        self.args.dom_or_int = 'DOM'
        self.args.source_name = 'c114'
        self.args.fuzeren = '' 
        
        try:
            self.args.start = datetime.datetime.strptime(self.args.start, "%Y-%m-%d %H:%M:%S")
            self.args.end = datetime.datetime.strptime(self.args.end, "%Y-%m-%d %H:%M:%S")
        except:
            self.args.start = ''
            self.args.end = ''

    
    def html2res(self, url, date='', i=1):
        '''抓取单个网页'''
        page = requests.get(url, headers={'headers':self.ua.random})
        page_content = page.content

        # 使用BeautifulSoup解析html
        soup1 = BeautifulSoup(page_content, 'lxml')

        title = soup1.find('h1').text
        title = rep_comma(title)
        print('题目:\t', title)
        
        if date != '':
            date = date
        else:
            date = soup1.find('div', {'class': 'r_time'}).text.strip().replace('/','-')+':00'
            date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        print('日期:\t', date)        

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
                
        news = soup1.find('div', {'class': 'text'})
          
        start_words = []
        stop_words = []
        clean_md, clean_text, clean_doc = clean_html(self.args, i, news, start_words=start_words, stop_words=stop_words)

        return clean_md, clean_text, clean_doc, redu, reci, title, date, url, dianzan, pinglun, yuedu
    
    
    def run(self):
        flag = False
        j = 1
        for k in range(1, self.PAGE_NUM):
            if flag:
                break
            try:
                # 待抓取的网页地址
                url = 'https://www.c114.com.cn/news/roll.asp'
                c = requests.get(url, headers={'headers':self.ua.random})
                # 使用BeautifulSoup解析html
                soup = BeautifulSoup(c.content, 'lxml')
                all_news = soup.find_all('div', attrs={'class':'new_list_c'})
                
                for hotNews in all_news:
                    if flag:
                        break
                    try:
                        detail_url = hotNews.find('h6').find('a')['href']
                    
                        print('序号:\t', j)
                        print('链接:\t', detail_url)
                            
                        page = requests.get(detail_url, headers={'headers':self.ua.random})
                        page_content = page.content
                        soup1 = BeautifulSoup(page_content, 'lxml')
                            
                        # 必须从单个新闻页面获取日期
                        date = soup1.find('div', {'class': 'r_time'}).text.strip().replace('/','-')+':00'
                        date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                        
                        if self.args.start < date < self.args.end:
                                
                            clean_md, clean_text, clean_doc, redu, reci, title, date, url, dianzan, \
                                pinglun, yuedu = self.html2res(detail_url, date, j)
                                
                            if self.args.keyword == '' or self.args.keyword in clean_text:
                                if re.search('量子|脑机|类脑', clean_text):
                                    
                                    save_file(self.args, j, clean_md, clean_text, clean_doc, redu, reci, title, date, url, dianzan, pinglun, yuedu)

                                    j += 1
                                else:
                                    print('该文章不属于未来信息领域：跳过！')
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
        time.sleep(1)
        
        if os.path.exists("./tmp/img/"):
            shutil.rmtree("./tmp/img/")
        os.makedirs("./tmp/img/", exist_ok = True) 
        return
    
   