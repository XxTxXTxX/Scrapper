import shutil
from fake_useragent import UserAgent
from source.utils import *
from selenium import webdriver
## 文章带图片，但是爬不出来，utils里面的reg可能需要改一下


class Spider(object):
    def __init__(self, args):
        self.ua = UserAgent()
        self.PAGE_NUM = 2
        self.name = '东风汽车'
        self.driver_normal = True

        self.args = args
        self.args.name = self.name
        self.args.industry_name = self.args.industry
        self.args.industry_type = allinfo.get(self.args.industry_name, ['', ''])[1]
        self.args.industry_ID = allinfo.get(self.args.industry_name, ['', ''])[0]
        self.args.dom_or_int = 'DOM'
        self.args.source_name = '东风汽车'
        self.args.fuzeren = ''

        try:
            self.args.start = datetime.datetime.strptime(self.args.start, "%Y-%m-%d %H:%M:%S")
            self.args.end = datetime.datetime.strptime(self.args.end, "%Y-%m-%d %H:%M:%S")
        except:
            self.args.start = ''
            self.args.end = ''
        
# 文章链接保存为md
    def html2res(self, url, date='', i=1):
        response = requests.get(url, headers = {'headers': self.ua.random}, verify = False)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.find('h3').get_text()
        title = rep_comma(title)
        print('标题: ', title)

        source = soup.find('em').get_text().replace(' ', '')[20:].replace('\n', '') # 固定的
        date = soup.find('em').get_text().replace(' ', '')[5:16].replace('\n', '') # 固定的，很奇特的存储手法
        date = datetime.datetime.strptime(str(date) + ' 09:00:00', "%Y-%m-%d %H:%M:%S")
        print('时间：', date)

        redu, reci, dianzan, pinglun, yuedu = '', '', '', '', ''

        html = soup.find('div', {'class': 'infocontent_text'})

        start_words = []
        stop_words = []
        clean_md, clean_text, clean_doc = clean_html(self.args, i, html, start_words=start_words, stop_words=stop_words)

        return clean_md, clean_text, clean_doc, redu, reci, title, date, url, dianzan, pinglun, yuedu


    def run(self):
        requestUrl = 'https://www.dfmc.com.cn/news/qiyexinwen.json'
        # 动态网页，需要去到get的网站发送请求拿数据
        dynamicHeader = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            'Host': 'www.dfmc.com.cn',
            'Cookie': 'Hm_lvt_0ebb7d60e0f98e845e7f99452a6c24f7=1717640365; Hm_lpvt_0ebb7d60e0f98e845e7f99452a6c24f7=1717642779'
        }

        try:
            idd = 1
            flag = False # 检测内容是否为太早的内容
           
            while not flag: # 动态网站么有page，直接通过发布时间来判断继续扫描或者停止就好
                # 随机暂停几秒，避免过快的请求导致被检测到

                time.sleep(random.randint(1, 5))

                resp = requests.get(requestUrl, headers = dynamicHeader)
                newsJson = json.loads(resp.text)
                # 拿到所有的数据，网页在加载的同时会直接加载出来500条，从前面慢慢找就行
                newsList = newsJson['list']
                for news in newsList:
                    
                    # 拿到日期，这个网站没有发布时间，只有发布年月日，并且是用string的方式直接写上去的
                    pubDate = news.get('pubyear') + '-' + news.get('pubmonth') + '-' + news.get('pubday') + ' 09:00:00'
                    pubDate = datetime.datetime.strptime(pubDate, "%Y-%m-%d %H:%M:%S")
                    print('发布日期: ', pubDate)

                    # 拿到链接地址
                    ref = news.get('link')
                    print('链接: \t', ref)

                    time.sleep(random.randint(2, 3))
                    content_Url = 'https://www.dfmc.com.cn/' + ref # 固定地址

                    date = datetime.datetime.strptime(str(pubDate), "%Y-%m-%d %H:%M:%S")
                    if self.args.start <= date <= self.args.end:  #时间在爬取范围内，进行内容提取
                        print('资讯时间符合要求，开始处理文本、图片、markdown...')
                        try:
                            clean_md, clean_text, clean_doc, redu, reci, title, date, url, dianzan, \
                                        pinglun, yuedu = self.html2res(content_Url, date, str(idd))
                            if self.args.keyword == '' or self.args.keyword in clean_text:

                                save_file(self.args, idd, clean_md, clean_text, clean_doc, redu, reci, title, date, url, dianzan, pinglun, yuedu)

                                idd += 1
                            else:
                                print('该文章不包含关键词：{}！跳过！'.format(self.args.keyword))
                        except Exception as e:
                            print(e)
                            print('单链接爬取失败', content_Url)
                            continue
                    elif date > self.args.end:
                        print('当前资讯比查找范围最新日期还要新，继续查找')
                        continue
                    else:
                        print('当前资讯过早，结束查找！')
                        flag = True
                        break        
                    print('===================\n')

        except Exception as e:
            print('整体网页爬取异常：%s' % e)
            print(traceback.format_exc())
            pass
        
        if os.path.exists("./tmp/img/"):
            shutil.rmtree("./tmp/img/")
        os.makedirs("./tmp/img/", exist_ok = True) 
        return
