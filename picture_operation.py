import numpy
from PyQt5.QtWidgets import QApplication
import pyautogui    # 自动化桌面脚本库，包含鼠标、键盘、截图操作
import matplotlib.pyplot as plt
import win32gui
import sys
import time
import numpy as np


def get_hwnd_title_list():
    """
    获取 句柄(hwnd) 标题(title) 的列表
    for test
    :return:
    """
    hwnd_title = dict()  # 创建字典保存窗口的句柄与名称映射关系

    def get_all_hwnd(hwnd, mouse):
        if win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd):
            hwnd_title.update({hwnd: win32gui.GetWindowText(hwnd)})

    win32gui.EnumWindows(get_all_hwnd, 0)
    for h, t in hwnd_title.items():
        if t != "":
            print(h, t)


def screen_cap2(title='C:/Windows/system32/cmd.exe'):
    """
    截取某窗口视图。使用PyQt5库。
    貌似该函数用久（4~5小时连续不断）后，命令行会出现无法获得窗口句柄的报错。
    :param if_save:
    :param title:
        当前全屏：'C:/Windows/system32/cmd.exe'
    :return:
    """
    hwnd = win32gui.FindWindow(None, title)   # 通过窗口名称获取窗口句柄
    app = QApplication(sys.argv)
    screen = QApplication.primaryScreen()
    image = screen.grabWindow(hwnd).toImage()  # <class 'PyQt5.QtGui.QImage'>
    image.save("./cache/screenshot_last.png")
    image = plt.imread('./cache/screenshot_last.png')  # <class 'numpy.ndarray'>
    return image


def screen_cap(region=None, if_save=False):
    """
    截图屏幕某区域视图，使用pyautogui库
    :param if_save: 一般调试时设为True
    :param region:
    :return:
    """
    if region is None:
        region = [0, 0, 1366, 768]    # x,y,w,h
    image = pyautogui.screenshot(region=region)    # <class 'PIL.Image.Image'>
    if if_save is True:
        image.save("screenshot_last.png")
    # image = plt.imread('screenshot_last.png')  # <class 'numpy.ndarray'>
    image = numpy.array(image)    # <class 'numpy.ndarray'>
    return image


# def image_1to255_noalpha(img0):
#     # 将像素值从0~1变为0~255，删除透明度层
#     # 删除透明度层
#     if


def image_rgb2gray(img_):
    # img元素值0~1之间
    image = img_[:, :, :3].sum(axis=2) / 3
    img_[:, :, 0] = image
    img_[:, :, 1] = image
    img_[:, :, 2] = image
    # image = np.expand_dims(image, axis=-1)

    # print(type(image))
    # print(image.shape)
    return image, img_   # image维数为2，表示灰度图。  img_维数为3，rgb值一样，用于显示。


def image_rgb2bw(img_, thresold_01=160):  # 255白
    img_gray_1layer, _ = image_rgb2gray(img_)
    for i in range(len(img_gray_1layer)):
        for j in range(len(img_gray_1layer[0])):
            img_gray_1layer[i][j] = 255 if img_gray_1layer[i][j] > thresold_01 else 0
    img_[:, :, 0] = img_gray_1layer
    img_[:, :, 1] = img_gray_1layer
    img_[:, :, 2] = img_gray_1layer
    return img_gray_1layer, img_


# def image_cut_text(img0, lb_thre=30):
#     # 针对仅包含文字的图片，进一步切割图片，令文字信息占据图片更大比例
#     # 将图片二值化
#     print(img0)
#     print(XXXXXX)
#     # img1, _ = image_rgb2bw(img0)
#     # 判断黑多还是白多，用于确定背景色
#     print(len(img1), len(img1[0]))
#     clr_sum = 0
#     for row in img1:
#         for pixel in row:
#             clr = 1 if pixel > 0 else 0
#             clr_sum += clr
#     print(clr_sum)
#     print(XXXXX)
#     # 从左上角开始，找到第一个非背景像素点
#     # 右下角边框延伸，若持续lb_thre个像素尺寸都没有非背景像素点，则确定右下边框位置，
#     """
#                  |  | <-- lb_thre
#         -----------------------------
#         |________|  |               |
#         |___________|               |
#         |                           |
#         |                           |
#         |                           |
#         -----------------------------
#     """
#     # 对原图裁剪，返回



IMAGE_SIMILAR_THRE = 0.08

def get_image_similarity(img1, img2):
    # img元素值0~1之间
    img1_size = img1.shape
    img2_size = img2.shape

    # 判断黑白、彩图
    if len(img1_size) != len(img2_size):
        return 2
    # 判断图片尺寸
    if img1_size[0] != img2_size[0] or img1_size[1] != img2_size[1]:
        return 3

    img_pixel = img1_size[0]*img1_size[1]
    if len(img1_size) > 2:
        img_pixel *= img1_size[2]
    img_sub = abs(img1-img2)
    # print(img_sub[400:410, 300:310, :])
    res = img_sub.sum()/img_pixel
    # print(img_sub.sum())
    # print(img_pixel)
    # print(res)
    return res    # 0<res<1


def my_bubble_sort_for_2d_distance(array):
    # bubble sort
    # array = [(0,0), (0,1), (1,1), (1,0), (1,-1), ...]
    num = len(array)
    for i in range(num-1, 0, -1):
        bubble_temp = array[0]
        for j in range(0, i):
            if abs(bubble_temp[0])+abs(bubble_temp[1]) > abs(array[j+1][0])+abs(array[j+1][1]):
                array[j] = array[j+1]
            else:
                array[j] = bubble_temp
                bubble_temp = array[j+1]
        array[i] = bubble_temp
    return array


def images_compare_similarity_range(img1, img2_large, img2_hei_edge, img2_wid_edge, range_lim):
    """
    一张示例图片，从另一张图中选一块区域，两者比较相似度。
    还会从选择的区域附近选择多个尺寸相同的区域，比较多次相似度，输出最小的一个。
    :return:
    """
    offset_array = []
    for i in range(-range_lim, range_lim+1):
        for j in range(-range_lim, range_lim+1):
            offset = (i, j)
            offset_array.append(offset)
    if len(offset_array)>4:
        offset_array = my_bubble_sort_for_2d_distance(offset_array)    # bubble sort
    # print(offset_array)

    res = 10
    for (off_h, off_w) in offset_array:
        img2 = img2_large[img2_hei_edge[0]+off_h:img2_hei_edge[1]+off_h, img2_wid_edge[0]+off_w:img2_wid_edge[1]+off_w, :]
        res = get_image_similarity(img1, img2)
        # print(res)
        if res < IMAGE_SIMILAR_THRE:    # find similar image
            return res, (off_h, off_w)

    (off_h, off_w) = offset_array[len(offset_array)-1]
    return res, (off_h, off_w)


if __name__ == "__main__":
    # get_hwnd_title_list()
    # time.sleep(5)
    # screen_cap('C:/Windows/system32/cmd.exe')

    # plt.imshow(img)
    # plt.show()

    # time.sleep(3)
    # img1 = plt.imread('解压输入.png')
    # img2 = screen_cap()
    # img1 = img1[533+2:560+2, 633-1:666-1, :]
    # img1, _ = image_rgb2gray(img1)
    # img2, _ = image_rgb2gray(img2)
    # print(img1.shape)
    # print(img2.shape)
    # images_compare_similarity_range(img1, img2, [533, 560], [633, 666], 3)

    timepoint = time.time()  # (example) timepoint = 1651129411.2421718
    img = screen_cap()
    run_time = time.time() - timepoint  # (example) run_time = 72.69022607803345 (unit: s)
    print(type(img))
    print(img.shape)
    print(run_time)
