#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
MIT License

Copyright (c) 2019 Maemo8086, MikoSec

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import os
import random
import requests
import sys
import time
from bs4 import BeautifulSoup


def download(file_url, path, filename):  # 下载函数
    global download_exception

    print()
    print(f'\r[Downloading] Path => {path}\tFile Name => {filename}')
    sys.stdout.flush()

    delay = False

    if delay:
        wait = round(random.uniform(0, 5), 2)
        print(f'\r[Info] Waiting {wait} seconds...')
        sys.stdout.flush()
        time.sleep(wait)

    start = time.time()  # 开始时间

    if not os.path.exists(path):
        os.makedirs(path)
    if path[-1] != os.sep:
        path += os.sep
    full_path = path + filename

    try:
        response = requests.get(file_url, stream=True, timeout=30)
    except:
        response.close()
        download_exception.append((file_url, path, filename))
        print(f'\r[Error] Download request for *{filename}* has failed.')
        return

    if response.status_code != 200:
        response.close()
        download_exception.append((file_url, path, filename))
        print(
            f'\r[Error] Download request for *{filename}* has failed.\tStatus Code => {response.status_code}')
        return

    chunk_size = 512
    content_size = int(response.headers['content-length'])
    print('[File Size] %0.2f MB' % (content_size / 1024 ** 2))
    sys.stdout.flush()

    if os.path.exists(full_path):
        if os.path.getsize(full_path) == content_size:  # 判断文件大小
            response.close()
            print('[Info] Same sized file exists, skipping...')
            return
        else:
            print('[Warning] Overwriting existing copy.')

    size = 0
    try:
        with open(full_path, 'wb') as f:
            for data in response.iter_content(chunk_size):
                f.write(data)
                size += len(data)
                print(
                    '\r[Downloading] %s>%.2f%%' % (
                        '=' * int(size * 50 / content_size), float(size / content_size * 100)), end='')
    except:
        download_exception.append((file_url, path, filename))
        if os.path.exists(full_path):
            os.remove(full_path)
        print(f'\r[Error] Download *{filename}* has failed.')
        return
    finally:
        response.close()
        end = time.time()  # 结束时间
        print('\rTime elapsed: %.2fs' % (end - start))


def recursive_fetch(soup, part_url):
    global url

    for i in soup.find_all('td', class_='link')[1:]:  # 获取文件或目录
        if i.text[-1] != '/':
            path = part_url[len(url):]
            filename = i.text
            file_url = part_url + filename
            download(file_url, path, filename)
        else:
            dir_url = part_url + i.text
            print()
            print(f'\r[Info] Searching under {dir_url}.')

            execute = True
            while execute:
                wait = round(random.uniform(0, 5), 2)
                print(f'\r[Info] Waiting {wait} seconds...')
                sys.stdout.flush()
                time.sleep(wait)

                execute = False
                try:
                    with requests.get(dir_url, timeout=30) as req:
                        req.encoding = req.apparent_encoding
                        soup1 = BeautifulSoup(req.text, 'lxml')
                except:
                    execute = True
                    print(f'\r[Error] URL request *{dir_url}* has failed, retrying...')

            recursive_fetch(soup1, dir_url)


def main():
    global url
    global download_exception

    display = [
        'Python 爱盘抓盘工具',
        '',
        '作者： Maemo8086，MikoSec',
        '源码： https://github.com/Maemo8086/Python_AiPan_Crawler',
        '',
        '一款基于Python 的吾爱破解论坛爱盘下载工具',
        '本工具使用Python3，requests库，(BeautifulSoup4) bs4库以及lxml库，',
        '建议使用前先修改User Agent 一栏。'
    ]

    for row in display:
        print(row.center(80))

    directory = 'AiPan'
    if not os.path.exists(directory):
        os.mkdir(directory)
    os.chdir(directory)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77me/77.0.3865.120 Safari/537.36'}

    try:
        with requests.get(url, headers=headers, timeout=30) as req:
            req.encoding = req.apparent_encoding
            soup = BeautifulSoup(req.text, 'lxml')
    except:
        print(f'\r[Error] URL request *{url}* has failed.')
        return

    recursive_fetch(soup, url)

    while download_exception:
        print()
        print(f'\r[Info] Retrying {len(download_exception)} failed downloads...')

        for file_url, _ in download_exception:
            print(f'\r\t File URL => {file_url}')

        wait = round(random.uniform(10, 30), 2)
        print()
        print(f'\r[Info] Waiting {wait} seconds...')
        sys.stdout.flush()
        time.sleep(wait)

        download_exception_copy = download_exception
        download_exception.clear()
        while download_exception_copy:
            download(*download_exception_copy.pop())


url = 'https://down.52pojie.cn/'  # 爱盘 URL

download_exception = list()
main()
