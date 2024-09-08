#-*-coding:utf-8-*-
import json 
import yaml
import argparse

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="update info")
    parser.add_argument("--sources", type=str, 
                        default = "jiqizhixin liangziwei xinzhiyuan zhongguonengyuanbao zhongguobaowu shengwugu gaofenzikexueqianyan MaterialsViews huagongxinxingcailiao",
                        help="需要更新的公众号，以空格衔接")
    args, unknown = parser.parse_known_args()

    source_list = [source.strip("\n").strip() for source in args.sources.split(" ")]
    print("需要更新的公众号包含：{}\n\n".format(source_list))

    fixinfo = json.load(open("./utils/fixinfo.json","r",encoding="utf-8"))
    print(fixinfo)

    dyninfo = json.load(open("./utils/dyninfo.json","r",encoding="utf-8"))
    print(dyninfo)

    for source in source_list:
        s = fixinfo[source]["source"]
        fakeid = fixinfo[source]["fakeid"]
        cookie = dyninfo["cookie"]
        token = dyninfo["token"]
        user_agent = dyninfo["user_agent"]

        tmp_d = {
            "source":s,
            "fakeid":fakeid,
            "cookie":cookie,
            "token":token,
            "user_agent":user_agent,
            }
        
        with open("./utils/{}.yaml".format(source),"w",encoding="gbk") as f:
            yaml.dump(data = [tmp_d], stream=f, allow_unicode=True)