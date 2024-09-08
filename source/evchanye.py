from fake_useragent import UserAgent
import shutil
from source.utils import *

class Spider(object):
    
    def __init__(self,args):
        
        self.ua = UserAgent()
        self.PAGE_NUM = 2
        self.name = '新能源汽车'
        self.driver_normal = True

        self.args = args
        self.args.name = self.name
        self.args.industry_name = self.args.industry
        self.args.industry_type = allinfo.get(self.args.industry_name, ['',''])[1]
        self.args.industry_ID = allinfo.get(self.args.industry_name, ['',''])[0]
        self.args.dom_or_int = 'DOM'
        self.args.source_name = '新能源汽车'
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
        title = soup.find('h1', {'class': 'article-content-title'}).get_text().strip()
        title = rep_comma(title)
        print('题目:\t', title)

        print('时间:\t', date)

        # 热度、热词, 点赞，评论
        redu, reci, dianzan, pinglun, yuedu = '', '', '', '', ''

        html = soup.find('div', {'class': 'article-detail-inner'})
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
                url = 'https://www.evchanye.com/news/{}.shtml'.format(i)
                resp = requests.get(url, headers = {'headers': self.ua.random})  

                #获取近一天内文章网址
                soup = BeautifulSoup(resp.content, 'lxml')
                newsList = soup.find('div', {'class': 'article-list article-picture-list'}).find_all('li')

                # latestNews = all_news_box.find(attrs={'data-testid': 'tthumbnail'})
                # latestNews_href = latestNews.get('href')
                # print("Href for latest news = ", latestNews_href)

                for new in newsList:
                    print(new)
                    if flag:
                        break
                    # 获取符合时间要求的链接地址 ：
                    content_url = new.find('a')['href']
                    print('链接:\t', content_url)
                    time.sleep(random.randint(2, 3))
                    new_c = requests.get(content_url, headers={'headers':self.ua.random}, verify=False)
                    # new_c.encoding('utf-8')

                    # 这里可以拿到文章内容了
                    new_soup = BeautifulSoup(new_c.content, 'lxml')


                    ori_new_time = new_soup.find('span', {'class': 'date'}).get_text().strip() + ':00'
                    print(ori_new_time)

                    
                    date = datetime.datetime.strptime(str(ori_new_time), "%Y-%m-%d %H:%M:%S")
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