#-*-coding:utf-8-*-
import argparse
import os
import shutil
import pandas as pd
import time
import chardet
import datetime
from importlib import import_module
from source.utils import *

def get_encoding(file):
    with open(file,'rb') as f:
        tmp = chardet.detect(f.read())
        return tmp['encoding']


if __name__ == "__main__":

    allinfo = {
        '新能源汽车':['1766033643315834880'],
        '人工智能':['1766033379397664768'],
        '集成电路':['1766034156832903168'],
        '工业母机':['1766033463598276608'],
        '新能源':['1766033744289464320'],
        '新一代移动通信':['1766034093557596160'],
        '生物技术':['1766033589087674368'],
        '工业软件':['1766034205675507712'],
        '新材料':['1766033523736182784']
    }
    
    parser = argparse.ArgumentParser(description='spider')
    parser.add_argument('--industry', type=str, 
                        default = '人工智能', 
                        help='所属产业，如:人工智能')
    parser.add_argument('--thub_type', type=str, default = 'txt', help='缩略图')
    parser.add_argument('--date', type=str, default = '2024-05-11 8:00:00', help='时间')
    parser.add_argument('--source', type=str, default = 'eefocus', help='所属源')
    parser.add_argument('--url', type=str, default = 'https://www.eefocus.com/article/1693358.html', help='需要爬取的网页')
    parser.add_argument('--idd', type=int, default = 1, help='编号')
    args, unknown = parser.parse_known_args()
    
    args.day = args.date.split(' ')[0].replace('-','')
    args.info_path = './output/{}/{}/{}新闻.csv'.format(args.day, args.industry, args.day)
    
    # 创建文件夹
    for dirname in ['output']:
        os.makedirs("./{}/".format(dirname), exist_ok = True) 
        os.makedirs("./{}/{}/".format(dirname, args.day), exist_ok = True) 
        os.makedirs("./{}/{}/{}/".format(dirname, args.day, args.industry), exist_ok = True) 
        
        os.makedirs("./{}/{}/{}/doc/".format(dirname, args.day, args.industry), exist_ok = True)
        os.makedirs("./{}/{}/{}/mdFiles/".format(dirname, args.day, args.industry), exist_ok = True)
        os.makedirs("./{}/{}/{}/text/".format(dirname, args.day, args.industry), exist_ok = True)
        os.makedirs("./{}/{}/{}/thumbFiles/".format(dirname, args.day, args.industry), exist_ok = True)
        
    os.makedirs("./tmp/", exist_ok = True) 
    os.makedirs("./tmp/img/", exist_ok = True)   
    
    # 初始化爬取信息
    with open(args.info_path, "w", encoding='utf8') as f:
        f.write("id,产业名称,产业类型,产业ID,负责人,国内或国际,热度,热词,标题,新闻发布时间,来源,原文链接,点赞量,评论量,阅读量,hasimg\n")
    
    start = time.time()
    
    x = import_module('source.' + args.source)
    spider = x.Spider(args)
    
    print('******************************************')
    print('******************************************')
    print('开始爬取{}网页中...'.format(spider.args.name))
    print('******************************************')
    print('******************************************')

    clean_md, clean_text, clean_doc, redu, reci, title, date, url, dianzan, pinglun, yuedu = spider.html2res(args.url, args.date, args.idd)
    save_file(args, args.idd, clean_md, clean_text, clean_doc, redu, reci, title, date, url, dianzan, pinglun, yuedu)
    
    if os.path.exists("./tmp/img/"):
        shutil.rmtree("./tmp/img/")
    os.makedirs("./tmp/img/", exist_ok = True)
    
    print('爬取{}网页耗时:{}'.format(args.url, time.time()-start))