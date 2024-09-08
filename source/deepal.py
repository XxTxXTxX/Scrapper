import shutil
from fake_useragent import UserAgent
from source.utils import *
from selenium import webdriver
import json
import re

class Spider(object):
    
    def __init__(self,args):
        
        self.ua = UserAgent()
        self.PAGE_NUM = 2
        self.name = '深蓝汽车'
        self.driver_normal = True

        self.args = args
        self.args.name = self.name
        self.args.industry_name = self.args.industry
        self.args.industry_type = allinfo.get(self.args.industry_name, ['',''])[1]
        self.args.industry_ID = allinfo.get(self.args.industry_name, ['',''])[0]
        self.args.dom_or_int = 'DOM'
        self.args.source_name = '深蓝汽车'
        self.args.fuzeren = '' 

        try:
            self.args.start = datetime.datetime.strptime(self.args.start, "%Y-%m-%d %H:%M:%S")
            self.args.end = datetime.datetime.strptime(self.args.end, "%Y-%m-%d %H:%M:%S")
        except:
            self.args.start = ''
            self.args.end = ''


    #将文章链接保存为md
    def html2res(self, url, date, i=1):
        # headers = {
        #     'Accept': 'application/json, text/plain, */*',
        #     'Accept-Encoding': 'gzip, deflate, br, zstd',
        #     'Apptype': 'android',
        #     'Connection': 'keep-alive',
        #     'Content-Length': '58',
        #     'Content-Type': 'application/json',
        #     'Referer': 'https://www.deepal.com.cn/',
        #     'Fingerprint': '0de01266461c0a2adc064261a617d9ac',
        #     'Origin': 'https://www.deepal.com.cn',
        #     'Host': 'app-api.deepal.com.cn',
        #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
        # }
        # response = requests.get(url, headers={'headers':self.ua.random}, verify=False)
        page_content = get_pages_content(url)
        print(page_content)

        soup = BeautifulSoup(page_content, 'html.parser')

        m = re.findall('<h1 class="title___2ZsF1">(.*?)</h1>', page_content)
        title = m[0]
        title = rep_comma(title)
        print('题目:\t', title)

        print('时间:\t', date)

        # 热度、热词, 点赞，评论
        redu, reci, dianzan, pinglun, yuedu = '', '', '', '', ''

        html = soup.find('div', {'class': 'innerbox___Q5zhh'}).find('div')
        # print(article)
       
        start_words = []
        stop_words = []
        clean_md, clean_text, clean_doc = clean_html_forDeepal(self.args, i, html, start_words=start_words, stop_words=stop_words)

        return clean_md, clean_text, clean_doc, redu, reci, title, date, url, dianzan, pinglun, yuedu

    def run(self):        
        idd = 1
        # session = requests.Session()
        # url = 'https://app-api.deepal.com.cn/appapi/v1/m_app/article/listWeb'
        # headers = {
        #     'Accept': 'application/json, text/plain, */*',
        #     'Accept-Encoding': 'gzip, deflate, br, zstd',
        #     'Apptype': 'android',
        #     'Connection': 'keep-alive',
        #     'Content-Length': '58',
        #     'Content-Type': 'application/json',
        #     'Referer': 'https://www.deepal.com.cn/',
        #     'Fingerprint': '0de01266461c0a2adc064261a617d9ac',
        #     'Origin': 'https://www.deepal.com.cn',
        #     'Host': 'app-api.deepal.com.cn',
        #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        #     }
        
        # data = {
        #     'categoryName': '官网-新闻中心',
        #     'page': '1',
        #     'size': '999'
        # }

        try:
            flag = False
            while not flag:
                if flag:
                    break

                page_content = get_pages_content('https://www.deepal.com.cn/news')
                href_soup = BeautifulSoup(page_content, 'lxml').find('div', {'class': 'listbox___1Qk_e'}).find_all('a')
                # 随机暂停几秒，避免过快的请求导致过快的被查到
                # time.sleep(random.randint(1, 5))

                counter = 0
                # 网页里面每个链接会重复两次（标题带一个链接，图片还带一个链接，所以这里加一个
                # counter，每次counter到1就重置跳过
                for news in href_soup:
                    if counter == 1:
                        counter = 0
                        # 跳过重复的链接
                        continue
                    counter += 1
                    if flag:
                        break
                    # 获取符合时间要求的链接地址 ：
                    news = re.findall('<a href="(.*?)"', str(news))
                    news = news[0]
                    print('链接:\t', news)
                    # officialUrl = 'https://app-api.deepal.com.cn/appapi/v1/m_app/article/'
                    officialUrl = 'https://www.deepal.com.cn'
                    content_url = officialUrl + news
                    time.sleep(random.randint(2, 3))

                    page_detail = get_pages_content(content_url)
                    date_pattern = r'(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})'
                    match = re.search(date_pattern, page_detail)
                    ori_new_time = match.group()
                    print(ori_new_time)

                    
                    date = datetime.datetime.strptime(str(ori_new_time), "%Y-%m-%d %H:%M:%S")
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
        except Exception as e:
            print('整体网页爬取异常：%s' % e)
            print(traceback.format_exc())
            pass

        if os.path.exists("./tmp/img/"):
            shutil.rmtree("./tmp/img/")
        os.makedirs("./tmp/img/", exist_ok = True) 
        return
    


def clean_html_forDeepal(args, idd, html, start_words=[], stop_words=[], element=['p','h2','h3','section','div'], img_links = ['data-src', 'src', 'data-original']):
        '''
        idd：编号
        html：主要的html内容
        start_words：获取到该词在内容中就开始处理
        stop_words：获取到该词在内容中就停止处理
        element：处理html时需要处理的所有元素
        img_links：处理图片时需要处理的所有元素
        '''
        del_imgsrc = ['https://mmbiz.qpic.cn/mmbiz_png/JWVrUoA6c7jJcRQELLRjftia53rn3icpaCLcIEbsDicWeU7cNNquUa9LKmic0Q1Kf6avCic5CRDImyj8C230H6Lb2AQ/640?wx_fmt=png',
                    'https://mmbiz.qpic.cn/mmbiz_png/JWVrUoA6c7gJJia5xWW774Yib26tmR3yMgHzNW2oAsP20CJe7EEWnXIWeBxsrpufUicc5H2QHFZ2ojjRIlrNzicrYA/640?wx_fmt=png']
        os.makedirs("./output/{}/{}/doc/{}/".format(args.day, args.industry, args.name), exist_ok = True)
        os.makedirs("./output/{}/{}/mdFiles/{}/".format(args.day, args.industry, args.name), exist_ok = True)
        os.makedirs("./output/{}/{}/text/{}/".format(args.day, args.industry, args.name), exist_ok = True)
        os.makedirs("./output/{}/{}/thumbFiles/{}/".format(args.day, args.industry, args.name), exist_ok = True) 

        res = []
        onlytext_res = []
        n = 1
        output_doc = Document() 

        # 设置默认字体、字号和中文字体
        font_name = u'宋体'
        output_doc.styles['Normal'].font.size = Pt(12) # 设置默认字号为12号字体
        output_doc.styles['Normal'].font.name = font_name # 设置默认字体为楷体
        output_doc.styles['Normal']._element.rPr.rFonts.set(qn('w:eastAsia'), font_name) # 设置中文字体为宋体

        paragraph = output_doc.add_paragraph()

        flag = False
        startflag = False
        content_set = set()
        for div in html:
            if flag:
                break
            if 'video' in str(div) or '.gif' in str(div):
                continue
            try: 
                images = div.find_all('img')
                for src in images:
                    print(src.get('src'))
                    imgsrc = src.get('src')
                    pre_img_type = imgsrc.split('.')[-1]
                    if imgsrc == '' or imgsrc in content_set or pre_img_type in ['gif']:
                        print('获取不到图片，或图片格式不在处理范围！')
                        continue
                    # 如果图片以webp结尾，则将后缀去掉
                    if imgsrc.endswith('.webp'):
                        imgsrc = imgsrc.split('.webp')[0]
                    content_set.add(imgsrc)

                    print('下载第{}张图片:{}'.format(n, imgsrc))
                    img_type = pre_img_type if pre_img_type != '' else 'png'
                    file_path = './tmp/img/{}_pre_{}.{}.{}'.format(args.name,idd,n,img_type)
                    resize_file_path = './tmp/img/{}_{}.{}.{}'.format(args.name,idd,n,img_type)


                    download(file_path, imgsrc)
                    resize_image_1000(file_path, resize_file_path)
                    resize_base64_str = image_to_base64(resize_file_path)
                    imagetext = '![image](data:image/{};base64,{})'
                    image_base64text = imagetext.format(resize_file_path.split('.')[-1],resize_base64_str)

                    res.append(image_base64text)
                    output_doc.add_picture(resize_file_path)
                    paragraph = output_doc.add_paragraph()

                    # 把第一张存为缩略图
                    if n == 1:
                        image_path = file_path
                        if args.thub_type == 'txt':
                            resize_image_path = './tmp/img/{}_{}.{}'.format(args.name,idd,img_type)
                            result_path = './output/{}/{}/thumbFiles/{}/{}.txt'.format(args.day,
                                                                                    args.industry,
                                                                                    args.name,idd)
                            thumbnail(image_path, resize_image_path, result_path)
                        else:
                            resize_image_path = './output/{}/{}/thumbFiles/{}/{}.{}'.format(args.day,
                                                                                            args.industry,
                                                                                            args.name,idd,img_type)
                            result_path = resize_image_path = './tmp/img/{}_{}.txt'.format(args.name,idd)
                            thumbnail(image_path, resize_image_path, result_path)
                    n += 1
            except Exception as e:
                print('处理图片出现错误：{}'.format(e))
                pass
            #　处理文字内容
            try:
                if ('<style>' in str(div)):
                    continue
                content = div.get_text().strip('\n').strip()
                content = replace_symbol(content)

                # 如遇网址则跳过，可注释
                httpreg = '(http[s]?://[0-9a-zA-Z_\-=?,/\.:~%&]*)'
                if re.compile(httpreg).search(content) is not None:
                    continue

                if content in content_set:
                    continue
                content_set.add(content)

                if len(start_words) == 0:
                    startflag = True
                else:
                    for start_word in start_words:
                        if start_word in content:
                            startflag = True

                if startflag:
                    for stop_word in stop_words:
                        if stop_word in content:
                            flag = True
                            break
                    
                    if flag:
                        break
                    onlytext_res.append(content)
                    if str(div).startswith('<h2') or str(div).startswith('<h3'):
                        res.append('## <font color="#00e4ff">**{}**</font>'.format(content))

                        r = paragraph.add_run(content)
                        r.font.name = font_name
                        r.bold = True

                        r = paragraph.add_run('\n\n\n')
                        r.font.name = font_name
                    else:
                        res.append(content)

                        r = paragraph.add_run(content+'\n\n\n')
                        r.font.name = font_name
            except Exception as e:
                print('处理文字出现错误：{}'.format(e))
                pass
        res_text = '\n\n'.join(res)
        onlytext_res_text = '\n\n'.join(onlytext_res)
        return res_text, onlytext_res_text, output_doc