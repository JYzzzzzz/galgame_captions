# coding=utf-8
# 技术文档：https://cloud.baidu.com/doc/OCR/s/1k3h7y3db

import sys
import json
import base64
import time
import os

# 保证兼容python2以及python3
IS_PY3 = sys.version_info.major == 3
if IS_PY3:
    from urllib.request import urlopen
    from urllib.request import Request
    from urllib.error import URLError
    from urllib.parse import urlencode
    from urllib.parse import quote_plus
else:
    import urllib2
    from urllib import quote_plus
    from urllib2 import urlopen
    from urllib2 import Request
    from urllib2 import URLError
    from urllib import urlencode

# 防止https证书校验不正确
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

API_KEY = ''
SECRET_KEY = ''

OCR_URL = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic"

"""  TOKEN start """
TOKEN_URL = 'https://aip.baidubce.com/oauth/2.0/token'


def fetch_token():
    """
        获取token
    """
    params = {'grant_type': 'client_credentials',
              'client_id': API_KEY,
              'client_secret': SECRET_KEY}
    post_data = urlencode(params)
    if IS_PY3:
        post_data = post_data.encode('utf-8')
    req = Request(TOKEN_URL, post_data)
    try:
        f = urlopen(req, timeout=5)
        result_str = f.read()
    except URLError as err:
        print(err)
    if IS_PY3:
        result_str = result_str.decode()

    result = json.loads(result_str)

    if 'access_token' in result.keys() and 'scope' in result.keys():
        if not 'brain_all_scope' in result['scope'].split(' '):
            print('please ensure has check the  ability')
            exit()
        return result['access_token']
    else:
        print('please overwrite the correct API_KEY and SECRET_KEY')
        exit()


def read_file(image_path):
    """
        读取文件
    """
    f = None
    try:
        f = open(image_path, 'rb')
        return f.read()
    except:
        print('read image file fail')
        return None
    finally:
        if f:
            f.close()


def request(url, data):
    """
        调用远程服务
    """
    req = Request(url, data.encode('utf-8'))
    has_error = False
    try:
        f = urlopen(req)
        result_str = f.read()
        if IS_PY3:
            result_str = result_str.decode()
        return result_str
    except URLError as err:
        print(err)


def get_ocr_text(img_dir, lang_type):
    """
    JYZ 编写便于调用
    :param img_dir:
    :param lang_type: CHN_ENG, JAP
    :return:
    """

    # 获取access token
    token = fetch_token()

    # 拼接通用文字识别高精度url
    image_url = OCR_URL + "?access_token=" + token

    text = ""

    # 读取测试图片
    file_content = read_file(img_dir)

    # 生成url data
    url_data = {
        'image': base64.b64encode(file_content),
        'language_type': lang_type
    }

    # 调用文字识别服务
    result = request(image_url, urlencode(url_data))

    # 解析返回结果
    result_json = json.loads(result)       # 按行存储
    for words_result in result_json["words_result"]:
        text = text + words_result["words"]  # 换行连贯

    # 保存
    file_path = "./cache/baiduOCR_history/"
    if os.path.exists(file_path) == 0:
        os.makedirs(file_path)
    file_name = "OCRres_" + time.strftime('%Y%m%d_%H%M%S') + ".json"
    with open(file_path+file_name, "w", encoding="utf-8") as fp:
        json.dump(result_json, fp, ensure_ascii=False, indent=4)

    return result_json, text


if __name__ == '__main__':

    # 调用
    dd, tt = get_ocr_text(r'特殊范围文本.png', 'JAP')
        # 每月有免费额度，不要轻易调用
    print(dd)
    print(tt)
