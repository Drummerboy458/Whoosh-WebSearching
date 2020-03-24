import json
import os
import re
from time import sleep

# 用来解析 HTML 文本，可以获取爬到的 HTML 文本中的各个项的属性
from bs4 import BeautifulSoup
# 可以模拟浏览器获取异步数据或者执行点击操作
from selenium import webdriver

import urllib.request

import ssl

ssl._create_default_https_context = ssl._create_unverified_context

pagegraph = []  # 构建链接之间的有向图

browser = webdriver.Chrome()


# 不同老师有的信息可能并不展示，使用try-catch结构，将没有找到的项置为空
def get_cc_data(t_info, url):
    urlset = set()  # 用于判断是否重复
    try:
        # 使用剖析器为html.parser
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        allList = soup.select('tr')
        Len = len(allList)
        for i in range(1, Len):
            a = allList[i].select('td')[0].select('a')
            infoList = allList[i].text.split()
            if len(infoList) < 4:
                infoList.append('')
            try:  # 如果抛出异常就代表为空
                href = a[0]['href']
                if not href.startswith('http'):
                    href = r'http://cc.nankai.edu.cn' + href
                browser.get(href)
                if href in urlset:
                    continue
                else:
                    urlset.add(href)
            except:
                href = ''
            try:
                intro = browser.find_element_by_class_name('text').text
                intro = intro[0:min(len(intro), 100)] + ' ……'
                sleep(1)
            except:
                intro = ''
            # 把爬取到的每条数据组合成一个字典用于数据库数据的插入
            new_dict = {
                "name": infoList[0],
                "academy": '计算机学院',
                "job": infoList[1],
                'department': infoList[2],
                'researchArea': infoList[3],
                "resume": intro,
                "link": href,

            }

            saveToFile(href, "computer")  # 保存教师主页源码
            t_info.append(new_dict)
            pagegraph.append([url, href, {"anchor": infoList[0]}])
            # print(new_dict)

    except Exception as e:
        print(e)


def get_his_data(t_info, url, files, urlset):
    base_url = 'https://history.nankai.edu.cn'
    try:
        # 使用剖析器为html.parser
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        allList = soup.find_all(name='li', attrs={"class": "teacher_list_unit cl"})
        Len = len(allList)
        for i in range(1, Len):
            a = allList[i].select('a')
            infoList = re.sub('\s', '', allList[i].text)
            pos1 = infoList.find(u'职务：')
            pos2 = infoList.find(u'专业：')
            pos3 = infoList.find(u'研究方向')
            imgs = soup.find_all("img")  # 保存图片

            _path = os.getcwd()
            new_path = os.path.join(_path, 'pictures')
            if not os.path.isdir(new_path):
                os.mkdir(new_path)
            new_path += '/'
            try:
                x = 1
                global filetype
                if len(imgs) == 0:
                    print("当前页无图片!")
                for img in imgs:
                    link = img.get('src')
                    if link.find('jpg') != -1:
                        filetype = 'jpg'
                    elif link.find('png') != -1:
                        filetype = 'png'
                    elif link.find('gif') != -1:
                        filetype = 'gif'
                    else:
                        continue
                    # print("It's downloading", str(x), "piture")
                    # urllib.request.urlretrieve(base_url + link, new_path + (base_url + link).replace('/', '|'))

                    # 保存图片链接
                    if str(base_url + link) in urlset:
                        continue
                    else:
                        file_dict = {
                            "link": base_url + link,
                            "filetype": filetype,
                        }
                        files.append(file_dict)
                        urlset.add(str(base_url + link))

                    x += 1
            except Exception as e:
                print(e)
            else:
                pass
            finally:
                if x:
                    print("It's Done!!!")
            try:  # 如果抛出异常就代表为空
                href = a[0]['href']
                if not href.startswith('http'):
                    href = r'https://history.nankai.edu.cn/' + href
                browser.get(href)
                if href in urlset:
                    continue
                else:
                    urlset.add(href)
            except:
                href = ''
            try:
                intro = browser.find_element_by_class_name('tabbox-page').text
                intro = intro[0:min(len(intro), 100)] + ' ……'
                sleep(1)
            except:
                intro = ''
            # 把爬取到的每条数据组合成一个字典用于数据库数据的插入
            new_dict = {
                "name": infoList[1:pos1],
                "job": infoList[pos1 + 3:pos2],
                'department': infoList[pos2 + 3:pos3],
                'researchArea': infoList[pos3 + 5:len(infoList)],
                "link": href,
                "academy": '历史学院',
                "resume": intro
            }
            # saveToFile(href, "history")  # 保存教师主页源码
            t_info.append(new_dict)
            pagegraph.append([url, href, {"anchor": infoList[1:pos1]}])
            # print(new_dict)

    except Exception as e:
        print(e)


def get_fin_data(t_info, url):
    response = urllib.request.urlopen(url)
    soup = BeautifulSoup(response, 'lxml')  # lxml解析
    urlset = set()  # 用于判断是否重复
    try:
        # 使用剖析器为html.parser
        allList = soup.select('.shiziListBox')
        print(allList)
        global intro
        global e_mail
        for teacher in allList:
            a = teacher.select('a')
            try:  # 如果抛出异常就代表为空
                href = a[0]['href']
                tm = 'http://finance.nankai.edu.cn' + href
                print(tm)
                response_in = urllib.request.urlopen(tm)
                soup_in = BeautifulSoup(response_in, 'lxml')  # lxml解析
                if href in urlset:
                    continue
                else:
                    urlset.add(href)
                intro = soup_in.select('teacherDetail').text
                intro = intro[0:min(len(intro), 100)] + ' ……'
                sleep(1)
            except:
                href = ''
            try:  # 如果抛出异常就代表为空
                e_mail = a[1].text
            except:
                e_mail = ''

            text = teacher.select('p')[0].text.split()
            name = text[0]
            if len(text) < 2:
                cate = ''
            else:
                cate = text[1]
            # 把爬取到的每条数据组合成一个字典用于数据库数据的插入
            new_dict = {
                "name": name,
                "job": cate,
                "link": 'http://finance.nankai.edu.cn' + href,
                "academy": '金融学院',
                "resume": intro
            }
            saveToFile(href, "finance")  # 保存教师主页源码
            t_info.append(new_dict)
            pagegraph.append(
                [url, 'http://finance.nankai.edu.cn' + href, {"anchor": e_mail}])
            # print(new_dict)
    except Exception as e:
        print(e)


def finance():
    info = []
    urls = ['http://finance.nankai.edu.cn/f/teacher/teacher/qzjs',
            'http://finance.nankai.edu.cn/f/teacher/teacher/jzds',
            'http://finance.nankai.edu.cn/f/teacher/teacher/rxjs']
    for url in urls:
        get_fin_data(info, url)
    # 写入
    saveDict('finance.json', info)


def history():
    info = []
    files = []  # 抓取教师图片
    urlset = set()  # 用于判断是否重复
    urls = [r'https://history.nankai.edu.cn/16054/list.htm',
            r'https://history.nankai.edu.cn/16055/list.htm',
            r'https://history.nankai.edu.cn/16056/list.htm']
    for url in urls:
        browser.get(url)
        get_his_data(info, url, files, urlset)
    # 写入
    # saveDict('history.json', info)
    saveDict('history_images.json', files)


def computercol():
    info = []
    urls = [r'http://cc.nankai.edu.cn/jswyjy/list.htm', r'http://cc.nankai.edu.cn/fjswfyjy/list.htm',
            r'http://cc.nankai.edu.cn/js/list.htm', r'http://cc.nankai.edu.cn/syjxdw/list.htm']
    for url in urls:
        browser.get(url)
        get_cc_data(info, url)
    # 写入
    saveDict('computer.json', info)


def getElec(baseUrl, index, result, url_record):
    seedUrl = baseUrl + str(index)
    print(seedUrl)
    response = urllib.request.urlopen(seedUrl)
    soup = BeautifulSoup(response, 'lxml')  # lxml解析
    teachers = soup.select('tbody tr')  # 教师列表，每一行为一项
    title = soup.select('title')
    print(title)
    # 输出到控制台以及写到文件
    for teacher in teachers:
        info = {}
        link = teacher.a['href']  # 教师主页链接
        url = baseUrl + '/' + str(link)
        name = teacher.select('td')[0].string
        job = teacher.select('td')[1].string
        department = teacher.select('td')[2].string
        researchArea = teacher.select('td')[3].string

        info['name'] = name
        info['academy'] = "电子信息与光学工程学院"
        info['job'] = job
        info['department'] = department
        info['researchArea'] = researchArea
        info['resume'] = getResume(link)
        info['link'] = url

        if url not in url_record:
            result.append(info)
            url_record.add(url)
            saveToFile(url, "electric")  # 保存教师主页源码
            pagegraph.append(
                [seedUrl, url, {"anchor": name}])
    print('成功抓取', len(teachers), '位电光教师信息')


def elec():
    baseUrl = 'https://ceo.nankai.edu.cn/szll'
    indexs = ['/xdgxyjs.htm', '/gdzbmqjyjsyjs.htm', '/wdzgcx.htm',
              '/dzkxygcx.htm', '/dzxxgcx.htm', '/txgcx.htm', '/dzxxsyjxzx.htm', '/ICsjzx.htm']
    result=[]
    url_record = set()  # 用来去除重复的爬取
    for index in indexs:
        getElec(baseUrl, index, result, url_record)
    saveDict('elec.json', result)


def getResume(link):
    baseUrl = 'https://ceo.nankai.edu.cn/szll'
    url = baseUrl + '/' + str(link)
    # print(url)
    page = urllib.request.urlopen(url)
    soup = BeautifulSoup(page, 'lxml')  # lxml解析
    text = soup.select('#vsb_content')[0].text
    return text


def saveToFile(url, academy):
    page = urllib.request.urlopen(url)
    html = page.read()

    html = html.decode('utf-8')

    # print(html)
    # 保存抓取到的网页源码
    os.makedirs(academy + "/", exist_ok=True)
    fileOb = open(academy + "/" + str(url).replace('/', '|'), 'w')
    fileOb.write(html)
    fileOb.close()


def saveDict(path, obj):
    with open(path, 'w') as f:
        json.dump(obj, f, ensure_ascii=False)





if __name__ == "__main__":
    # finance()
    # computercol()
    history()
    # elec()
    # saveDict('pageGraph.json', pagegraph)
