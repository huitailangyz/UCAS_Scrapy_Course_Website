# -*- coding:utf8 -*-

import requests
from bs4 import BeautifulSoup
import os


def recursion_download(course_name, dir_name, url, session):
    res = session.get(url, headers=HEADERS)
    html = res.content.decode('utf-8')
    soup = BeautifulSoup(html, "html.parser")
    items = soup.find_all('li')[1:]
    if not items:
        return
    now_dir = os.path.join(".", dir_name)
    os.makedirs(now_dir, exist_ok=True)
    exist_files = os.listdir(now_dir)
    for item in items:
        file = item.find('a')
        file_url = url + file['href']
        file_name = file.text
        if 'file' in item['class']:
            file_type = file_url.split('.')[-1]
            if not file_name.endswith(file_type):
                file_name = file_name+'.'+ file_type.lower()
            table_1 = str.maketrans('<>:*?', '《》：×？')
            table_2 = str.maketrans({key: None for key in '/\|"'})
            file_name = file_name.translate(table_1).translate(table_2)
            if file_name not in exist_files:
                try:
                    save_path = os.path.join(now_dir, file_name)
                    with open(save_path, "wb") as f:
                        res = session.get(file_url, headers=HEADERS)
                        f.write(res.content)
                    print(course_name, file_name, "下载成功")
                except:
                    print(course_name, file_name, "下载失败")
        elif 'folder' in item['class']:
            recursion_download(course_name, os.path.join(dir_name, file_name), file_url, session)
        else:
            pass


if __name__ == '__main__':
    try:
        config = open("user.txt")
        line = config.readlines()
        username = line[0].strip()
        password = line[1].strip()
        config.close()
    except:
        username = input("输入用户名: ")
        password = input("输入密码: ")

    HEADERS = {'user-agent': 'Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14', }
    url_login = "http://sep.ucas.ac.cn/slogin?userName=" + username + "&pwd=" + password + "&sb=sb&rememberMe=1"
    url_site = "http://sep.ucas.ac.cn/portal/site/16/801"
    course_site = "http://course.ucas.ac.cn/access/content/group/"

    # login in
    session = requests.Session()
    res = session.get(url_login, headers=HEADERS)
    html = res.content.decode('utf-8')
    soup = BeautifulSoup(html, "html.parser")
    nameTag = soup.find("li", {"class": "btnav-info", "title": "当前用户所在单位"})
    location, name = nameTag.text.strip().split()

    # jump to site
    res = session.get(url_site, headers=HEADERS)
    html = res.content.decode('utf-8')
    soup = BeautifulSoup(html, "html.parser")

    newUrl = soup.find("noscript").meta.get("content")[6:]
    res = session.get(newUrl)
    html = res.content.decode('utf-8')
    soup = BeautifulSoup(html, "html.parser")

    # choose the id
    now_id = soup.find('div', class_='Mrphs-userNav__submenuitem--displayid').text.strip()
    new_url = None
    user_profiles = soup.find_all('li', class_="Mrphs-userNav__submenuitem")
    for user_profile in user_profiles:
        item = user_profile.find('a')
        if not item:
            continue
        text = item.text.strip()
        if text.startswith("20") and len(text) == 15:
            new_id = text
            new_url = "http://course.ucas.ac.cn" + item["href"]
            break
    if new_url and now_id < new_id:
        res = session.get(new_url)
        html = res.content.decode('utf-8')
        soup = BeautifulSoup(html, "html.parser")

    url_my_course = soup.find('a', title="我的课程 - 查看或加入站点")['href']
    res = session.get(url_my_course, headers=HEADERS)
    html = res.content.decode('utf-8')
    soup = BeautifulSoup(html, "html.parser")
    courses = soup.find_all('th', headers="worksite")
    for course in courses:
        item = course.find('a')
        course_name = item.text[:-7]
        course_url = item['href']
        course_id = course_url.split('/')[-1]
        course_url = course_site + course_id + '/'
        recursion_download(course_name, course_name, course_url, session)

    os.system("pause")
    exit()