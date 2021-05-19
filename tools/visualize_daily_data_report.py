#**coding:utf-8**

import os
import json
import sys
from prettytable import PrettyTable
from PIL import Image, ImageDraw, ImageFont
import fnmatch
from read_and_write_json import loadTag,saveTag


def getMatchedFilePaths(data_dir,
                        pattern="*",
                        formats=[".json"],
                        recursive=False):
    files = []
    data_dir = os.path.normpath(os.path.abspath(data_dir))
    for f in os.listdir(data_dir):
        current_path = os.path.join(os.path.normpath(data_dir), f)
        if os.path.isdir(current_path) and recursive:
            files += getMatchedFilePaths(current_path, pattern, formats,
                                         recursive)
        elif fnmatch.fnmatch(f,
                             pattern) and os.path.splitext(f)[-1] in formats:
            files.append(current_path)
    return files

def main():

    report_json_list = getMatchedFilePaths('../data_report', pattern="*")

    for report_json_path in report_json_list:

        tag = loadTag(report_json_path,'')
        # report_png_path = report_json_path.replace('.json','.png')
        # if os.path.exists(report_png_path):
        #     continue

        date = list(tag.keys())[0]

        table = PrettyTable([' 上传日期 ', ' 核验结果 ', ' 数据名称 ', ' 数据类型 ',' 数据大小(MB) ',' 上传路径 '])
        if 'true' in tag[date].keys():
            for i in tag[date]['true']:
                addTableRow(table,tag[date]['true'][i])
        if 'false' in tag[date].keys():
            table.add_row(['','','','','',''])
            for i in tag[date]['false']:
                addTableRow(table,tag[date]['false'][i])

        table.align[1] = 'l'
        table.border = True
        table.junction_char = '+'
        table.horizontal_char = '+'
        table.vertical_char = '|'
        createTableImg(table,tag[date],date)
        print(table)

def addTableRow(table,data_list):
    upload_date = data_list['upload_date']
    data_name = data_list['data_name']
    data_type = data_list['data_type']
    data_link = data_list['data_link']
    data_size = data_list['file_size(MB)']
    check_result = data_list['check_result']
    table.add_row([upload_date,check_result,data_name,data_type,data_size,data_link])
    return table

def createTableImg(table,tag_data,date,**kwargs):
    space = 22  ## 表格边距
    line_height = 8
    kwargs['font'] = "ui/font/simkai.ttf"
    kwargs['default_font_size'] = 20
    kwargs['table_title_font_size'] = 28
    kwargs['default_background_color'] = (255,255,255,255)
    kwargs['table_top_heght'] = kwargs['table_title_font_size'] + space + int(kwargs['table_title_font_size'] / 2)
    describe_len = 0
    kwargs['table_botton_heght'] = describe_len * kwargs['default_font_size'] + space
    kwargs['img_type'] = 'PNG'
    font = ImageFont.truetype(kwargs['font'], kwargs['default_font_size'], encoding='utf-8')
    font2 = ImageFont.truetype(kwargs['font'], kwargs['table_title_font_size'], encoding='utf-8')

    im = Image.new('RGB', (10, 10), kwargs['default_background_color'])
    draw = ImageDraw.Draw(im)
    tab_info =  str(table)
    img_size = draw.multiline_textsize(tab_info, font=font)
    img_width = img_size[0] + space * 2
    table_height = img_size[1] + space * 2
    img_height = table_height + kwargs['table_botton_heght'] + kwargs['table_top_heght']
    im_new = im.resize((img_width, img_height))
    draw = ImageDraw.Draw(im_new, 'RGB')
    draw.multiline_text((space, kwargs['table_top_heght']), tab_info + '\n\n', fill=(0, 0, 0), font=font)

    table_title = date.replace('_','')+' 数据产线报告'
    title_left_padding = (img_width - len(table_title) * kwargs['table_title_font_size']) / 2
    draw.multiline_text((title_left_padding, space), table_title, fill=(20, 0, 0), font=font2, align='center')

    y = table_height + space / 2
    if "False_file_size(MB)" in tag_data.keys():
        false_file_size = str(tag_data["False_file_size(MB)"] / 1000) + '(GB)'
    else:
        false_file_size = str(0) + '(GB)'
    if "True_file_size(MB)" in tag_data.keys():
        true_file_size = str(tag_data["True_file_size(MB)"] / 1000) + '(GB)'
    else:
        true_file_size = str(0) + '(GB)'

    if "Test_length(Min)" in tag_data.keys():
        test_time_size = str(tag_data["Test_length(Min)"]) + '(Min)'
    else:
        test_time_size = str(0) + '(Min)'

    kwargs['describe'] = ['正常数据总量：' + true_file_size,
                          '测试总时长：' + test_time_size,
                          '异常数据总量：' + false_file_size]

    y = y + kwargs['default_font_size']
    frist_row = kwargs['describe'].pop(0)
    draw.text((space, y), frist_row, fill=(0, 0, 0), font=font)
    for describe_row in kwargs['describe']:
        y = y + kwargs['default_font_size'] + line_height
        draw.text((space, y), describe_row, fill=(0, 0, 0), font=font)
    del draw
    img_name = ''.join(['data_report/',date,'.png'])
    im_new.save(img_name, kwargs['img_type'],dpi=(300.0,300.0))
    #im_new.show()



if __name__ == "__main__":
    main()


