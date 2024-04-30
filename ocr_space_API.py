
# ocr service from: http://ocr.space/OCRAPI
# code from: https://github.com/Zaargh/ocr.space_code_example/blob/master/ocrspace_example.py

# use your email to get a APIKEY:
OCR_SPACE_API_KEY = ""

import requests


def ocr_space_file(filename, overlay=False, api_key='helloworld', language='eng'):
    """ OCR.space API request with local file.
        Python3.5 - not tested on 2.7
    :param filename: Your file path & name.
    :param overlay: Is OCR.space overlay required in your response.
                    Defaults to False.
    :param api_key: OCR.space API key.
                    Defaults to 'helloworld'.
    :param language: Language code to be used in OCR.
                    List of available language codes can be found on https://ocr.space/OCRAPI
                    Defaults to 'en'.
    :return: Result in JSON format.
    """

    payload = {'isOverlayRequired': overlay,
               'apikey': api_key,
               'language': language,
               }
    with open(filename, 'rb') as f:
        r = requests.post('https://api.ocr.space/parse/image',
                          files={filename: f},
                          data=payload,
                          )
    return r.content.decode()


def ocr_space_url(url, overlay=False, api_key='helloworld', language='eng'):
    """ OCR.space API request with remote file.
        Python3.5 - not tested on 2.7
    :param url: Image url.
    :param overlay: Is OCR.space overlay required in your response.
                    Defaults to False.
    :param api_key: OCR.space API key.
                    Defaults to 'helloworld'.
    :param language: Language code to be used in OCR.
                    List of available language codes can be found on https://ocr.space/OCRAPI
                    Defaults to 'en'.
    :return: Result in JSON format.
    """

    payload = {'url': url,
               'isOverlayRequired': overlay,
               'apikey': api_key,
               'language': language,
               }
    r = requests.post('https://api.ocr.space/parse/image',
                      data=payload,
                      )
    return r.content.decode()


def ocr_space_get_text(filename, lang):
    # lang: japanese(jpn)
    result = ocr_space_file(filename=filename, api_key=OCR_SPACE_API_KEY, language=lang)
    #print(result)
    #print(XXXXXX)
    """  example, a string with json format
    {
        "ParsedResults":[{
            "TextOverlay":{
                "Lines":[],
                "HasOverlay":false,
                "Message":"Text overlay is not provided as it is not requested"
            },
            "TextOrientation":"0",
            "FileParseExitCode":1,
            "ParsedText":"どこかは判らない牧場で、白馬にまたがって走る感触を。\r\n大きな動物のやさしい体温を。\r\n",
            "ErrorMessage":"",
            "ErrorDetails":""
        }],
        "OCRExitCode":1,
        "IsErroredOnProcessing":false,
        "ProcessingTimeInMilliseconds":"328",
        "SearchablePDFURL":"Searchable PDF not generated as it was not requested."
     }
    """
    false = False    # correct the format of dict for eval()
    result_text = eval(result)["ParsedResults"][0]["ParsedText"]
    result_text = result_text.replace("\n", "").replace("\r", "")
    return result_text


if __name__ == '__main__':
    # 该ocr的日语识别准确率要在图片二值化后才会较高
    # text = ocr_space_get_text('OCR_image_last.png', 'jpn')
    text = ocr_space_get_text(r"C:\Users\pc\Desktop\new_path\微信图片_20231213174124.png", 'eng')
    print(text)
    # Use examples:
    # test_url = ocr_space_url(url='http://i.imgur.com/31d5L5y.jpg')
    # test_file = ocr_space_file(filename='OCR_image_test.png', api_key=OCR_SPACE_API_KEY, language='jpn')
    # print(test_file)
