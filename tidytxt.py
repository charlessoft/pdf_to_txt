import ast
import codecs
import glob
import io
import json
import logging
import os
import re
import sys
from collections import Counter
from logging.config import fileConfig

import pandas as pd
from abc import ABC, abstractmethod

import config

abspath = os.path.abspath(os.path.dirname(__file__))
fileConfig(os.path.join(abspath, './logging_config.ini'))


class BaseProcessor(ABC):
    def __init__(self):
        self.data = []

    @abstractmethod
    def process_data(self):
        pass

    @abstractmethod
    def to_json(self):
        pass


class TextProcesseor(BaseProcessor):
    def __init__(self):
        super().__init__()
        self.pages = []

    def process_data(self):
        for item in self.data:
            self.add_text_to_page(item)

    def to_json(self):
        return self.pages

    def add_text_to_page(self, item):
        page_number = item['page']
        text = item['inside']

        # 查找具有相同页码的现有页面
        existing_page = None
        for page in self.pages:
            if page['page'] == page_number:
                existing_page = page
                break

        # 如果找到了具有相同页码的页面，将文本添加到内容中
        if existing_page:
            existing_page['content'] += text + '\n'
        # 否则，创建一个新的页面字典并将其添加到 pages 列表中
        else:
            new_page = {'page': page_number, 'content': text}
            self.pages.append(new_page)


class FooderProcessor(BaseProcessor):
    def process_data(self):
        pass

    def to_json(self):
        return
        # print(f"Processing {len(self.data)} items of type '页脚':")
        # for item in self.data:
        # print(item)


class HeaderProcessor(BaseProcessor):
    def process_data(self):
        pass

    def to_json(self):
        return
        # print(f"Processing {len(self.data)} items of type '页眉':")
        # for item in self.data:
        #     print(item)


class ExcelProcessor(BaseProcessor):
    def __init__(self):
        super().__init__()
        self.tables = []
        self.count = 0

    def process_data(self):
        self.count+=1
        # logging.info(f"Processing {len(self.data)} items of type 'Excel':")
        self.extract_table()

    def to_json(self):
        return self.tables

    def merge_rows(self, row1, row2):
        new_header = []
        for col1, col2 in zip(row1, row2):
            new_header.append(f"{col1}_{col2}")
        return new_header

    def has_duplicates(self, header):
        return header.index.duplicated().any()
        # return len(header) != len(set(header))
# 检查给定行中是否有超过2个相同的表头
    def has_more_than_two_duplicates(self,row):
        counter = Counter(row)
        return any(count > 2 for count in counter.values())
    # 检查 inside_list[0] 是否为空
    # def is_empty_row(self,row):
    #     return all(cell == '' for cell in row)
    def extract_table(self):
        """
        # {'page': 5, 'allrow': 50, 'type': 'excel', 'inside': "['释义项', '指', '释义内容']"}
        # {'page': 5, 'allrow': 50, 'type': 'excel', 'inside': "['释义项', '指', '释义内容']"}
        :param lines:
        :return:
        """
        # 分割字符串为行
        setPage = set()
        # 初始化一个空列表，用于存储提取的inside值
        inside_list = []
        max_column = 0
        # 遍历每一行
        for line in self.data:
            data_json = line
            setPage.add(data_json['page'])
            inside = ast.literal_eval(data_json['inside'])
            nColumn = len(inside)  # 获取有几列
            if max_column != 0 and max_column != nColumn:
                assert "%d length != %d" % (max_column, nColumn)
            else:
                max_column = nColumn
            inside_list.append(inside)

        # df = pd.DataFrame(inside_list[1:], columns=inside_list[0])

        df = pd.DataFrame(inside_list[1:], columns=inside_list[0])

        # 批量判断表头是否重复
        # header = df.iloc[0]
        # while self.has_duplicates(header):
        #     for i in range(1, len(df)):
        #         header = self.merge_rows(header, df.iloc[i])
        #         if not self.has_duplicates(header):
        #             break
        #     else:
        #         continue
        #     break

        # # 设置新的表头
        # df.columns = header
        #
        # # 删除已合并的行并重置索引
        # df.drop(range(len(header) - 1), inplace=True)
        # df.reset_index(drop=True, inplace=True)
        #
        # # print(self.count)
        # if self.count == 13:
        #     pass
        markdown = df.to_markdown()
        # 重命名重复的列名
        # df.columns = pd.io.parsers.ParserBase({'names': df.columns})._maybe_dedup_names(df.columns)
        try:
            # myjson = df.to_json(orient='records')
            buffer = io.StringIO()
            df.to_csv(buffer, index=False)
            # 将缓冲区的内容重置到开始位置
            buffer.seek(0)
            print(df)
            print("=="*10)
            header = inside_list[0]
            sorted_list = sorted(list(setPage))
            page = "-".join(str(num) for num in sorted_list)
            tableDic = {
                'header': header,
                'markdown': markdown,
                'csv': buffer.getvalue(),
                'page': page
            }
            self.tables.append(tableDic)
        except Exception as e:
            logging.error(e)
            sys.exit(1)
        return tableDic


class TidyTxt(object):
    def __init__(self):
        # self.content = content
        self.dict = {}
        self.tables = []
        self.processor_dict = {}
        self.previous_type = None
        self.file_path = ''
        self.companyInfo = { # 企业信息
            "date": '', # 日期
            "company_name": '', # 公司名称
            "stock_code": '', # 股票代码
            "stock_abbreviation": '', # 股票简称
            "report_year": '', # 报告年份
            "report_type": '' # 报告类型
        }

    def to_file(self):
        if self.file_path == '':
            return
        self.file_path += '.json'
        dist_path = os.path.join(config.TIDY_DEST_FOLDER, os.path.basename(self.file_path))
        logging.info("save file_name: %s" % dist_path)
        f = codecs.open(dist_path, 'w', 'utf-8')
        json.dump(self.to_json(), f)
        f.close()

    def to_json(self):
        dict = {}
        dict.update(self.companyInfo)
        for key in self.processor_dict:
            dict[key+'s'] = self.processor_dict[key].to_json()

        return dict

    def process_title(self,filename):
        # 使用正则表达式提取各个字段
        pattern = r"(\d{4}-\d{2}-\d{2})__(.*?)__(\d{6})__(.*?)__(\d{4}年)__([^\.]+)\.*"
        match = re.match(pattern, filename)
        if match:
            date, company_name, stock_code, stock_abbreviation, report_year, report_type = match.groups()

            # 将提取到的字段存储为字典
            self.companyInfo = {
                "date": date,
                "company_name": company_name,
                "stock_code": stock_code,
                "stock_abbreviation": stock_abbreviation,
                "report_year": report_year,
                "report_type": report_type
            }

            # 将字典转换为JSON格式
            # json_data = json.dumps(data, ensure_ascii=False)

            # print(json_data)
        else:
            raise Exception("无法匹配文件名:%s" % filename)
    def process_file(self, file_path):
        self.process_title(os.path.basename(file_path))
        self.file_path = file_path
        content = codecs.open(file_path, 'r', 'utf-8').read()
        self.process_allData(content)

    def process_allData(self, data):
        """
        安航处理内容
        :param data:
        :return:
        """
        json_data = [ast.literal_eval(line) for line in data.strip().splitlines()]

        for i, line in enumerate(json_data):
            self.process_data(line)

    def process_data(self, line):
        obj_type = line['type']
        if obj_type != self.previous_type:
            if self.previous_type in self.processor_dict:
                previous_processor = self.processor_dict[self.previous_type]
                previous_processor.process_data()
                previous_processor.data.clear()  # 清除上一个处理器的数据

        if obj_type not in self.processor_dict:
            if obj_type == 'excel':
                self.processor_dict[obj_type] = ExcelProcessor()
            elif obj_type == 'text':
                self.processor_dict[obj_type] = TextProcesseor()
            elif obj_type == '页眉':
                self.processor_dict[obj_type] = HeaderProcessor()
            elif obj_type == '页脚':
                self.processor_dict[obj_type] = FooderProcessor()
            else:
                raise Exception("no type %s" % obj_type)

        processor = self.processor_dict[obj_type]
        processor.data.append(line)
        self.previous_type = obj_type


if __name__ == '__main__':
    folder_path = config.TIDY_SRC_FOLDER #  'D:\\test_txt2'
    file_names = glob.glob(folder_path + '/*.txt')
    file_names = sorted(file_names, reverse=True)
    name_list = []
    for file_name in file_names:
        tidyTxt = TidyTxt()
        tidyTxt.process_file(file_name)
        tidyTxt.to_file()

    # tidyTxt.extract_table()

    # name_list.append(file_name)
    # allname = file_name.split('\\')[-1]
    # date = allname.split('__')[0]
    # name = allname.split('__')[1]
    # year = allname.split('__')[4]
    # change_pdf_to_txt(file_name)

#     content = """
#     {'page': 5, 'allrow': 50, 'type': 'text', 'inside': "['释义项', '指', '释义内容']"}
#     {'page': 5, 'allrow': 50, 'type': 'text', 'inside': "['释义项', '指', '释义内容']"}
# {'page': 5, 'allrow': 50, 'type': 'excel', 'inside': "['释义项', '指', '释义内容']"}
# {'page': 5, 'allrow': 51, 'type': 'excel', 'inside': "['一、简称', '指', '']"}
# {'page': 5, 'allrow': 52, 'type': 'excel', 'inside': "['安靠智电、本公司、公司、发行人', '指', '江苏安靠智能输电工程科技股份有限公司']"}
# {'page': 5, 'allrow': 53, 'type': 'excel', 'inside': "['河南安靠', '指', '河南安靠电力工程设计有限公司']"}
# {'page': 5, 'allrow': 54, 'type': 'excel', 'inside': "['溧阳常瑞', '指', '溧阳市常瑞电力科技有限公司']"}
# {'page': 5, 'allrow': 55, 'type': 'excel', 'inside': "['江苏凌瑞', '指', '江苏凌瑞电力科技有限公司']"}
# {'page': 5, 'allrow': 50, 'type': 'text', 'inside': "['释义项', '指', '释义内容']"}
# {'page': 5, 'allrow': 56, 'type': 'excel', 'inside': "['安靠创投', '指', '江苏安靠创业投资有限公司']"}
# {'page': 5, 'allrow': 57, 'type': 'excel', 'inside': "['安云创投', '指', '江苏安云创业投资有限公司']"}
# {'page': 5, 'allrow': 58, 'type': 'excel', 'inside': "['安靠有限', '指', '江苏安靠超高压电缆附件有限公司']"}
# {'page': 5, 'allrow': 59, 'type': 'excel', 'inside': "['安靠光热', '指', '江苏安靠光热发电系统科技有限公司']"}
# {'page': 5, 'allrow': 60, 'type': 'excel', 'inside': "['ABB', '指', 'ABB（中国）有限公司']"}
# {'page': 5, 'allrow': 61, 'type': 'excel', 'inside': "['3M', '指', '明尼苏达矿务及制造业公司']"}
# {'page': 5, 'allrow': 62, 'type': 'excel', 'inside': "['建创能鑫', '指', '建创能鑫（天津）创业投资有限责任公司']"}
# {'page': 5, 'allrow': 63, 'type': 'excel', 'inside': "['曲水增益、卓辉增益', '指', '曲水卓辉增益投资管理中心（有限合伙）']"}
# {'page': 5, 'allrow': 64, 'type': 'excel', 'inside': "['国家电网', '指', '国家电网有限公司']"}
# {'page': 5, 'allrow': 65, 'type': 'excel', 'inside': "['南方电网', '指', '中国南方电网有限责任公司']"}
# {'page': 5, 'allrow': 66, 'type': 'excel', 'inside': "['', '', '中国华能集团公司、中国大唐集团公司、中国华电集团公司、中国']"}
# {'page': 5, 'allrow': 67, 'type': 'excel', 'inside': "['五大发电集团', '指', '国电集团公司、国家电力投资集团公司']"}
# {'page': 5, 'allrow': 68, 'type': 'excel', 'inside': "['', '', '']"}
# {'page': 5, 'allrow': 69, 'type': 'excel', 'inside': "['中国证监会、证监会', '指', '中国证券监督管理委员会']"}
# {'page': 5, 'allrow': 70, 'type': 'excel', 'inside': "['深交所', '指', '深圳证券交易所']"}
# {'page': 5, 'allrow': 71, 'type': 'excel', 'inside': "['公司法', '指', '中华人民共和国公司法']"}
# {'page': 5, 'allrow': 72, 'type': 'excel', 'inside': "['证券法', '指', '中华人民共和国证券法']"}
# {'page': 5, 'allrow': 73, 'type': 'excel', 'inside': "['股东大会', '指', '江苏安靠智能输电工程科技股份有限公司股东大会']"}
# {'page': 5, 'allrow': 74, 'type': 'excel', 'inside': "['董事会', '指', '江苏安靠智能输电工程科技股份有限公司董事会']"}
# {'page': 5, 'allrow': 75, 'type': 'excel', 'inside': "['监事会', '指', '江苏安靠智能输电工程科技股份有限公司监事会']"}
# {'page': 5, 'allrow': 76, 'type': 'excel', 'inside': "['公司章程', '指', '江苏安靠智能输电工程科技股份有限公司章程']"}
# {'page': 5, 'allrow': 77, 'type': 'excel', 'inside': "['报告期', '指', '2019年1月1日至2019年12月31日']"}
#     """
#     tidyTxt = TidyTxt()
#     tidyTxt.process_allData(content)
# tidyTxt.extract_table()

# extract_table(content)
# main()
