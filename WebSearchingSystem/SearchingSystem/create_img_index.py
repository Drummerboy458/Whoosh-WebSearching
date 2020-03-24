import json
import os

from whoosh.index import create_in, open_dir
from whoosh.fields import *
from whoosh.fields import Schema

# 创建schema, stored为True表示能够被检索
schema = Schema(link=ID(stored=True),  # 文件的链接
                filetype=ID(stored=True)  # 文件类型
           )


def getFiles(path):
    file = open(path, 'r')
    content = file.read()
    files = json.JSONDecoder(strict=False).decode(content)
    return files


def createIndex():
    global ix
    if not os.path.exists("index_for_imag"):
        os.mkdir("index_for_imag")
        ix = create_in("index_for_imag", schema)
    else:
        ix = open_dir('index_for_imag')
    writer = ix.writer()
    # 电光学院
    paths = ['/Users/lww/PycharmProjects/WebSearchingSystem/Spider/history_images.json']
    for path in paths:
        files = getFiles(path)
        for file in files:
            link = file['link']
            filetype = file['filetype']

            writer.add_document(link=link, filetype=filetype)
    writer.commit()
    print('添加成功')


def main():
    createIndex()


if __name__ == '__main__':
    main()