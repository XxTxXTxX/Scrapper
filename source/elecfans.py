#!encoding=utf-8
import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from html2text import HTML2Text
from PIL import Image
import datetime
import random
import shutil
import traceback
from source.utils import *
import datetime
from fake_useragent import UserAgent
from docx import Document


class Spider(object):
    
    def __init__(self,args):
        
        self.ua = UserAgent()
        self.PAGE_NUM = 2
        self.name = 'elecfans'
        self.driver_normal = True

        self.args = args
        self.args.name = self.name
        self.args.industry_name = self.args.industry
        self.args.industry_type = allinfo.get(self.args.industry_name, ['',''])[1]
        self.args.industry_ID = allinfo.get(self.args.industry_name, ['',''])[0]
        self.args.dom_or_int = 'DOM'
        self.args.source_name = '电子发烧友'
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
        # print(response.encoding)   #ISO-8859-1
        # response.encoding('utf-8')
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.find('h1', {'class': 'article-title'}).get_text().strip()
        title = rep_comma(title)
        print('题目:\t', title)

        if date != '':
            date = date 
        else:
            date = soup.find('span', {'class': 'time'}).get_text().strip()
            date = datetime.datetime.strptime(str(date), "%Y-%m-%d %H:%M:%S")
        print('时间:\t', date)

        # 热度、热词, 点赞，评论
        redu, reci, dianzan, pinglun, yuedu = '', '', '', '', ''

        html = soup.find('div', {'class': 'simditor-body clearfix'})
        # print(article)
       
        start_words = []
        stop_words = []
        clean_md, clean_text, clean_doc = clean_html(self.args, i, html, start_words=start_words, stop_words=stop_words)

        return clean_md, clean_text, clean_doc, redu, reci, title, date, url, dianzan, pinglun, yuedu
        


    def run(self):
        mainUrl = 'https://www.elecfans.com/news/hangye/Article_090_' #这个是新闻主页，一页有很多个新闻，页数直接加到page后面就行
        mainUrl_suffix = '.html'

        
        idd = 1
        try:
            i = 1
            flag = False
            while i < self.PAGE_NUM:
                if flag:
                    break
                # 随机暂停几秒，避免过快的请求导致过快的被查到

                counter = 0
                # 有的网站会穿插一些老文章在新文章中间，所以加一个variable counter
                # 去判断我们在这一页里一共连续读了几篇 老文章
                # 如果连续读了4篇以上那么后面的文章大概率都是老文章
                # 因为我们只检查发布时间，所以这个不会浪费太多时间


                time.sleep(random.randint(1, 5))

                url = mainUrl + str(i) + mainUrl_suffix
                resp = requests.get(url, headers = {'headers': self.ua.random})
                if resp.status_code == 403:
                    print("403 Forbidden!!!!!!!!!!!")
                if resp.status_code == 200:
                    print("success!!!!")     

                # resp.encoding('utf-8')
                # print('resp', resp.text)

                #获取近一天内文章网址
                soup = BeautifulSoup(resp.content, 'lxml')
                all_news_title = soup.find('div', {'class': 'main-wrap'}).find_all('h3', {'class': 'a-title'})

                # latestNews = all_news_box.find(attrs={'data-testid': 'tthumbnail'})
                # latestNews_href = latestNews.get('href')
                # print("Href for latest news = ", latestNews_href)

                for new in all_news_title:
                    print(new)
                    if flag:
                        break
                    # 获取符合时间要求的链接地址 ：
                    new_url = new.find('a')['href']
                    print('链接:\t', new_url)
                    time.sleep(random.randint(2, 3))
                    content_Url = new_url
                    new_c = requests.get(content_Url, headers={'headers':self.ua.random}, verify=False)
                    # new_c.encoding('utf-8')

                    # 这里可以拿到文章内容了
                    new_soup = BeautifulSoup(new_c.content, 'lxml')


                    ori_new_time = new_soup.find('span', {'class': 'time'}).get_text().strip()
                    print(ori_new_time)

                    
                    date = datetime.datetime.strptime(str(ori_new_time) + ":00", "%Y-%m-%d %H:%M:%S")
                    if self.args.start <= date <= self.args.end:  #时间在爬取范围内，进行内容提取
                        print('资讯时间符合要求，开始处理文本、图片、markdown...')
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
                        if (counter == 4):
                            print('当前资讯过早，结束查找！')
                            flag = True
                            break 
                        else:
                            counter += 1          
                    print('===================\n')
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