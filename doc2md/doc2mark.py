import base64
import markdown
import os
import re
import io
import shutil
import pandas as pd
import argparse
import numpy as np

from PIL import Image
from docx import Document
from os.path import basename



# 修改二进制流图像，300*
def resize_image(rb, size):
    imagePixmap = rb.size
    n_img = rb.resize(size, Image.ANTIALIAS)
    return n_img
        
# 修改二进制流图像，1000*
def resize_image_rb1000(rb):
    imagePixmap = rb.size
    width = imagePixmap[0]
    height = imagePixmap[1]
    scale = 1000/width
    n_img = rb.resize((int(width*scale), int(height*scale)), Image.ANTIALIAS)
    return n_img

# 保存图片
def save_image(img, save_path):
    img.save(save_path)
    return

# 图片转base64
def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()
        base64_data = base64.b64encode(image_data)
        base64_string = base64_data.decode("utf-8")
        return base64_string
    
# 保存图片base64文本    
def save_base64(image_path, base64path):
    image_base64 = image_to_base64(image_path)
    text = '''data:image/{};base64,{}'''.format(image_path.split('.')[-1],image_base64)
    with open(base64path,'w') as f:
        f.write(text)
    
        
# 输入doc路径，完成所有doc markdown化
def docs2md(args, num):
    doc_path = "./{}/doc/".format(args.date)
    files = os.listdir(doc_path)
    files = [file for file in files if file == '{}.docx'.format(num)]
    if len(files) > 0:
        file = files[0]
        file_path = os.path.join(doc_path, file)
        outfile = os.path.join('./{}/mdFiles/'.format(args.date), file.split('.')[0]+'.txt')
        doc2markdown(args, num, file_path, outfile)
        print(file + ' done')
        print('####################################')
    else:
        print('找不到{}日名为{}的文档！'.format(args.date,num))
        
# 将docx格式转化为markdown，包括图片，图片修改大小，粗体标识
def doc2markdown(args, num, docx, outfile):
    doc = Document(docx)

    # 读取每个段落的文本内容
    text = []
    save_text = []
    
    flag = 0
    pattern = re.compile('rId\d+')
    img_n = 1
    for paragraph in doc.paragraphs:
        run_line = ''
        for run in paragraph.runs:
            # print('run.text',run.text)
            if run.text != '':
                if run.bold:
                    line = '## <font color="#00e4ff">**{}**</font>'.format(run.text)
                    text.append(line)
                    continue
                    # print('cuti')
                else:
                    run_line += run.text
                save_text.append(run.text)
            
            else:
                # print(run.element.xml)
                contentID = pattern.search(run.element.xml).group(0)
#                 print(contentID)
                try:
                    contentType = doc.part.related_parts[contentID].content_type
                    # print(contentType)
                except KeyError as e:
                    print(e)
                    continue
                if not contentType.startswith('image'):
                    continue
                imgName = basename(doc.part.related_parts[contentID].partname)
                # print(imgName)
                imgData = doc.part.related_parts[contentID].blob
                img_t = contentType.split('/')[-1]
                
                image_stream = Image.open(io.BytesIO(imgData))
                
                # 保存处理成宽度1000px的图片
                new_imgData = resize_image_rb1000(image_stream)
                save_image1000_path = "./{}/pictures（留存参考）/{}.{}.png".format(args.date,num,img_n)
                save_image(new_imgData, save_image1000_path)
                print("{}.{}.png".format(num,img_n),Image.open(save_image1000_path).size)
                
                # 保存第一个缩略图(300,200)
                if img_n == 1:
                    thub_imgData = resize_image(image_stream, (300,200))
                    save_thub_image_path = "./{}/thub_pic/{}.png".format(args.date,num)
                    save_image(thub_imgData, save_thub_image_path)
                    print("thub {}.png saved! shape:".format(num),Image.open(save_thub_image_path).size)
                    
                    if args.thub_type == 'txt':
                        base64path = "./{}/thumbFiles/{}.txt".format(args.date, num)
                        save_base64(save_thub_image_path, base64path)
                        print("thub {}.txt saved!".format(num))
                    else:
                        pic_path = "./{}/thumbFiles/{}.png".format(args.date, num)
                        shutil.copyfile(save_thub_image_path, pic_path)
                        print("thub {}.png saved!".format(num))
                
                img_n += 1
                
                output_buffer = io.BytesIO()
                new_imgData.save(output_buffer, format=image_stream.format.lower())
                new_imgData = output_buffer.getvalue()
                
                img_base64 = base64.b64encode(new_imgData).decode('utf-8')
                text.append(f"![image](data:image/{img_t};base64,{img_base64})")                  
        text.append(run_line)
        # print('text',text)
    
    all_doctext = '\n\n'.join(text)
    with open(outfile, 'w', encoding='utf-8') as fout:
        fout.write(all_doctext)
    
    all_savetext = ''.join(save_text)
    save_txt_path = "./{}/text/{}.txt".format(args.date, num)
    with open(save_txt_path, 'w', encoding='utf-8') as fout:
        fout.write(all_savetext)
    return True


    
    
            
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='doc')
    parser.add_argument('--date', type=str, default = '20240729', help='choose a date')
    parser.add_argument('--thub_type', type=str, default = 'txt', help='choose thumbnail type: txt, pic')
    args, unknown = parser.parse_known_args()
    
    date = args.date
    
    if os.path.exists("./{}/text/".format(date)):
        shutil.rmtree("./{}/text/".format(date))
    if os.path.exists("./{}/mdFiles/".format(date)):
        shutil.rmtree("./{}/mdFiles/".format(date))
    if os.path.exists("./{}/pictures（留存参考）/".format(date)):
        shutil.rmtree("./{}/pictures（留存参考）/".format(date))
    if os.path.exists("./{}/thub_pic/".format(date)):
        shutil.rmtree("./{}/thub_pic/".format(date))
    if os.path.exists("./{}/thumbFiles/".format(date)):
        shutil.rmtree("./{}/thumbFiles/".format(date))
    
    os.makedirs("./{}/".format(date), exist_ok = True) 
    os.makedirs("./{}/doc/".format(date), exist_ok = True) 
    os.makedirs("./{}/text/".format(date), exist_ok = True) 
    os.makedirs("./{}/mdFiles/".format(date), exist_ok = True) 
    os.makedirs("./{}/pictures（留存参考）/".format(date), exist_ok = True) 
    os.makedirs("./{}/thub_pic/".format(date), exist_ok = True) 
    os.makedirs("./{}/thumbFiles/".format(date), exist_ok = True) 
    
    files = os.listdir("./{}/doc/".format(date))
    files = [file for file in files if '.doc' in file]
    print('对下列文档进行处理：',files)
    
    for file in files:
        try:
            num = file.split('.')[0]
            docs2md(args, num)
        except Exception as e:
            print('===========================')
            print('{}.txt转写失败!!!失败原因:{}'.format(num,e))
            print('===========================')
        
    #generate_all_kuaibao_input(date, files, "./{}/text/".format(date))