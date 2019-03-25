# coding: utf-8

import re
import math
import time
import codecs
import base64
import random
import requests
from Crypto.Cipher import AES
from bs4 import BeautifulSoup as bs

__base_str = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
__gain = len(__base_str)


def __GetRandomStr(length):
    '''生成长度为 length 的随机字符串, 对应 js 脚本中的 function a(a) '''

    random_strs = ""
    for i in range(length):
        e = math.floor(random.random() * __gain)
        random_strs = random_strs + __base_str[e]

    return random_strs


__iv = '0102030405060708'  # 用来加密或者解密的初始向量(必须是16位)


def __AESEncrypt(msg, key):
    ''' AES 加密函数，对应于 js 脚本中的 function b(a, b) '''

    # 如果信息的长度不是16的倍数则进行填充(paddiing)
    padding = 16 - len(msg) % 16
    # 这里使用padding对应的单字符进行填充
    msg = msg + padding * chr(padding)

    cipher = AES.new(key.encode(), AES.MODE_CBC, __iv.encode())
    # 加密后得到的是bytes类型的数据
    encryptedbytes = cipher.encrypt(msg.encode())
    # 使用Base64进行编码,返回byte字符串
    encodestrs = base64.b64encode(encryptedbytes)
    # 对byte字符串按utf-8进行解码
    enctext = encodestrs.decode('utf-8')

    return enctext


def __RSAEncrypt(randomstrs, key, f):
    ''' RSA 加密，对应 js 脚本中的 function c(a, b, c) '''
    # 随机字符串逆序排列
    string = randomstrs[::-1]
    # 将随机字符串转换成byte类型数据
    text = bytes(string, 'utf-8')
    seckey = int(codecs.encode(text, encoding='hex'),
                 16)**int(key, 16) % int(f, 16)
    # 返回整数的小写十六进制形式
    return format(seckey, 'x').zfill(256)


__e = '010001'
__f = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
__g = '0CoJUm6Qyw8W8jud'


def __GetPostData(rid, page):
    ''' 获得 POST 请求报文中 params 和 encSecKey 的值，对应 js 脚本中的 window.asrsea() 函数

    :param rid: 专辑的id
    :type rid: str

    :param page: 要访问的评论所在的页数
    :type page: int
    '''
    d = '{"rid":"R_AL_3_' + rid + '","offset":' + \
        str((page-1) * 20) + ',"total":"false","limit":"20","csrf_token":""}'

    # 1. 生成长度为16的随机字符串
    temp1 = __GetRandomStr(16)
    # 2. 第一次 AES 加密
    enctext = __AESEncrypt(d, __g)
    # 3. 第二次 AES 加密后得到 params 的值
    encText = __AESEncrypt(enctext, temp1)
    # 4. 进行 RSA 加密后得到 encSecKey 的值
    encSecKey = __RSAEncrypt(temp1, __e, __f)

    return encText, encSecKey


__comments_header = {'Accept': '*/*',
                     'Accept-Encoding': 'gzip, deflate, br',
                     'Accept-Language': 'zh-CN,zh;q=0.9',
                     'Connection': 'keep-alive',
                     'Cookie': '_iuqxldmzr_=32; _ntes_nnid=9754eb807c09ed088696d18d9c6adeea,1547206072247; _ntes_nuid=9754eb807c09ed088696d18d9c6adeea; WM_TID=yU27lmrox1hEBQURRQN8hOZp9ijAnMyT; WM_NI=1MmoLZ%2FVibH0tKR73s3pAkWWEluYKGkk3n7l1eLYQlBhxkYmxEj2s3EGZlEZTjkNaLUcW8Q027kpAiTAY5StIWe1WxOZOuZtI8jO4bgpBaa4qqT2TIjUTjHbLGFOcIbRVTY%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6eea4d879fc8d96b8cc4aa3928ab7d44f968a9aaef368f1aa00d0b26da2b4848fc22af0fea7c3b92af393a390cf52ed8aa783cb3cb8959ed8b279f1b08f8cd65d87b4bbbaca4da9b5fd8fb668f3bb84bad46882b8b88cdc67bc9ba6d3f2398799968dc85298b6a5afe44897bd99d9d43cf2e9a591c463989f97d6d2808b89abd2d6748d868196d9808be8a6b0b76aa5b08e82e440b3af9cd3d743aa8b9c8bcb6a90998ab0e243a28e9ab5dc37e2a3; JSESSIONID-WYYY=WKXC2UPEwf6tSxayB5Yhx96FVfSIEY2%2FSDYd2ssirYn1dRUqJj3zNUJXxFC6VakvoJNSNhTED6tZY1yBBrcniYqix7hz5tFSm9Emwc0N5Z9ZfRWqpHvnWRxK2JjE8xF3Qpj29ndmK%2FhW4WXlFweaZGnKAB1MjIXTCZ7xX2DHU7OrA15V%3A1552626465106',
                     'Host': 'music.163.com',
                     'Origin': 'https://music.163.com',
                     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}


def GetAlbumComments(album_id, page):
    ''' 获取音乐专辑第 page 页的评论，爬取成功时返回json格式的评论

    :param album_id: 专辑的id
    :type album_id: string    e.g. album_id = '34735139'

    :param page: 评论所在的页数
    :type page: int
    '''

    url = 'https://music.163.com/weapi/v1/resource/comments/R_AL_3_' + album_id + '?csrf_token='
    params, encSecKey = __GetPostData(album_id, page)
    data = {'params': params, 'encSecKey': encSecKey}

    receive = requests.post(url, headers=__comments_header, data=data)
    receive.encoding = 'utf-8'

    if receive.status_code == 200:
        return receive.json()
    else:
        raise Exception('status code error')


def GetSongComments(song_id, page):
    ''' 获取歌曲第 page 页的评论，爬取成功时返回json格式的评论，否则返回 None

    :param song_id: 歌曲的id
    :type song_id: string    eg. song_id = '28563317'

    :param page: 评论所在的页数
    :type page: int
    '''

    url = 'https://music.163.com/weapi/v1/resource/comments/R_SO_4_' + song_id + '?csrf_token='
    params, encSecKey = __GetPostData(song_id, page)
    data = {'params': params, 'encSecKey': encSecKey}

    receive = requests.post(url, headers=__comments_header, data=data)
    receive.encoding = 'utf-8'

    if receive.status_code == 200:
        return receive.json()
    else:
        raise Exception('status code error')


__info_header = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                 'Accept-Encoding': 'gzip, deflate, br',
                 'Accept-Language': 'zh-CN,zh;q=0.9',
                 'Connection': 'keep-alive',
                 'Cookie': '_ntes_nnid=5f4831327d9789cbfe056803d13f64c4,1531652809772; _ntes_nuid=5f4831327d9789cbfe056803d13f64c4; _iuqxldmzr_=32; __utmz=94650624.1532529363.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); WM_TID=q86IKojnv4QEPh3PyXpI16Gka4c%2Bi%2FrH; JSESSIONID-WYYY=wDWR1CxZYGluue%2FMo7F%2Bnxqv6VP909SoW2joXe%2FJErZJo6mRvaef61VhViqnQQ%2FsyEFFfjNZXBl9NvZ3%2FiVwX%2Ft63%2FRkIbXpcjG2QvK9dDxEWFwHG7Xnuoy%2F5FdnN71mpxCjpPq1VG2aT9hcTblGO%2BtrA9E6E5zdkeP%2FR8YOgSworCND%3A1535643619089; __utma=94650624.346451733.1532529363.1532529363.1535641819.2; WM_NI=Hczth2LAmyzBtly6iI9dLS9B3vg6RL8KN0ZnivlX55%2FoGlp9FkNMyPCGs0NKdACXl5tBirbqrEaMPwlB0iCoA%2BxxoXgpBca9RoYpHvh%2BDWj5aSyIs0SaXWp0EGJTCqAneFc%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6ee87d46bf2f08f86e57eb7f0a3b7e2599ba99ab3c1409bea8da6f14bfc88a690f22af0fea7c3b92a8cbdb695eb3a909fa39af94ab8b4b7d7ec43fbbc84b4bc4af1aaa9d7d148fc9582d1d966abaaa4b9b83fedb1898df33386b582aefc5c8199bdd1cd41a89f8db9ef3fb89ea793e17bb29bafaed37db09e008ac26583f5b899ee54a5b08e84e43392b19791cb7eacf58cb8e93fa38db7aaf23c91bf98b8f33c879986b5c27b83b2aba7e237e2a3; f_=1542288996123',
                 'Host': 'music.163.com',
                 'Referer': 'https://music.163.com',
                 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}


def GetAlbumInfo(album_id):
    """获取音乐专辑的信息

    :param `album_id`: 音乐专辑的id
    :type `album_id`: string    e.g. album_id = '34735139'

    :return info_dic = `{'name':'', 'cnt_comment':0, 'songs':{}};`
    """
    info_dic = {'name':'', 'cnt_comment':0, 'songs':{}};
    url = 'https://music.163.com/album?id=' + album_id

    ini_info = requests.get(url, headers=__info_header)
    page = bs(ini_info.text, 'lxml')

    #debug
    # with open('test.html', 'w', encoding='utf-8') as f:
    #     f.write(page.prettify())

    '''获取专辑名'''
    info_dic['name'] = page.find('h2', "f-ff2").get_text()

    '''获取专辑内的歌曲名及其id'''
    song_list = page.find('div', id='song-list-pre-cache')

    for song in song_list.find_all('a'):

        song_name = song.get_text().split()  # 用空格代替歌曲名中'\xa0'
        song_name = " ".join(song_name)

        info_dic['songs'][song_name] = song.get('href')[9:]

    '''获取专辑的总评论数目'''
    info_dic['cnt_comment'] = int((page.find(id='cnt_comment_count')).get_text())

    return info_dic



def GetAlbumId(singer_id):
    """根据歌手的 id 爬取该歌手的所有专辑的id，爬取成功返回专辑 album_list    e.g. album_list = {'海胆&谁来剪月光': '35835294', ... }

    :param singer_id: 歌手的id
    :type singer_id: string    e.g. singer_id = '2116'
    """
    ini_url = 'https://music.163.com/artist/album?id=' + singer_id + '&limit=12&offset='
    offset = 0
    album_list = {}

    while True:
        url = ini_url + str(offset)
        album_page = requests.get(url, headers=__info_header)

        album_page = bs(album_page.text, 'lxml')
        album_info = album_page.find_all("a", "tit s-fc0")

        for i in album_info:
            album_name = i.get_text().split()
            album_name = " ".join(album_name)
            album_list[album_name] = i.get('href')[10:]

        #if album_page.find("a", "zbtn znxt js-disabled"):
        if not album_page.find("a", "zbtn znxt"):
            break

        offset = offset + 12

    return album_list


__year_now = time.time()//(3600*24*365)


def GetUserInfo(user_id):
    """ 爬取用户的 性别、地区、年龄等信息

    :param user_id: 用户的id (e.g. '486963791')
    :type user_id: string

    :return gender: 用户性别 0表示保密 1表示男性 2表示女性
    :type gender: int

    :return area: 用户所在地（若用户无此信息，则返回 None）
    :type area: string

    :return age: 用户年龄（若用户无此信息，则返回 None）
    :type age: int
    """
    url = 'https://music.163.com/user/home?id=' + user_id

    ini_info = requests.get(url, headers=__info_header)
    info = ini_info.text

    '''获取性别'''
    gender_pattern = re.compile('<i class="icn u-icn u-icn-0(\d+)">')
    gender = re.search(gender_pattern, info)
    if gender:
        gender = int(gender.group(1))
    else:
        gender = None

    '''获取地址'''
    location_pattern = re.compile('<span>所在地区：(.+?)</span>')
    location = re.search(location_pattern, info)
    if location:
        location = location.group(1)
    else:
        location = None

    ''' 获取年龄'''
    age_pattern = re.compile(r'<span.*?data-age="(\d+)">')
    age = re.search(age_pattern, info)
    if age:
        age = int(age.group(1))//(3600*24*365*1000)
        age = int(__year_now - age)
    else:
        age = None

    return gender, location, age

