import os
import requests
from lxml import etree

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'
}

url = 'https://www.1biqug.com'

search_url = 'https://www.1biqug.com/searchbook.php?keyword='

base_dir = '笔趣阁'


def download(name):
    html = get_html(search_url + name)
    list = html.xpath("//div[@class='novelslist2']//li")
    list_num = len(list)
    if list_num < 2:
        print('未搜索到相关内容')
        return
    elif list_num > 11:
        list_num = 11
    print(f'搜索成功，此处最多只展示10条搜索结果：')
    for i in range(list_num):
        if i > 0:
            type = '\n'.join(list[i].xpath("span[@class='s1']/text()")).strip()
            name = '\n'.join(list[i].xpath("span[@class='s2']/a/text()")).strip()
            author = '\n'.join(list[i].xpath("span[@class='s4']/text()")).strip()
            status = '\n'.join(list[i].xpath("span[@class='s7']/text()")).strip()
            book_url = '\n'.join(list[i].xpath("span[@class='s2']/a/@href")).strip()
            print(f'序号：{i}\t书名：{name}({status}) \t作者：{author} \t类型：{type}\t网址直达：{url + book_url}')
    # 获取用户选择
    choose = get_choose(list_num)
    # 创建下载目录
    book_name = '\n'.join(list[choose].xpath("span[@class='s2']/a/text()")).strip()
    mkdir(book_name)
    # 获取章节目录列表
    html = get_html(url + '\n'.join(list[choose].xpath("span[@class='s2']/a/@href")).strip())
    chapter_list = html.xpath("//div[@id='list']//dd/a/@href")
    for chapter_url in chapter_list:
        save_chapter_content(book_name, url + chapter_url)


def mkdir(dir):
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)
    if not os.path.exists(dir):
        os.mkdir(base_dir + '/' + dir)


def get_html(url):
    response = requests.get(url)
    return etree.HTML(response.text)


def save_chapter_content(book_name, url):
    html = get_html(url)
    title = '\n'.join(html.xpath("//div[@class='bookname']/h1/text()")).strip()
    text = '\n'.join(html.xpath("//div[@id='content']/text()")).strip()
    try:
        with open(f'{base_dir}/{book_name}/{title}.txt', mode='w', encoding='utf-8') as f:
            print(f'开始保存{title}.txt')
            f.write(text)
    except Exception as ex:
        print(f'保存{title}.txt 时发生错误：：{ex}')


def get_choose(list_num):
    while True:
        choose = input('请输入小说序号进行下载：')
        if choose.isalpha() or choose.isspace() or int(choose) < 1 or int(choose) >= list_num:
            print('你的输入有误！')
        else:
            return int(choose)


if __name__ == '__main__':
    name = input('请输入小说名称：')
    download(name)
