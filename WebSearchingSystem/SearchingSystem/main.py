import json

from flask import Flask, render_template, request, jsonify, make_response
from whoosh.index import open_dir
from whoosh.qparser import QueryParser
from flask_paginate import Pagination, get_page_parameter
import pymysql.cursors

import datetime as d

import time
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # 解决中文乱码问题

buffer = []
results = []
hot_type = ""
hot_word = ""
details = []  # 教师的个人简介
items = []  # 最近的热搜条目
temp = []
nums = 0  # 搜索的匹配结果数量
duration = 0  # 查询时间
ix = open_dir('index')
ix_image = open_dir('index_for_imag')
file = open('PageRank.json', 'r')  # 读取PageRank的计算结果
content = file.read()
pageRank = json.JSONDecoder(strict=False).decode(content)


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/search/')  # GET 请求
def search():
    connection = pymysql.connect(host='localhost', user='root',
                         password='Liwenwei1999.', db='web_searching', charset='utf8mb4')

    clock = d.datetime.now().strftime("%Y.%m.%d-%H:%M:%S")
    global nums
    global temp
    global duration
    global details
    global items
    global buffer
    global hot_type
    global hot_word
    global results
    perPage = 10
    q = request.args.get("q")
    target = request.args.get("target")
    page = request.args.get(get_page_parameter(), type=int, default=1)  # 分页实现
    print("page", page)

    if page is 1:  # 第一次查询
        details = []  # 重新初始化各全局变量
        items = []
        results = []
        temp = []


        try:
            # 获取会话指针
            with connection.cursor() as cursor:
                sql2 = "select  `query` from `items`  where `query` =" + "\'" + q + " \'"
                # print(sql2)
                count = cursor.execute(sql2)
                # print(count)
                if count is 0:  # 新的搜索词
                    if len(q) != 0:
                        sql3 = "insert into `items`(`query`,`freq`,`type`) values(%s,%s,%s)"
                        cursor.execute(sql3, (q, 1, target))
                else:
                    sql4 = "update `items` set  `freq` =  `freq` + 1 where `query` =" + "\'" + q + " \'" + \
                           "and  `type` =" + "\'" + target + " \'"
                    # print(sql4)
                    cursor.execute(sql4)
                sql = "select  `query`,`type` from `items` order by `freq` Desc"  # 查询最近的热搜词汇
                # 查询所有行数
                count = cursor.execute(sql)
                # print(count)
                hot_query = cursor.fetchmany(min(count, 5))
                # 查询前5条数据
                hot_type = hot_query[0][1]
                hot_word = hot_query[0][0]
                # print(hot_type)
                for item in hot_query:
                    # print(item)
                    items.append(str(item[0]).strip(',()\''))  # 去除特殊字符

                # 将热搜榜排名第一的查询结果进行缓存，下一次判断如果为该查询则读取即可
                if len(buffer) == 0:
                    parse = QueryParser(hot_type, schema=ix.schema).parse(items[0])
                    searcher = ix.searcher()
                    buffer = searcher.search(parse, limit=None)
                    print("热搜榜第一条检索到", len(buffer), "个结果，已缓存..")

                # 创建SQL语句
                sql1 = "insert into `log`(`user`,`time`, `query`, `type`) values(%s,%s,%s,%s)"
                # 执行SQL语句
                cursor.execute(sql1, ('lww', clock, q, target))
                # 提交
                connection.commit()
        finally:
            connection.close()
        # 判断是否能从缓存中直接得到结果
        if target == hot_type and q == hot_word:
            print("缓存得到结果")
            duration = 0
            results = buffer
            # print(results)
        else:
            if target == 'filetype':
                mparser = QueryParser(target, schema=ix_image.schema).parse(q)
                searcher = ix_image.searcher()
                startTime = time.time()
                results = searcher.search(mparser, limit=None)
                print(len(results))
                endTime = time.time()
                duration = float(endTime) - float(startTime)  # 计算查询时间

            else:
                mparser = QueryParser(target, schema=ix.schema).parse(q)
                searcher = ix.searcher()
                startTime = time.time()
                results = searcher.search(mparser, limit=None)
                endTime = time.time()
                duration = float(endTime) - float(startTime)  # 计算查询时间
        toSort = {}
        # 根据pageRank值从大到小排序
        for result in results:
            if result['link'] in pageRank.keys():
                toSort[result['link']] = pageRank[result['link']]
            else:
                toSort[result['link']] = 0  # 防止意外出错

        for i in toSort.keys():
            print(toSort[i])

        sortedResult = sortedDict(toSort)
        print()
        for i in sortedResult.keys():
            print(sortedResult[i])
        if target == 'filetype':
            for result in results:
                tm = {}
                tm['title'] = result['link']
                tm['link'] = result['link']
                tm['snapshot'] = result['link'].replace('/', '|')
                #print(tm['snapshot'])
                details.append(tm)
        else:
            i = 0
            for link in sortedResult.keys():
                for result in results:
                    if result['link'] == link:
                        i += 1
                        tm = {}
                        tm['title'] = result['academy'] + result['name'] + result['job']
                        tm['snapshot'] = result['link'].replace('/', '|')  # 找到对应链接的本地源码
                        r = result.highlights('resume')
                        if len(r) is 0:
                            tm['description'] = result['resume'][0:200]
                        else:
                            tm['description'] = result.highlights('resume')
                        tm['link'] = result['link']
                        tm['no'] = i  # 记录是排名第几的搜索结果
                        details.append(tm)
        # print(res)
        # print(details)
        nums = len(results)
        temp = details[0 : perPage]
        print('一共发现%d份文档。' % nums)

    else:
        start = (page-1) * perPage  # 计算当前页显示的数据位置
        end = start + perPage
        temp = details[start: end]

    pagination = Pagination(page=page, total=nums, bs_version=4)
    return render_template('search.html', query=q, nums=nums,
                           time=duration, pagination=pagination, details=temp, items=items)


def sortedDict(d):
    temp = sorted(d.items(), key=lambda x: x[1], reverse=True)
    sorted_dict = {}
    for item in temp:
        sorted_dict[item[0]] = item[1]

    return sorted_dict


if __name__ == '__main__':
    app.run()