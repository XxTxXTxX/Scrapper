#-*-coding:utf-8-*-
import argparse
import os
import shutil
import pandas as pd
import time
import chardet
import datetime
from importlib import import_module

def get_encoding(file):
    with open(file,'rb') as f:
        tmp = chardet.detect(f.read())
        return tmp['encoding']


if __name__ == "__main__":

    allinfo = {
        '新能源汽车':['1766033643315834880','SEI'],
        '人工智能':['1766033379397664768','SEI'],
        '集成电路':['1766034156832903168','SEI'],
        '工业母机':['1766033463598276608','SEI'],
        '新能源':['1766033744289464320','SEI'],
        '新一代移动通信':['1766034093557596160','SEI'],
        '生物技术':['1766033589087674368','SEI'],
        '工业软件':['1766034205675507712','SEI'],
        '新材料':['1766033523736182784','SEI'],

        '未来能源':['1766037300157493248','FI'],
        '未来健康':['1766037619054665728','FI'],
        '未来信息':['1766034292099186688','FI'],
        '未来网络':['1766037094787706880','FI'],
        '未来空间':['1766037771639222272','FI'],
        '未来制造':['1766037449856417792','FI'],

        '商业航天':['1787741534431309824','OI'],
        '低空经济':['1787751043652476928','OI']
    }

    today = datetime.datetime.now().strftime('%Y-%m-%d')
    yesterday =  (datetime.datetime.now()-datetime.timedelta(days=1)).strftime('%Y-%m-%d')

    parser = argparse.ArgumentParser(description='spider')
    parser.add_argument('--start', type=str, default = yesterday +' 9:00:00', help='爬取起始时间')
    parser.add_argument('--end', type=str, default = today +' 9:00:00', help='爬取结束时间')
    parser.add_argument('--industry', type=str, 
                        # default = '人工智能', 
                        # default = '未来信息', 
                        # default = '新能源', 
                        # default = '新能源汽车', 
                        # default = '生物技术', 
                        # default = '新材料', 
                        default = '新一代移动通信', 
                        # default = '工业母机', 
                        # default = '工业软件', 
                        # default = '集成电路', 
                        help='所属产业，如:人工智能，新能源，新能源汽车，生物技术，新材料，新一代移动通信，工业母机，工业软件，集成电路')
    parser.add_argument('--thub_type', type=str, default = 'txt', help='缩略图')
    parser.add_argument('--keyword', type=str, default = '', help='文章所需关键词')
    parser.add_argument('--sources', type=str, 
        # default = 'wlxx_naoji1 wlxx_naoji2 wlxx_liangkewang wlxx_c114',
        # default = 'jiqizhixin liangziwei xinzhiyuan itzhijia zhanzhang xinhuawang', 
        # default = 'zhongguonengyuanbao nengyuanjie nengyuanxinwen',
        # default = 'autoce diyiec taimeiti autohome yiche ofweek',
        # default = 'shengwugu shengwutong',
        # default = 'xincailiao_ofweek chinasia csteelnews escn MaterialsViews gaofenzikexueqianyan huagongxinxingcailiao zhongguobaowu',
        # default = 'c114 wulian 199it',
        # default = 'thepaper dongfangcaifu souhu cnc jc35 158jixie',
        # default = 'caifu_ruanjian zhinengzhizao zhongguogongkong',
        # default = 'eleeng icspec qqbdtgc xinzhixun eefoucus jiweiwang elecfans',
        # default = 'zgyqgzh zgyq DongFeng deepal avatr changangzh shenlangzh avatrgzh huawei gjnyw evchanye chinaev hedianzhan',
        # default = 'yangguangwang',
        help='爬取的源，以空格衔接，如：jiqizhixin liangziwei xinzhiyuan itzhijia zhanzhang xinhuawang huaqiangzixun cww_net guandian zhitongcaijing caijingwang beebom ainews mit_news techcrunch')
    args, unknown = parser.parse_known_args()

    args.day = args.end.split(' ')[0].replace('-','')
    args.info_path = './output/{}/{}/origin_excelFile_新闻_{}.csv'.format(args.day, args.industry, args.day)
    
    source_list = [source.strip('\n').strip() for source in args.sources.split(' ')]
    print('爬取的源包含：{}\n\n'.format(source_list))
    allsources = [x.strip('.py') for x in os.listdir('./source/') if 'init' not in x]
    othersources = list(set(allsources).difference(set(source_list)))
    print('未爬取的源包含：{}\n\n'.format(othersources))


    # 删除文件夹
    for dirname in ['output']:
        if os.path.exists("./{}/{}/{}/".format(dirname, args.day, args.industry)):
            shutil.rmtree("./{}/{}/{}/".format(dirname, args.day, args.industry))
    if os.path.exists("./tmp/"):
        shutil.rmtree("./tmp/")


    all_start = time.time()

    os.makedirs("./log/{}/".format(args.day), exist_ok = True)
    with open('./log/{}/error_{}.log'.format(args.day, args.industry),'a+') as f:
            f.write('\n\n******爬取错误信息******\n{}\n'.format(datetime.datetime.now()))

    
    recommend_info = "./recommend/{}/{}/origin_excelFile_新闻_{}.csv".format(args.day, args.industry, args.day)
    if os.path.exists(recommend_info):
        try:
            df = pd.read_csv(recommend_info, encoding="utf-8")
        except:
            df = pd.read_csv(recommend_info, encoding="gbk")
        if len(df) > 0:
            total_index = list(df['序号'])[-1]+1
        else:
            total_index = 1
    else:
        total_index = 1

    error_num = 0

    for source in source_list:
        error_indexs = set()

        # 每爬一个源都重新创建文件夹
        for dirname in ['output','recommend']:
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
            # f.write("序号,产业名称,产业类型,产业ID,负责人,国内或国际,热度,热词,标题,新闻发布时间,来源,原文链接,点赞量,评论量,阅读量,hasimg\n")
            f.write("序号,产业名称,产业类型,产业ID,负责人,国内或国际,热度,热词,标题,新闻发布时间,来源,原文链接\n")

        try:

            start = time.time()

            args, unknown = parser.parse_known_args()
            args.day = args.end.split(' ')[0].replace('-','')
            args.info_path = './output/{}/{}/origin_excelFile_新闻_{}.csv'.format(args.day, args.industry, args.day)

            x = import_module('source.' + source)
            spider = x.Spider(args)

            print('******************************************')
            print('******************************************')
            print('开始爬取{}网页中...'.format(spider.args.name))
            print('******************************************')
            print('******************************************')

            spider.run()
        

            recommend_info = "./recommend/{}/{}/origin_excelFile_新闻_{}.csv".format(args.day, args.industry, args.day)
            if os.path.exists(recommend_info):
                try:
                    df = pd.read_csv(recommend_info, encoding="utf-8")
                except:
                    df = pd.read_csv(recommend_info, encoding="gbk")
            else:
                with open(recommend_info, "w", encoding='utf8') as f:
                    # f.write("序号,产业名称,产业类型,产业ID,负责人,国内或国际,热度,热词,标题,新闻发布时间,来源,原文链接,点赞量,评论量,阅读量,hasimg\n")
                    f.write("序号,产业名称,产业类型,产业ID,负责人,国内或国际,热度,热词,标题,新闻发布时间,来源,原文链接\n")
                try:
                    df = pd.read_csv(recommend_info, encoding="utf-8")
                except:
                    df = pd.read_csv(recommend_info, encoding="gbk")

            
            df_res = pd.read_csv("./output/{}/{}/origin_excelFile_新闻_{}.csv".format(args.day, args.industry, args.day), error_bad_lines=False)
            df_res = df_res[df_res['来源']==spider.name].reset_index(drop=True)
            
            if len(df_res) > 0:
                
                # 如果该网站爬取数量大于0，修改序号

                for index, id in enumerate(df_res['序号']):
                    
                    # 复制结果，更新序号
                    xuhao = df_res['序号'][index]
                    df_res.loc[index, '序号'] = total_index

                    for resdir in ['doc', 'mdFiles','text','thumbFiles']:  

                        if os.path.exists("./output/{}/{}/{}/{}/{}.txt".format(args.day, args.industry, resdir, spider.name, xuhao)):
                            try:
                                shutil.copyfile("./output/{}/{}/{}/{}/{}.txt".format(args.day, args.industry, resdir, spider.name, xuhao),
                                                "./recommend/{}/{}/{}/{}.txt".format(args.day, args.industry, resdir, total_index))
                            except:
                                print("./recommend/{}/{}/{}/{}.txt　复制失败！".format(args.day, args.industry, resdir, total_index))

                                pass
                        else:
                            print("./output/{}/{}/{}/{}/{}.txt　不存在，不进行复制".format(args.day, args.industry, resdir, spider.name, xuhao))
                    
                        if os.path.exists("./output/{}/{}/{}/{}/{}.docx".format(args.day, args.industry, resdir, spider.name, xuhao)):
                            try:
                                shutil.copyfile("./output/{}/{}/{}/{}/{}.docx".format(args.day, args.industry, resdir, spider.name, xuhao),
                                                "./recommend/{}/{}/{}/{}.docx".format(args.day, args.industry, resdir, total_index))
                            except:
                                print("./recommend/{}/{}/{}/{}.docx".format(args.day, args.industry, resdir, total_index))

                                pass
                        else:
                            print("./output/{}/{}/{}/{}/{}.docx".format(args.day, args.industry, resdir, spider.name, xuhao))
                    
                    # 校验结果，如果文件结果不存在则进行删除
                    for resdir in ['mdFiles','text']:  
                        if not os.path.exists("./recommend/{}/{}/{}/{}.txt".format(args.day, args.industry, resdir, total_index)):
                            error_indexs.add(total_index)
                            print("./recommend/{}/{}/{}/{}.txt 不存在该文件，去掉该新闻！".format(args.day, args.industry, resdir, total_index))
                    
                    total_index += 1

                # 剔除出现错误的新闻信息
                df_res = df_res[~(df_res['序号'].isin(error_indexs))].reset_index(drop=True)         

                df = pd.concat([df,df_res]).drop_duplicates(subset=['标题'], keep='first').reset_index(drop=True)
                try:
                    df.to_csv(recommend_info, encoding="utf-8", index=False)
                    print('全部抓取信息已保存至{}！'.format(recommend_info))
                except:
                    df.to_csv(recommend_info, encoding="gbk", index=False)
                    print('全部抓取信息已保存至{}！'.format(recommend_info))
            
            else:
                try:
                    df.to_csv(recommend_info, encoding="utf-8", index=False)
                    print('未爬取到数据，{}不进行更新！'.format(recommend_info))
                except:
                    df.to_csv(recommend_info, encoding="gbk", index=False)
                    print('未爬取到数据，{}不进行更新！'.format(recommend_info))
                    

            print('爬取{}耗时：{}'.format(spider.name, time.time()-all_start))

            # 每爬一个源都删除文件夹
            # for dirname in ['output']:
            #     if os.path.exists("./{}/{}/".format(dirname, args.day)):
            #         shutil.rmtree("./{}/{}/".format(dirname, args.day))
            if os.path.exists("./tmp/"):
                shutil.rmtree("./tmp/")

            if not spider.driver_normal:
                raise ValueError("无法用浏览器打开{}".format(source))

        except Exception as e:

            with open('./log/{}/error_{}.log'.format(args.day, args.industry),'a+') as f:
                error_num += 1
                f.write('{}\t{}\t{}\n'.format(args.industry, source, e))
            print('{}爬取网页出现错误：{}！跳过！'.format(source, e))

    print('爬取总耗时：{}'.format(time.time()-all_start))

    if error_num == 0:
        try:
            os.remove('./log/{}/error_{}.log'.format(args.day, args.industry))
        except:
            pass

    # 删除文件夹
    # for dirname in ['output']:
    #     if os.path.exists("./{}/{}/{}/".format(dirname, args.day, args.industry)):
    #         shutil.rmtree("./{}/{}/{}/".format(dirname, args.day, args.industry))
    if os.path.exists("./tmp/"):
        shutil.rmtree("./tmp/")
