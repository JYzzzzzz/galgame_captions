
import time
import win32api
import win32con
import win32gui


def get_mouse_pos():
    """
    函数功能：获取当前鼠标坐标
    左上角为(0,0)，右下角为（1365，767）
    """
    pos = win32gui.GetCursorPos()
    return pos


def mouse_move(pos):
    """
    函数功能：移动鼠标到指定位置
    参  数：x:x坐标
       y:y坐标
    """
    win32api.SetCursorPos(pos)


def mouse_click(lr, down_dly=0.0, up_dly=0.0):
    """
    函数功能：鼠标点击
    """
    if lr == 'right' or lr == 'r':
        mouse_down = win32con.MOUSEEVENTF_RIGHTDOWN
        mouse_up = win32con.MOUSEEVENTF_RIGHTUP
    elif lr == 'left' or lr == 'l':
        mouse_down = win32con.MOUSEEVENTF_LEFTDOWN
        mouse_up = win32con.MOUSEEVENTF_LEFTUP
    else:
        mouse_down = win32con.MOUSEEVENTF_LEFTDOWN
        mouse_up = win32con.MOUSEEVENTF_LEFTUP

    win32api.mouse_event(mouse_down, 0, 0, 0, 0)
    if down_dly > 0:
        time.sleep(down_dly)
    win32api.mouse_event(mouse_up, 0, 0, 0, 0)
    if up_dly > 0:
        time.sleep(up_dly)


def mouse_move_click(pos, lr, down_dly=0.0, up_dly=0.0):
    """
    mouse move & click
    :param up_dly:
    :param down_dly:
    :param pos:
    :param lr:
    :return:
    """
    mouse_move(pos)
    mouse_click(lr, down_dly=down_dly, up_dly=up_dly)


if __name__ == "__main__":
    time.sleep(5)
    print(get_mouse_pos())
    # mouse_move_click([1330, 78], 'l', down_dly=0.1)
