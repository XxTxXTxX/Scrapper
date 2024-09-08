#-*-coding:utf-8-*-
import argparse
import pandas as pd
import os
import datetime

if __name__ == "__main__":

    today = datetime.datetime.now().strftime('%Y-%m-%d')
    yesterday =  (datetime.datetime.now()-datetime.timedelta(days=1)).strftime('%Y-%m-%d')

    parser = argparse.ArgumentParser(description='totalinfo')
    parser.add_argument('--start', type=str, default = yesterday +' 10:00:00', help='爬取起始时间')
    parser.add_argument('--end', type=str, default = today +' 10:00:00', help='爬取结束时间')
    parser.add_argument('--industrys', type=str, 
                        default = '人工智能 新能源 新能源汽车 生物技术 新材料 新一代移动通信 工业母机 工业软件 集成电路', 
                        help='所属产业，如:人工智能')
    args, unknown = parser.parse_known_args()

    args.day = args.end.split(' ')[0].replace('-','')

    industry_list = [source.strip('\n').strip() for source in args.industrys.split(' ')]

    print('统计{}爬取数目：'.format(args.day))
    for industry in industry_list:
        try:

            recommend_info = "./recommend/{}/{}/origin_excelFile_新闻_{}.csv".format(args.day, industry, args.day)
            try:
                df = pd.read_csv(recommend_info, encoding="utf-8")
            except:
                df = pd.read_csv(recommend_info, encoding="gbk")
        except:
            df = pd.DataFrame([])

        print('{}：\t{}条'.format(industry, len(df)))