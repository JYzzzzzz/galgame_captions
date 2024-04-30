
# https://www.bilibili.com/video/BV16M411Y7rc/?vd_source=af3c46447034e1f89be315aaf6c3ddba
#   主要参考该视频。但该视频没给出headers中应包含的信息

# https://www.bilibili.com/video/BV14R4y1v7hn/?vd_source=af3c46447034e1f89be315aaf6c3ddba
#   本身讲得不好，但补充了上文视频中没有的内容


# 逆向步骤
# 1、多翻译几次，查看参数，发现有变化的只有sign和mystictime

# 2、处理sign：在全局搜索中找sign，找到一行 “sign: b(t, e),”，顺便找到了“mysticTime: t,”。

# 3、多翻译几次得到：
#   t: 1677250913731    e: "fsdsogkndfokasodnaso"
#   t: 1677251242694    e: "fsdsogkndfokasodnaso"
# 可知e是一个定值，t会变

# 密
import base64
import hashlib
from Crypto.Cipher import AES   # how to install: https://blog.csdn.net/zhinian1204/article/details/124112512

import os
import time
import random
import requests
import execjs
import json


user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'


def get_parameters_by_python(query, translate_from, translate_to):
    t = int(time.time() * 1000)
    ctx = f"client=fanyideskweb&mysticTime={t}&product=webfanyi&key=fsdsogkndfokasodnaso"
    obj = hashlib.md5()
    obj.update(ctx.encode("utf-8"))
    sign = obj.hexdigest()

    parameters = {
        'i': query,
        'from': translate_from,
        'to': translate_to,
        'dictResult': 'true',
        'keyid': 'webfanyi',
        'sign': sign,
        'client': 'fanyideskweb',
        'product': 'webfanyi',
        'appVersion': '1.0.0',
        'vendor': 'web',
        'pointParam': 'client,mysticTime,product',
        'mysticTime': t,
        'keyfrom': 'fanyi.web',
    }
    return parameters


def get_parameters_by_javascript(query, translate_from, translate_to):
    with open('youdao_encrypt.js', 'r', encoding='utf-8') as f:
        youdao_js = f.read()
    params = execjs.compile(youdao_js).call('get_params', query, user_agent)    # 通过 JavaScript 代码获取各个参数
    bv = hashlib.md5(user_agent.encode()).hexdigest()                           # 对 UA 进行 MD5 加密，生成 bv 值
    parameters = {
        'i': query,
        'from': translate_from,
        'to': translate_to,
        'smartresult': 'dict',
        'client': 'fanyideskweb',
        'salt': params['salt'],
        'sign': params['sign'],
        'lts': params['lts'],
        'bv': bv,
        'doctype': 'json',
        'version': '2.1',
        'keyfrom': 'fanyi.web',
        'action': 'FY_BY_REALTlME'
    }
    return parameters


def get_translation_result(parameters):
    translate_url = 'https://dict.youdao.com/webtranslate'

    headers = {
        'User-Agent': user_agent,
        # 'Host': 'fanyi.youdao.com',
        # 'Origin': 'https://fanyi.youdao.com',
        'Referer': 'https://fanyi.youdao.com/',
        # 'X-Requested-With': 'XMLHttpRequest',
        # 'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        'Cookie': '_ga=GA1.2.148556814.1646643432; OUTFOX_SEARCH_USER_ID_NCOO=1648918196.4647043; OUTFOX_SEARCH_USER_ID="439048465@10.110.96.160"; P_INFO=15895878191|1657426774|1|youdaonote|00&99|null&null&null#zhj&330200#10#0|&0|null|15895878191; UM_distinctid=1867ab06f321-0e1f1f26020cd9-a3e3164-100200-1867ab06f33498'
    }
    # cookie = {
    #     "OUTFOX_SEARCH_USER_ID": "-1551186736@196.168.60.5"
    # }
    response = requests.post(url=translate_url, headers=headers, data=parameters)
    # result = response.json()['translateResult'][0][0]['tgt']
    return response.text


def result_decode(result):
    decodekey = "ydsecret://query/key/B*RGygVywfNBwpmBaZg*WT7SIOUP2T0C9WHMZN39j^DAdaZhAnxvGcCY6VYFwnHl"
    decodeiv = "ydsecret://query/iv/C@lZe2YzHtZ2CYgaXKSVfsb7Y4QWHjITPPZ0nQp87fBeJ!Iv6v^6fvi2WN@bYpJ4"
    # obj = hashlib.md5()
    # obj.update(decodekey.encode("utf-8"))
    # decodekey = obj.hexdigest()
    decodekey = hashlib.md5(decodekey.encode("utf-8")).digest()
    decodeiv = hashlib.md5(decodeiv.encode("utf-8")).digest()
    aes = AES.new(decodekey, AES.MODE_CBC, decodeiv)
    ctx = aes.decrypt(base64.urlsafe_b64decode(result))   # 二进制格式翻译内容
    ctx = str(ctx, 'utf-8')
    # 得到的字符串结尾多出几个字符，导致不是正确的字典格式，为了转化为字典，需要修正
    i = 0
    for i in range(len(ctx)-1, 0, -1):
        if ctx[i] == '}':
            break
    ctx = ctx[0:i+1]
    # 转化为字典
    ctx = json.loads(ctx)
    # 获取最终文本
    text_ans = ''
    for item in ctx['translateResult'][0]:
        text_ans += item['tgt']
    return text_ans
    # print(decodekey)


def trans_text(text, lang_from, lang_to):
    param = get_parameters_by_python(text, lang_from, lang_to)
    result = get_translation_result(param)
    result = result_decode(result)

    # 保存
    file_path = "./cache/youdaofanyi_history/"
    if os.path.exists(file_path) == 0:
        os.makedirs(file_path)
    file_name = "TRANSres_" + time.strftime('%Y%m%d_%H%M%S') + ".txt"
    with open(file_path+file_name, "w", encoding="utf-8") as fp:
        fp.write(result)

    return result


def trans_test():
    # query = 'おはよう'

    query = 'どこかは判らない牧場で、白馬にまたがって走る感触を。大きな動物のやさしい体温を。'
    # result = '_jsUyA02rwkOJ4enKX7c4dhd7CjvGkcKfbRx0BjNGW9Lsnottep33ZRVNmlxdLnGxZ6kWZYO8f_-vbicViIgIJXdzR-YExcejkzUulRIMe9lHhKG8-tH88veoz231g9AG601PfBsoqulsycJwsDz2DJ7hIZjUoTIsvBk3GfdaA5XB9xHZbdc4yUbFrmXMKiihXs97L608FaUzOKcXR_nU7Yxq2gqTY0vTNCkLOxNdMnRIy5L5TmKWkTTy-n3Buj-j8p7pKHGKQZ2BQWHFdpbqtpnjenwtGxFaBvSClwxd1JTSLRORlhmuq0ZQB1v9ZalhY_UwHBzF71IpSwu8wJs8QiRfXENbQIXrMoLFtabgQlJyk0W3w46JbpPSbWMqIxW0Z72q17ogJAhClWR_5SE21cEpl5rgEtXNQC_BCWprb6o9wP7rlGOl0-6pyZW83zEOgvzWF9bJfErWxj5Y5ptIKozbVQBAj5sOq9ax6FgcYHaHLRK2Ng08z05bsXyHbrOHgVhrobblNUGoS_2LvDiYyv8K1vnsx7_rVUxSxhzctv6Y36vBJJ27k31MuJ8bgOWm_AD5HnmQDvOUH6sNcGVY6dHy9QFJzhId6Cb28g8zc_2A4UTEY7dWTKqoT6YL1ILoWJRZnCvEcf-l4bzTNWZw_pndKgQ9A4kI3OCDB801A_YPa-4m6wdAew8Kp0RnSZdZ3aqYEViozsgtPiU4dp4-Hef4fqyKYkrbW55vBnSaQfUlFjMtblPpWJGNu4bRqNkH2goH612BycJ5ZGcTB_0xN2aS60AY5PJFwOZRzHHlfptb7IAQx-ICvVlOMaXSnA7bDmGUDtF1DPA92ybfWYddVSqCVmK6kivVfooYXa88YHuAey1UoCCJQN8jn_SYAj0YiRm69QahL6RfXwIp7BuUYkGF3C1J9HMm2gSiB812aEiycv-HempMC5YbCoYcuqz7xE-iMuEaWgg_AUcgZUI0G9Wng7U0rTyyNj-hHBYDOUKH03ZebeeXbn9QtKWiuyC3EtjdpOZxQ4nquvWkd8L_aIcvaw1rCCTcoTNoLWHOoycc1DTel2Hccd3k5VlbDW9yaXjYRGWRtL_upGk4vLNFRkpnbR1q0vGTBc1Gzlo-ho3SKWI9tRNLdlmINuefMBTjsS8hI63xdTumu8RJgFUwRhFdXGRcFcXb5kJ4sOOsu8nHzvLkop1RQ28U_HfaYNKhuJ_EX_bDpelPn5x-o2-1YDtI5QmVB69SN9kJUQjp0M1GIVZ2wKTpty6lvjrQVJl5Nj4a-lC_KLrQLMwJ8jQOjoNIN8yo1ASx7bEwNZgJ7w8uSXxD43XEIKYEMUWYFt75zgjxP4Ec0c1ZNpOEdDKl6FEqj5iswrijsMU_A9rYgSqpJPGQI2Yj8AdiIMLLqZN7ryuucI60AS39FQA12ft393tG-I2f90pIlJP4miKhhIe14m0KqDkwmW76RaI2qRWbwdcBVIkDLMs_INw7krPE9ZVUSaD8CqHKxFmao-FVSMq7n545NXxSFmUuc4_UpNq3X4iO5K-Xg9Hd90_QZBrLB2ry7hIvDghB1L-WYX7T40='

    # query = 'good'

    # 原始语言，目标语言，默认自动处理
    translate_from = 'ja'    # 'zh-CHS' 'en' 'ja'
    translate_to = 'zh-CHS'
    # 通过 Python 获取加密参数或者通过 JavaScript 获取参数，二选一
    param = get_parameters_by_python(query, translate_from, translate_to)
    # param = get_parameters_by_javascript(query, translate_from, translate_to)
    result = get_translation_result(param)
    # print('翻译的结果为：', result)
    result = result_decode(result)
    print(result)


if __name__ == '__main__':
    trans_test()    # ok 2306
    # result_decode()
    # with open('test.txt', "a", encoding="utf-8") as fp:
    #     fp.write('\n\n'+'a')
    #
    # with open('test.txt', "a", encoding="utf-8") as fp:
    #     fp.write('\n'+'b')

