
import sys
import time
import matplotlib.pyplot as plt
import win32gui
import win32con
import argparse
import json

import show_text
import mouse
import picture_operation as picop
import baiduOCRAPI
import ocr_space_API
import youdaofanyi_2023 as youdaofanyi

"""
手动调用后
1、截图，裁剪
2、调用在线OCR，得到文字
3、调用在线翻译，得到中文
4、在屏幕上显示中文。
"""


def ocr_manual_correction(lang_list, text, rep_map):
    textout = text
    changed = 0
    if "ja" in lang_list:
        for r in rep_map:
            textout = textout.replace(*r)
    if textout != text:
        changed = 1
    return textout, changed


print("grogram start")
WID = 0
HEI = 1
WINtop = 0
WINbut = 1
WINlef = 2
WINrig = 3

parser = argparse.ArgumentParser()
parser.add_argument('--win', type=str, default="[618, 740, 230, 1040]",
                    help="window position when mouse move to top-left. "
                         "[top, button, left, right] offset to top-left of the screen.")
parser.add_argument('--win2', type=str, default="[115, 672, 230, 1100]",
                    help="window position when mouse move to 笔记本盖左侧突起下方. ")
parser.add_argument('--ocr', type=str, default='api_baidu',
                    help="which ocr. {'api_baidu', 'py_easyocr', 'api_ocr_space'}")
parser.add_argument('--gamename', type=str, default='',
                    help="name of game, for text record classify")
parser.add_argument('--img_op', type=str, default='black_white',
                    help="image operation. {'gray', 'black_white'}")
args = parser.parse_args()
args.win = eval(args.win)
args.win2 = eval(args.win2)

if args.ocr.find('api_ocr_space') >= 0:
    with open("./cache/ocrspace_record/ocrspace_jpn_correction.json", 'r', encoding='UTF-8') as f:
        ocrspace_REP_RULE = eval(f.read())
        # print("ocrspace_REP_RULE = {}".format(ocrspace_REP_RULE))

if args.ocr.find('py_easyocr') >= 0:
    print("import easyocr")
    import easyocr
    # ocr_reader = easyocr.Reader(['ja', 'en'], gpu=False,
    #             model_storage_directory='./cache/easyocr_record/model',
    #             user_network_directory='./cache/easyocr_record/user_network',
    #             recog_network='japanese_g2')
    ocr_reader = easyocr.Reader(['ja', 'en'], gpu=False,
                 model_storage_directory=None,
                 user_network_directory=None,
                 recog_network='japanese_g2')
    with open("./cache/easyocr_record/easyocr_error_correction.json", 'r', encoding='UTF-8') as f:
        easyocr_REP_RULE = eval(f.read())
        # print(easyocr_REP_RULE)

show_text.pygame_init()
caption_task_flag = 0
text_record_file = "./game_text_record/text_record_{}.txt".format(args.gamename)

# time.sleep(3)
# print(show_text.get_hwnd_title_list())
# hwnd = win32gui.FindWindow(None, "杺朄彮彈徚栒愴慄AnotherRecord")
# win32gui.ShowWindow(hwnd, win32con.SW_SHOW)

print("waiting ...")
show_text.show_text("【程序已开始】", duration=3)
while 1:    # loop
    time.sleep(0.2)

    mouse_pos = mouse.get_mouse_pos()
    if mouse_pos[WID] < 10 and mouse_pos[HEI] > 767-10:   # 鼠标移动到左下角退出程序
        show_text.show_text("【程序退出中】", duration=2)
        break
    if mouse_pos[WID] < 10 and mouse_pos[HEI] < 10:   # 鼠标移动到左上角，触发字幕显示
        time.sleep(0.5)
        mouse_pos = mouse.get_mouse_pos()
        if mouse_pos[WID] < 10 and mouse_pos[HEI] < 10:
            caption_task_flag = 1
    # if 295 < mouse_pos[WID] < 340 and mouse_pos[HEI] < 10:
    #     # 鼠标移动到上方，左侧突起下方。触发字幕显示，窗口位置为[115, 672, 230, 1100]
    #     time.sleep(0.5)
    #     mouse_pos = mouse.get_mouse_pos()
    #     if 295 < mouse_pos[WID] < 340 and mouse_pos[HEI] < 10:
    #         caption_task_flag = 2
    if 670 < mouse_pos[WID] < 700 and mouse_pos[HEI] < 10:
        # 鼠标移动到正上方，摄像头下方。触发字幕显示，窗口位置自定义
        time.sleep(0.5)
        mouse_pos = mouse.get_mouse_pos()
        if 670 < mouse_pos[WID] < 700 and mouse_pos[HEI] < 10:
            caption_task_flag = 3

    # -------------------- 触发 识别+翻译
    if caption_task_flag:

        # ---------- screenshot
        img = picop.screen_cap()                # 全屏截图
        if caption_task_flag == 1:
            win_pos = args.win
        elif caption_task_flag == 2:
            win_pos = args.win2
        elif caption_task_flag == 3:
            win_pos = [0, 0, 0, 0]
            show_text.show_text("【自定义窗口，将鼠标移动到窗口左上角，5秒后扫描鼠标位置】", duration=5)
            mouse_pos = mouse.get_mouse_pos()
            win_pos[WINtop] = mouse_pos[HEI]
            win_pos[WINlef] = mouse_pos[WID]
            show_text.show_text("【自定义窗口 Step2，将鼠标移动到窗口右下角，5秒后扫描鼠标位置】", duration=5)
            mouse_pos = mouse.get_mouse_pos()
            win_pos[WINbut] = mouse_pos[HEI]
            win_pos[WINrig] = mouse_pos[WID]
            print("自定义窗口：{}".format(win_pos))
        img = img[win_pos[WINtop]:win_pos[WINbut], win_pos[WINlef]:win_pos[WINrig], 0:3]
        # ^^^ cut image. offset to left-top of the screen.
        # ^^^ [top:button, left:right, 0:3]
        if args.img_op.find('black_white') >= 0:
            _, img = picop.image_rgb2bw(img)  # 黑白图字有点小时，baiduOCR的准确率会下降
        elif args.img_op.find('gray') >= 0:
            _, img = picop.image_rgb2gray(img)
        # img_ocr = plt.imread("OCR_image_last.png")  # 读取上一个ocr图片
        # img_ocr = img_ocr[:, :, 0:3]
        # im_simi = picop.get_image_similarity(img, img_ocr)  # 比较图片相似度

        if 0:    # for test
        # if im_simi <= 0.01:
            print("ocr stopped because no difference in images")
            show_text.show_text("【OCR中断。与上一张图片相同】", duration=3)
        else:
            img_name_time = time.strftime('IMG_%Y%m%d_%H%M%S.png')
            plt.imsave("./cache/OCR_image_last.png", img)              # 保存新的OCR缓存图
            plt.imsave("./game_text_record/text_images/{}".format(img_name_time), img)  # 图片永久保存
            print('{}, img_op={}'.format(img_name_time, args.img_op))
            with open(text_record_file, "a", encoding="utf-8") as file_text_record:
                file_text_record.write('\n\n{}, img_op={}'.format(img_name_time, args.img_op))

            # ---------- OCR
            text_ch = ""
            text_ja_good = None   # to test the performance of other ocr

            if args.ocr.find('api_baidu') >= 0:
                _, text_ja_baidu = baiduOCRAPI.get_ocr_text("OCR_image_last.png", "JAP")  # 调用OCR
                print("BaiduOcr: {}".format(text_ja_baidu))
                with open(text_record_file, "a", encoding="utf-8") as file_text_record:
                    file_text_record.write('\n' + 'BaiduOcr: '+text_ja_baidu)
                text_ja = text_ja_baidu
                text_ja_good = text_ja_baidu   # to test the performance of other ocr

            if args.ocr.find('api_ocr_space') >= 0:
                text_ja_ocrspace = ocr_space_API.ocr_space_get_text('OCR_image_last.png', 'jpn')  # 调用OCR
                print("OcrSpace: {}".format(text_ja_ocrspace))
                with open(text_record_file, "a", encoding="utf-8") as file_text_record:
                    file_text_record.write('\n' + 'OcrSpace: '+text_ja_ocrspace)
                text_ja_ocrspace, ocrspace_if_chg = ocr_manual_correction(["ja"], text_ja_ocrspace, ocrspace_REP_RULE)
                if ocrspace_if_chg:
                    print("OcrSpac1: {}".format(text_ja_ocrspace))
                    with open(text_record_file, "a", encoding="utf-8") as file_text_record:
                        file_text_record.write('\n' + 'OcrSpac1: ' + text_ja_ocrspace)
                if text_ja_good is not None and text_ja_ocrspace != text_ja_good:
                    text_ch += "【修正后OcrSpace不同】" if ocrspace_if_chg else "【OcrSpace不同】"
                else:
                    text_ja = text_ja_ocrspace
                    text_ja_good = text_ja_ocrspace

            if args.ocr.find('py_easyocr') >= 0:
                text_ja_easyocr = ocr_reader.readtext("OCR_image_last.png", detail=0)
                text_ja_easyocr = "".join([e for e in text_ja_easyocr])
                print("EasyOcr_: {}".format(text_ja_easyocr))
                text_ja_easyocr_corr, easyocr_if_chg = ocr_manual_correction(["ja"], text_ja_easyocr, easyocr_REP_RULE)
                print("EasyOcr1: {}".format(text_ja_easyocr_corr)) if easyocr_if_chg else 0
                with open(text_record_file, "a", encoding="utf-8") as file_text_record:
                    file_text_record.write('\n' + 'EasyOcr_: ' + text_ja_easyocr)
                    if easyocr_if_chg:
                        file_text_record.write('\n' + 'EasyOcr1: ' + text_ja_easyocr_corr)
                if text_ja_good is not None and text_ja_easyocr_corr != text_ja_good:
                    # print("【easyocr识别结果与baiduAPI不一致，请查看】")
                    text_ch += "【修正后EasyOcr不同】" if easyocr_if_chg else "【EasyOcr不同】"
                else:
                    text_ja = text_ja_easyocr_corr
            # text_ja = "どこかは判らない牧場で、白馬にまたがって走る感触を。大きな動物のやさしい体温を。"

            # ---------- translate
            # """
            text_ch += youdaofanyi.trans_text(text_ja, 'ja', 'zh-CHS')       # 调用翻译
            print("youdaoTR: {}".format(text_ch))
            with open(text_record_file, "a", encoding="utf-8") as file_text_record:
                file_text_record.write('\n'+'youdaoTR: '+text_ch)
            # ^^^ """
            # text_ch = text_ja

            # ---------- show
            show_text.show_text(text_ch, quit_key=[13, 32], duration=120)    # 显示文字, 退出方式（按ENTER键，或令窗口失焦）

            # ---------- other
            time.sleep(1)    # dead time
            print("\nwaiting ...")
    caption_task_flag = 0
    # ^^^ triggered
# ^^^ loop

print("program end")
show_text.pygame_quit()
sys.exit()

