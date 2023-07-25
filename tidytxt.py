import ast
import json
import pandas as pd
from abc import ABC, abstractmethod


class BaseProcessor(ABC):
    def __init__(self):
        self.data = []

    @abstractmethod
    def process_data(self):
        pass


class TextProcesseor(BaseProcessor):

    def process_data(self):
        print(f"Processing {len(self.data)} items of type 'Text':")
        for item in self.data:
            print(item)


class ExcelProcessor(BaseProcessor):
    def __init__(self):
        self.tables = []
        super().__init__()

    def process_data(self):
        print(f"Processing {len(self.data)} items of type 'Excel':")
        for item in self.data:
            print(item)
        self.extract_table()

    def extract_table(self):
        """
        # {'page': 5, 'allrow': 50, 'type': 'excel', 'inside': "['释义项', '指', '释义内容']"}
        # {'page': 5, 'allrow': 50, 'type': 'excel', 'inside': "['释义项', '指', '释义内容']"}
        :param lines:
        :return:
        """
        # 分割字符串为行
        # lines = content.strip().splitlines()
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

        df = pd.DataFrame(inside_list[1:], columns=inside_list[0])
        markdown = df.to_markdown()
        header = inside_list[0]
        sorted_list = sorted(list(setPage))
        page = "-".join(str(num) for num in sorted_list)
        tableDic = {
            'header': header,
            'markdown': markdown,
            'page': page
        }
        self.tables.append(tableDic)
        return tableDic


class TidyTxt(object):
    def __init__(self):
        # self.content = content
        self.dict = {}
        self.tables = []
        self.processor_dict = {}
        self.previous_type = None
        pass


    def process_allData(self, data, processor_dict=None):
        # json_data = [json.loads(line) for line in data.strip().split('\n')]
        json_data = [ast.literal_eval(line) for line in data.strip().splitlines()]

        for i, line in enumerate(json_data):
            self.process_data(line)

            # obj_type = line['type']
            # print(obj_type)

            # if obj_type not in processor_dict:
            #     if obj_type == 'Excel':
            #         processor_dict[obj_type] = ExcelProcessor()
            #     # elif obj_type == 'PDF':
            #     #     processor_dict[obj_type] = PDFProcessor()
            #
            # processor = processor_dict[obj_type]
            # processor.data.append(obj)
            #
            # if i < len(json_data) - 1:
            #     next_obj_type = json_data[i + 1]['type']
            #     if obj_type != next_obj_type:
            #         processor.process_data()
            #         processor.data = []

    def process_data(self, line):
        obj_type = line['type']
        if obj_type != self.previous_type:
            if self.previous_type in self.processor_dict:
                previous_processor = self.processor_dict[self.previous_type]
                previous_processor.process_data()
                previous_processor.data.clear()  # 清除上一个处理器的数据
            # if obj_type in self.processor_dict:
            #     self.processor_dict[obj_type].process_data()

        if obj_type not in self.processor_dict:
            if obj_type == 'excel':
                self.processor_dict[obj_type] = ExcelProcessor()
            elif obj_type == 'text':
                self.processor_dict[obj_type] = TextProcesseor()
            else:
                print("nonono")

        processor = self.processor_dict[obj_type]
        processor.data.append(line)
        self.previous_type = obj_type




if __name__ == '__main__':
    content = """
    {'page': 5, 'allrow': 50, 'type': 'text', 'inside': "['释义项', '指', '释义内容']"}
    {'page': 5, 'allrow': 50, 'type': 'text', 'inside': "['释义项', '指', '释义内容']"}
{'page': 5, 'allrow': 50, 'type': 'excel', 'inside': "['释义项', '指', '释义内容']"}
{'page': 5, 'allrow': 51, 'type': 'excel', 'inside': "['一、简称', '指', '']"}
{'page': 5, 'allrow': 52, 'type': 'excel', 'inside': "['安靠智电、本公司、公司、发行人', '指', '江苏安靠智能输电工程科技股份有限公司']"}
{'page': 5, 'allrow': 53, 'type': 'excel', 'inside': "['河南安靠', '指', '河南安靠电力工程设计有限公司']"}
{'page': 5, 'allrow': 54, 'type': 'excel', 'inside': "['溧阳常瑞', '指', '溧阳市常瑞电力科技有限公司']"}
{'page': 5, 'allrow': 55, 'type': 'excel', 'inside': "['江苏凌瑞', '指', '江苏凌瑞电力科技有限公司']"}
{'page': 5, 'allrow': 50, 'type': 'text', 'inside': "['释义项', '指', '释义内容']"}
{'page': 5, 'allrow': 56, 'type': 'excel', 'inside': "['安靠创投', '指', '江苏安靠创业投资有限公司']"}
{'page': 5, 'allrow': 57, 'type': 'excel', 'inside': "['安云创投', '指', '江苏安云创业投资有限公司']"}
{'page': 5, 'allrow': 58, 'type': 'excel', 'inside': "['安靠有限', '指', '江苏安靠超高压电缆附件有限公司']"}
{'page': 5, 'allrow': 59, 'type': 'excel', 'inside': "['安靠光热', '指', '江苏安靠光热发电系统科技有限公司']"}
{'page': 5, 'allrow': 60, 'type': 'excel', 'inside': "['ABB', '指', 'ABB（中国）有限公司']"}
{'page': 5, 'allrow': 61, 'type': 'excel', 'inside': "['3M', '指', '明尼苏达矿务及制造业公司']"}
{'page': 5, 'allrow': 62, 'type': 'excel', 'inside': "['建创能鑫', '指', '建创能鑫（天津）创业投资有限责任公司']"}
{'page': 5, 'allrow': 63, 'type': 'excel', 'inside': "['曲水增益、卓辉增益', '指', '曲水卓辉增益投资管理中心（有限合伙）']"}
{'page': 5, 'allrow': 64, 'type': 'excel', 'inside': "['国家电网', '指', '国家电网有限公司']"}
{'page': 5, 'allrow': 65, 'type': 'excel', 'inside': "['南方电网', '指', '中国南方电网有限责任公司']"}
{'page': 5, 'allrow': 66, 'type': 'excel', 'inside': "['', '', '中国华能集团公司、中国大唐集团公司、中国华电集团公司、中国']"}
{'page': 5, 'allrow': 67, 'type': 'excel', 'inside': "['五大发电集团', '指', '国电集团公司、国家电力投资集团公司']"}
{'page': 5, 'allrow': 68, 'type': 'excel', 'inside': "['', '', '']"}
{'page': 5, 'allrow': 69, 'type': 'excel', 'inside': "['中国证监会、证监会', '指', '中国证券监督管理委员会']"}
{'page': 5, 'allrow': 70, 'type': 'excel', 'inside': "['深交所', '指', '深圳证券交易所']"}
{'page': 5, 'allrow': 71, 'type': 'excel', 'inside': "['公司法', '指', '中华人民共和国公司法']"}
{'page': 5, 'allrow': 72, 'type': 'excel', 'inside': "['证券法', '指', '中华人民共和国证券法']"}
{'page': 5, 'allrow': 73, 'type': 'excel', 'inside': "['股东大会', '指', '江苏安靠智能输电工程科技股份有限公司股东大会']"}
{'page': 5, 'allrow': 74, 'type': 'excel', 'inside': "['董事会', '指', '江苏安靠智能输电工程科技股份有限公司董事会']"}
{'page': 5, 'allrow': 75, 'type': 'excel', 'inside': "['监事会', '指', '江苏安靠智能输电工程科技股份有限公司监事会']"}
{'page': 5, 'allrow': 76, 'type': 'excel', 'inside': "['公司章程', '指', '江苏安靠智能输电工程科技股份有限公司章程']"}
{'page': 5, 'allrow': 77, 'type': 'excel', 'inside': "['报告期', '指', '2019年1月1日至2019年12月31日']"}
    """
    tidyTxt = TidyTxt()
    tidyTxt.process_allData(content)
    # tidyTxt.extract_table()

    # extract_table(content)
    # main()
