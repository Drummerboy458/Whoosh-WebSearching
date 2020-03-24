import json
import os

from whoosh.index import create_in, open_dir
from whoosh.fields import *
from whoosh.fields import Schema
from jieba.analyse import ChineseAnalyzer

analyzer = ChineseAnalyzer()
# 创建schema, stored为True表示能够被检索
schema = Schema(name=ID(stored=True, analyzer=analyzer),  # 姓名
                job=TEXT(stored=True, analyzer=analyzer),  # 职务
                department=TEXT(stored=True, analyzer=analyzer),  # 所在部门
                researchArea=TEXT(stored=True, analyzer=analyzer),  # 研究方向
                resume=TEXT(stored=True, analyzer=analyzer),  # 简介
                academy=ID(stored=True, analyzer=analyzer),  # 学院
                link=ID(stored=True),  # 主页链接
                )


def getTeachers(path):
    file = open(path, 'r')
    content = file.read()
    teachers = json.JSONDecoder(strict=False).decode(content)
    return teachers


def createIndex():
    global ix
    if not os.path.exists("index"):
        os.mkdir("index")
        ix = create_in("index", schema)
    else:
        ix = open_dir('index')
    writer = ix.writer()
    # 电光学院
    paths = ['/Users/lww/PycharmProjects/WebSearchingSystem/Spider/elec.json',
             '/Users/lww/PycharmProjects/WebSearchingSystem/Spider/finance.json',
             '/Users/lww/PycharmProjects/WebSearchingSystem/Spider/computer.json',
             '/Users/lww/PycharmProjects/WebSearchingSystem/Spider/history.json'
             ]
    for path in paths:
        teachers = getTeachers(path)
        for pop_dict in teachers:
            name = pop_dict['name']
            job = pop_dict['job']
            if 'depatment' in pop_dict.keys():
                department = pop_dict['department']
            else:
                department = ""
            if 'researchArea' in pop_dict.keys():
                researchArea = pop_dict['researchArea']
            else:
                researchArea = ""
            resume = pop_dict['resume']
            link = pop_dict['link']
            academy = pop_dict['academy']
            writer.add_document(name=name, job=job, department=department, researchArea=researchArea,
                                resume=resume, academy=academy, link=link)

    writer.commit()
    print('添加成功')


def main():
    createIndex()


if __name__ == '__main__':
    main()