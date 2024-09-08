import shutil
from fake_useragent import UserAgent
from source.utils import *

class Spider(object):
    
    def __init__(self,args):
        
        self.ua = UserAgent()
        self.PAGE_NUM = 2
        self.name = 'gjnyw'
        self.driver_normal = True

        self.args = args
        self.args.name = self.name
        self.args.industry_name = self.args.industry
        self.args.industry_type = allinfo.get(self.args.industry_name, ['',''])[1]
        self.args.industry_ID = allinfo.get(self.args.industry_name, ['',''])[0]
        self.args.dom_or_int = 'DOM'
        self.args.source_name = '国家能源网'
        self.args.fuzeren = '' 

        try:
            self.args.start = datetime.datetime.strptime(self.args.start, "%Y-%m-%d %H:%M:%S")
            self.args.end = datetime.datetime.strptime(self.args.end, "%Y-%m-%d %H:%M:%S")
        except:
            self.args.start = ''
            self.args.end = ''

    
    #将文章链接保存为md
    def html2res(self, url, date, i=1):
        response = requests.get(url, headers={'headers':self.ua.random}, verify=False)
        # print(response.encoding)   #ISO-8859-1
        # response.encoding('utf-8')
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.find('div', {'class': 'content fix'}).find('h1', {'id': 'title'}).get_text().strip()
        title = rep_comma(title)
        print('题目:\t', title)

        print('时间:\t', date)

        # 热度、热词, 点赞，评论
        redu, reci, dianzan, pinglun, yuedu = '', '', '', '', ''

        html = soup.find('div', {'class': 'content fix'}).find('div', {'class': 'fix'}).find('div', {'class': 'rightDetail fr'}).find('div', {'id': 'content'})
        # print(article)
       
        start_words = []
        stop_words = []
        clean_md, clean_text, clean_doc = clean_html(self.args, i, html, start_words=start_words, stop_words=stop_words)

        return clean_md, clean_text, clean_doc, redu, reci, title, date, url, dianzan, pinglun, yuedu
    

    def run(self):        
        idd = 1
        try:
            i = 1
            flag = False
            while i < self.PAGE_NUM:
                if flag:
                    break
                # 随机暂停几秒，避免过快的请求导致过快的被查到
                time.sleep(random.randint(1, 5))
                url = 'https://www.in-en.com/keylist.php?q=%E6%B0%A2%E7%87%83%E6%96%99%E7%94%B5%E6%B1%A0%E5%8F%91%E5%8A%A8%E6%9C%BA%E7%B3%BB%E7%BB%9F'
                resp = requests.get(url, headers = {'headers': self.ua.random})  

                #获取近一天内文章网址
                soup = BeautifulSoup(resp.content, 'lxml')
                newsList = soup.find('ul', {'class': 'infoLists'}).find_all('li')
                
                for news in newsList:
                    print(news)
                    if flag:
                        break
                    # 获取符合时间要求的链接地址 ：
                    try:
                        content_url = news.find('div', {'class': 'listTxts'}).find('h5').find('a')['href']
                    except:
                        try:
                            content_url = news.find('div', {'class': 'listTxts_pic'}).find('h5').find('a')['href']
                        except Exception as e:
                            print('链接无法读取')
                            print('单链接爬取失败', content_url)
                            continue
                    print('链接:\t', content_url)

                    time.sleep(random.randint(2, 3))

                    ori_new_time = news.find('div', {'class': 'prompts'}).find('i').get_text().strip()
                    print(ori_new_time)

                    
                    date = datetime.datetime.strptime(str(ori_new_time) + " 09:00:00", "%Y-%m-%d %H:%M:%S")
                    #self.args.start <= 
                    if self.args.start <= date <= self.args.end:  #时间在爬取范围内，进行内容提取
                        print('资讯时间符合要求，开始处理文本、图片、markdown...')
                        try:
                            clean_md, clean_text, clean_doc, redu, reci, title, date, url, dianzan, \
                                        pinglun, yuedu = self.html2res(content_url, date, str(idd))
                            if self.args.keyword == '' or self.args.keyword in clean_text:

                                save_file(self.args, idd, clean_md, clean_text, clean_doc, redu, reci, title, date, url, dianzan, pinglun, yuedu)

                                idd += 1
                            else:
                                print('该文章不包含关键词：{}！跳过！'.format(self.args.keyword))
                        except Exception as e:
                            print(e)
                            print('单链接爬取失败', content_url)
                            continue
                    elif date > self.args.end:
                        print('当前资讯比查找范围最新日期还要新，继续查找')
                        continue
                    else:
                        print('当前资讯过早，结束查找！')
                        flag = True
                        break    
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