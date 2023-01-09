import json
import os
import re
from tkinter.filedialog import askdirectory

import requests
import threading
import time
from tkinter import *
from tkinter.ttk import *

headers = {
    'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
}

# 默认保存路径
folder_name = 'C:/'


def open_dir(dir):
    if os.path.exists(dir):
        os.startfile(dir)
    else:
        os.mkdir(dir)
        os.startfile(dir)


class Win:
    def __init__(self):
        self.root = self.__win()
        self.tk_button_open_dir = self.__tk_button_open_dir()
        self.tk_button_save_dir = self.__tk_button_save_dir()
        self.tk_input_save_dir = self.__tk_input_save_dir()
        self.tk_input_share_url = self.__tk_input_share_url()
        self.tk_button_download = self.__tk_button_download()
        self.tk_button_cancel_download = self.__tk_button_cancel_download()
        self.tk_text_show = self.__tk_text_show()
        self.status_download = True

    def __win(self):
        root = Tk()
        root.title("抖音无水印视频下载助手20220831 - lyusantu")
        # 设置大小 居中展示
        width = 620
        height = 520
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        geometry = '%dx%d+%d+%d' % (width, height, (screen_width - width) / 2, (screen_height - height) / 2)
        root.geometry(geometry)
        root.resizable(width=False, height=False)
        return root

    def show(self):
        self.root.mainloop()

    def __tk_button_open_dir(self):
        btn = Button(self.root, text="打开存储路径", command=self.opendir)
        btn.place(x=10, y=90, width=100, height=32)
        return btn

    def __tk_button_save_dir(self):
        btn = Button(self.root, text="选择存储路径", command=self.savedir)
        btn.place(x=120, y=90, width=100, height=32)
        return btn

    def __tk_input_save_dir(self):
        ipt = Entry(self.root, state='normal')
        ipt.place(x=230, y=90, width=375, height=32)
        ipt.insert(INSERT, folder_name)
        return ipt

    def getdir(self):
        return self.tk_input_save_dir.get()

    def opendir(self):
        open_dir(self.tk_input_save_dir.get())

    def savedir(self):
        global folder_name
        folder_name = askdirectory()
        if folder_name != '':
            self.tk_input_save_dir.delete(0, 'end')
            self.tk_input_save_dir.insert(0, folder_name)

    def __tk_input_share_url(self):
        ipt = Entry(self.root)
        ipt.insert(INSERT, '请在此处粘贴你想下载的抖音分享链接，支持单视频/图文视频/用户所有视频/合集视频/短剧视频下载')
        ipt.place(x=10, y=10, width=595, height=30)
        return ipt

    def __tk_button_download(self):
        btn = Button(self.root, text="开始下载", command=self.download)
        btn.place(x=10, y=50, width=80, height=32)
        return btn

    def __tk_button_cancel_download(self):
        btn = Button(self.root, text="结束下载", command=self.cancel_download, state='disable')
        btn.place(x=100, y=50, width=80, height=32)
        return btn

    def __tk_text_show(self):
        text = Text(self.root)
        text.configure(state='normal')
        text.place(x=10, y=130, width=595, height=376)
        return text

    # 开始下载
    def download(self):
        url = self.tk_input_share_url.get()
        if url:
            self.tk_button_download['state'] = 'disable'
            self.tk_button_cancel_download['state'] = 'normal'
            obj = threading.Thread(target=self.analysis, args=({url}))
            obj.daemon = True
            obj.start()
        else:
            self.print_log("请输入抖音分享链接")

        # 结束下载

    def cancel_download(self):
        self.status_download = False

    # 创建目录
    def create_folder(self, dirname):
        if os.path.exists(dirname):
            os.chdir(path=dirname)
            pass
        else:
            os.mkdir(dirname)
            os.chdir(path=dirname)

    def analysis(self, url):
        try:
            self.status_download = True
            try:
                url = re.search(r'[a-zA-z]+://[^\s]*', url).group(0)
            except Exception as e:
                self.print_log('下载失败：未检测到分享链接')
                self.tk_button_download['state'] = 'normal'
                self.tk_button_cancel_download['state'] = 'disable'
                return
            response = requests.get(url=url, headers=headers, allow_redirects=False)
            location = str(response.headers['location'])
            self.print___()
            self.print_log(f'开始解析分享链接：{url}')
            if location.find('share/video') != -1:
                self.download_video(url)
            elif location.find('share/user') != -1:
                self.download_user(response)
            elif location.find('share/mix') != -1:
                self.download_mix(response)
            elif location.find('share/playlet') != -1:
                self.download_playlet(response)
            else:
                self.print___()
                self.print_log('未匹配到下载类型，请检查分享链接是否正确')
        except Exception as ex:
            self.print_log(f'下载失败：{ex}')
        self.tk_button_download['state'] = 'normal'
        self.tk_button_cancel_download['state'] = 'disable'

    def download_video(self, url):
        response = requests.get(url=url, headers=headers, allow_redirects=False)
        location = str(response.headers['location'])
        aweme_id = re.match(r'.*video/(\d+)', location).group(1)
        result = requests.get('https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids=' + aweme_id,
                              headers=headers).json()
        vid = result['item_list'][0]['video']['play_addr']['uri']
        video_name = result['item_list'][0]['desc']
        video_name = video_name.replace('?', '').replace('\n', '').replace(':', '')
        if video_name == '':
            video_name = '无名称视频' + vid
        self.print_log(f'开始下载单视频<{video_name}>')
        if len(video_name) > 200:
            video_name = video_name[0: 200]
            self.print_log('由于视频名称过长，避免下载失败，已缩短视频名称..')

        images = result['item_list'][0]['images']
        if images is None:
            video_api = 'https://aweme.snssdk.com/aweme/v1/play/?video_id=' + vid + '&ratio=1080p&line=0'
            video = requests.get(video_api, headers=headers, stream=True)
            size = 0  # 初始化已下载大小
            chunk_size = 1024  # 每次下载的数据大小
            if video.status_code == 200:
                filename = os.path.join(folder_name, f'{video_name}' + '.mp4')
                with open(filename, 'wb') as f:
                    for data in video.iter_content(chunk_size=chunk_size):
                        f.write(data)
                        size += len(data)
            video_size = round(int(video.headers["content-length"]) / chunk_size / chunk_size, 2)
            self.print_log(f'结束下载单视频<{video_name}>，大小：{video_size}MB')
        else:
            self.print_log('视频类型为图文视频，改为下载图文..')
            # 视频保存路径
            video_name = video_name.replace(' ', '')
            save_dir = folder_name + '/' + video_name
            print(save_dir)
            self.create_folder(save_dir)
            images = result['item_list'][0]['images']
            for i in range(len(images)):
                with open(save_dir + '/' + str(i + 1) + '.png', 'wb') as v:
                    v.write(requests.get(url=images[i]['url_list'][0], headers=headers).content)
            self.print_log(f'图文视频<{video_name}>下载完成')

    def download_user(self, response):
        sec_uid = re.findall('(?<=sec_uid=)[a-z，A-Z，0-9, _, -]+', response.headers['location'], re.M | re.I)[0]
        # 用户信息
        userinfo = json.loads(
            requests.get(url='https://www.iesdouyin.com/web/api/v2/user/info/?sec_uid={}'.format(sec_uid),
                         headers=headers).text)
        nickname = userinfo['user_info']['nickname']
        signature = userinfo['user_info']['signature']
        follower_count = userinfo['user_info']['follower_count']  # 粉丝量
        total_favorited = userinfo['user_info']['total_favorited']  # 点赞量
        aweme_count = userinfo['user_info']['aweme_count']  # 视频数
        self.print_log(f'准备下载用户视频，用户名：{nickname}，视频总数：{aweme_count}')
        # 视频保存路径
        self.create_folder(folder_name + '/' + nickname)
        # 视频下载所需数据
        count = 0
        year = ('2018', '2019', '2020', '2021', '2022')
        month = ('01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12')
        timepool = [x + '-' + y + '-01 00:00:00' for x in year for y in month]
        k = len(timepool)
        for i in range(k):
            if not self.status_download:
                self.print_log('停止下载视频!')
                break
            if i < k - 1:
                min_cursor = int(time.mktime(time.strptime(timepool[i], '%Y-%m-%d %H:%M:%S')) * 1000)
                max_cursor = int(time.mktime(time.strptime(timepool[i + 1], '%Y-%m-%d %H:%M:%S')) * 1000)
            params = {
                'count': 500,
                'sec_uid': sec_uid,
                'min_cursor': min_cursor,
                'max_cursor': max_cursor
            }
            url = 'https://www.iesdouyin.com/web/api/v2/aweme/post/?'
            html = requests.get(url=url, params=params, headers=headers).text
            if html != '':
                data = json.loads(html)
                num = len(data['aweme_list'])
                if num > 0:
                    for j in range(num):
                        if not self.status_download:
                            self.print_log('停止下载视频!')
                            break
                        count += 1
                        video_url = data['aweme_list'][j]['video']['play_addr']['url_list'][0]
                        video_name = data['aweme_list'][j]['desc'].replace('?', '').replace('\n', '').replace(':', '')
                        if video_name == '':
                            video_name = nickname + '的无名称视频' + str(num)
                        if len(video_name) > 200:
                            video_name = video_name[0: 200]
                            self.print_log('由于视频名称过长，避免下载失败，已缩短视频名称..')
                        with open(video_name + '.mp4', 'wb') as v:
                            v.write(requests.get(url=video_url, headers=headers).content)
                            self.print_log(r'开始下载第{}个视频：{}'.format(str(count), video_name))
        self.print_log(f'下载任务已结束，共下载了{count}个视频 :)')

    def download_mix(self, response):
        mid = re.findall('detail/(.*?)/\?', response.headers['location'], re.M | re.I)[0]
        # 获取作品数
        page_url = "https://www.iesdouyin.com/web/api/mix/detail/?mix_id=" + mid
        page_resp = requests.get(url=page_url, headers=headers, allow_redirects=False).json()
        count = int(page_resp["mix_info"]["statis"]["updated_to_episode"])
        page = int(count / 10) + int(0 if count % 10 == 0 else 1)
        author = page_resp['mix_info']['author']['nickname']
        mix_name = page_resp['mix_info']['mix_name']
        # self.tk_input_input_username.insert(0, author)
        # self.tk_input_input_videocount.insert(0, mix_name)
        self.print_log(f'准备下载合集视频，合集名称：{mix_name}，视频总数：{count}，发布者名称：{author}')
        # 视频保存路径
        save_dir = folder_name + '/' + author + '-' + mix_name
        self.create_folder(save_dir)
        for count in range(page):
            if not self.status_download:
                self.print_log('停止下载视频!')
                break
            # 传入url
            urls = "https://www.iesdouyin.com/web/api/mix/item/list/?mix_id=" + mid + "&count=10&cursor=" + str(
                count * 10)
            urls_resp = requests.get(url=urls, headers=headers, allow_redirects=False).json()
            curr_count = int(count) * 10
            list_size = len(urls_resp["aweme_list"])
            # 遍历每一个作品的URL
            for i in range(list_size):
                if not self.status_download:
                    self.print_log('停止下载视频!')
                    break
                curr_video = curr_count + int(i) + 1
                curr_resp = urls_resp["aweme_list"][i]
                # 视频标题
                video_name = f'第{curr_video}集-{curr_resp["desc"]}'
                video_name = video_name.replace('?', '').replace('\n', '').replace(':', '')
                if video_name == '':
                    video_name = '无名称视频' + curr_video
                self.print_log('开始下载 {}'.format(video_name))
                if len(video_name) > 200:
                    video_name = video_name[0: 200]
                    self.print_log('由于视频名称过长，避免下载失败，已缩短视频名称..')
                # 视频地址
                video_url = curr_resp["video"]["play_addr"]["url_list"][0]
                # 调用下载
                with open(video_name + '.mp4', 'wb') as v:
                    v.write(requests.get(url=video_url, headers=headers).content)
        self.print_log('下载任务已结束 :)')

    def download_playlet(self, response):
        mid = re.findall('detail/(.*?)/\?', response.headers['location'], re.M | re.I)[0]
        # 获取作品数
        page_url = "https://www.iesdouyin.com/web/api/playlet/detail/?playlet_id=" + mid
        page_resp = requests.get(url=page_url, headers=headers, allow_redirects=False).json()
        print(page_resp)
        count = int(page_resp["playlet_info"]["statis"]["updated_to_episode"])
        page = int(count / 10) + int(0 if count % 10 == 0 else 1)
        author = page_resp['playlet_info']['author']['nickname']
        playlet_name = page_resp['playlet_info']['playlet_name']
        self.print_log(f'准备下载短剧视频，短剧名称：{playlet_name}，视频总数：{count}，创建者名称：{author}')
        # 视频保存路径
        save_dir = folder_name + '/短剧-' + playlet_name + '-' + author
        self.create_folder(save_dir)
        for count in range(page):
            if not self.status_download:
                self.print_log('停止下载视频!')
                break
            # 传入url
            urls = "https://www.iesdouyin.com/web/api/playlet/item/list/?playlet_id=" + mid + "&count=10&cursor=" + str(
                count * 10)
            urls_resp = requests.get(url=urls, headers=headers, allow_redirects=False).json()
            curr_count = int(count) * 10
            list_size = len(urls_resp["aweme_list"])
            # 遍历每一个作品的URL
            for i in range(list_size):
                if not self.status_download:
                    self.print_log('停止下载视频!')
                    break
                curr_video = curr_count + int(i) + 1
                curr_resp = urls_resp["aweme_list"][i]
                # 视频标题
                video_name = f'第{curr_video}集-{curr_resp["desc"]}'
                video_name = video_name.replace('?', '').replace('\n', '').replace(':', '')
                if video_name == '':
                    video_name = '无名称视频' + curr_video
                self.print_log('开始下载 {}'.format(video_name))
                if len(video_name) > 200:
                    video_name = video_name[0: 200]
                    self.print_log('由于视频名称过长，避免下载失败，已缩短视频名称..')
                # 视频地址
                video_url = curr_resp["video"]["play_addr"]["url_list"][0]
                # 调用下载
                with open(video_name + '.mp4', 'wb') as v:
                    v.write(requests.get(url=video_url, headers=headers).content)
        self.print_log('下载任务已结束 :)')

    def print___(self):
        self.print_log('----------------------------------------------------')

    def print_log(self, log):
        logmsg_in = str(log) + "\n"
        self.tk_text_show.tag_config("odd", background='#ffffff')
        self.tk_text_show.insert('end', logmsg_in, 'odd')


if __name__ == "__main__":
    win = Win()
    # TODO 绑定点击事件或其他逻辑处理
    win.show()
