import sys
import os
import time
import pygame as pg
import win32gui
import win32con
import win32com.client


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
    # for h, t in hwnd_title.items():
    #     if t != "":
    #         print(h, t)
    return hwnd_title.items()


def pygame_init():
    pg.init()


def pygame_quit():
    pg.quit()


def render_multi_line(screen, font, font_color, text,
                      x_left, y_top, y_incre):
    """
    show multi line text. there should be '\n' in text.
    """
    lines = text.splitlines()
    for i, l in enumerate(lines):
        screen.blit(font.render(l, 0, font_color), (x_left, y_top+y_incre*i))


Win_Hei_Last = 50


def show_text(text, quit_key=[13], duration=-1):
    # info = pg.display.Info()

    # set  height of window, font size, number of lines
    font_size = 20
    win_hei = 50
    line_num = len(text) // 42
    for li in range(line_num, 0, -1):
        text = text[:42*li] + '\n' + text[42*li:]
        win_hei += font_size + 10

    global Win_Hei_Last
    if win_hei != Win_Hei_Last:
        pg.quit()  # only when pygame is restarted, the position where the window appears world be changed
        pg.init()
        Win_Hei_Last = win_hei
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d, %d" % (200, 768-win_hei)  # 设置窗口出现位置
    screen = pg.display.set_mode((900, win_hei), pg.NOFRAME)   # 设置窗口尺寸
    screen.fill((50, 50, 50))                 # 设置窗口背景色 (0,0,0)黑
    screen_rect = screen.get_rect()          # 获得窗口尺寸信息
    # 设置焦点
    screen_title, _ = pg.display.get_caption()
    # print(screen_title)
    screen_hwnd = win32gui.FindWindow(None, screen_title)
    # print(win_list)
    shell = win32com.client.Dispatch("WScript.Shell")
    shell.SendKeys('%')
    # ^^^ 焦点设置报错解决：https://blog.csdn.net/bailichun19901111/article/details/105042145?spm=1001.2101.3001.6650.2&utm_medium=distribute.pc_relevant.none-task-blog-2%7Edefault%7ECTRLIST%7ERate-2-105042145-blog-112958323.pc_relevant_landingrelevant&depth_1-utm_source=distribute.pc_relevant.none-task-blog-2%7Edefault%7ECTRLIST%7ERate-2-105042145-blog-112958323.pc_relevant_landingrelevant&utm_relevant_index=3
    win32gui.SetForegroundWindow(screen_hwnd)
    win32gui.ShowWindow(screen_hwnd, win32con.SW_SHOW)

    font = pg.font.SysFont("Microsoft YaHei", font_size)     # 设置字体
    color = (200, 200, 200)                             # 文字颜色

    clock = pg.time.Clock()                   # 创建窗口刷新率相关对象

    # txt = font.render(text, True, color)          # 创建文字对象
    # screen.blit(txt, txt.get_rect(center=screen_rect.center))  # 将文字放到窗口中
    render_multi_line(screen, font, color, text,
                      x_left=25, y_top=10, y_incre=font_size+10)
    pg.display.flip()                                   # 窗口画面刷新
    display_timepoint = time.time()

    done = False
    # i = 0
    while not done:
        # ------------------------------ 循环退出管理
        if duration > 0:
            if time.time() - display_timepoint > duration:  # timeout
                done = True
        for event in pg.event.get():      # pygame事件捕捉
            # print(event)
            if event.type == pg.KEYUP:     # 键盘事件捕捉
                # print(event.key)    # （ENTER：13，'：39, <SPACE>:32, ）
                if event.key in quit_key:  # 检测到某键
                    done = True                # exit
            if event.type == pg.MOUSEBUTTONUP:     # 鼠标点击事件捕捉
                done = True
            # if event.type == pg.WINDOWFOCUSLOST:  # 焦点丢失
            #     done = True                     # exit
            # if event.type == pg.TEXTEDITING:
            #     pass

        # ------------------------------ 画面更新的内容
        # Update the text surface and color every 10 frames.
        # if timer <= 0:
        #     timer = 10
        #     color = (randrange(256), randrange(256), randrange(256))
        #     txt = font.render(random_letters(randrange(5, 21)), True, color)

        # screen.fill((50, 50, 50))    # 设置窗口背景色，循环中若不加这句原来的文字不会消失
        # txt = font.render(text, True, color)
        # screen.blit(txt, txt.get_rect(center=screen_rect.center))
        # pg.display.flip()

        clock.tick(10)    # 设置窗口画面每秒刷新n次，这个设得太低会导致事件捕捉延时会增加。
    # ^^^ display update

    screen = pg.display.set_mode((1, 1), pg.NOFRAME)  # 退出后，令窗口消失
    screen.fill((50, 50, 50))


if __name__ == '__main__':
    pg.init()
    show_text("【easyocr不同】但是，不管大众怎么想，乃惠美的想法都不一样。这个剑舞本身，是为了打击咏叹调，自己以更高的顶点为目标，乃惠美提议举办的。【easyocr不同】但是，不管大众怎么想，乃惠美的想法都不一样。这个剑舞本身，是为了打击咏叹调，自己以更高的顶点为目标，乃惠美提议举办的。", duration=60)
    show_text("【但是，不管大众不同】但是，不管大众怎么想，乃惠美的想法都不一样。这个剑舞本这个剑舞本身，身，", duration=60)
    pg.quit()
    sys.exit()