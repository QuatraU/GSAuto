import numpy as np
import win32api, win32gui, win32ui, win32con
import sys, time, cv2
import pyscreenshot as imgG
from matplotlib import pyplot as plt


class GenshinWnd:
    hwnd = None  # 窗口句柄
    left, top, right, bot = 0, 0, 0, 0  # 窗口的四边框坐标

    def __init__(self):
        self.window_init()

    # 窗口捕获
    def window_init(self):
        while not self.hwnd:
            print('getting genshin HWND...')
            self.hwnd = win32gui.FindWindow(None, '原神')
            if not self.hwnd:
                print('HWND not found.')
                time.sleep(5)
        print('genshin HWND captured.')
        self.left, self.top, self.right, self.bot = win32gui.GetWindowRect(self.hwnd)
        print(self.left, self.top, self.right, self.bot)
        # 窗口置顶
        win32gui.SetForegroundWindow(self.hwnd)

    # 截取指定位置截图
    def getScreenShot(self, x1, y1, x2, y2):  # 左 上 右 下
        return imgG.grab(backend="mss", childprocess=False, bbox=(x1, y1, x2, y2))

    # 获取左上角小地图截图
    def getMinimap(self):
        return self.getScreenShot(self.left + 64, self.top + 44,
                                  self.left + 64 + 215, self.top + 44 + 215)
    # 获取整个窗口截图
    def getFullscreen(self):
        return self.getScreenShot(self.left, self.top, self.right, self.bot)

# 在图片A上寻找图片B
def targetMatch(imgA, imgB):
    # 读取目标图片
    target = imgA
    # 读取模板图片
    template = imgB
    # 获得模板图片的高宽尺寸
    theight, twidth = template.shape[:2]
    # 执行模板匹配，采用的匹配方式cv2.TM_SQDIFF_NORMED
    result = cv2.matchTemplate(target, template, cv2.TM_SQDIFF_NORMED)
    # 归一化处理
    # cv2.normalize( result, result, 0, 1, cv2.NORM_MINMAX, -1 )
    # 寻找矩阵（一维数组当做向量，用Mat定义）中的最大值和最小值的匹配结果及其位置
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    # 绘制矩形边框，将匹配区域标注出来
    # min_loc：矩形定点
    # (min_loc[0]+twidth,min_loc[1]+theight)：矩形的宽高
    # (0,0,225)：矩形的边框颜色；2：矩形边框宽度
    cv2.rectangle(target, min_loc, (min_loc[0] + twidth, min_loc[1] + theight), (0, 0, 225), 2)
    # 匹配值转换为字符串
    # 对于cv2.TM_SQDIFF及cv2.TM_SQDIFF_NORMED方法min_val越趋近与0匹配度越好，匹配位置取min_loc
    # 对于其他方法max_val越趋近于1匹配度越好，匹配位置取max_loc
    strmin_val = str(min_val)
    # 初始化位置参数
    temp_loc = min_loc
    other_loc = min_loc
    numOfloc = 1
    # 第一次筛选----规定匹配阈值，将满足阈值的从result中提取出来
    # 对于cv2.TM_SQDIFF及cv2.TM_SQDIFF_NORMED方法设置匹配阈值为?
    threshold = 0.11
    loc = np.where(result < threshold)
    # 遍历提取出来的位置
    for other_loc in zip(*loc[::-1]):
        # 第二次筛选----将位置偏移小于?个像素的结果舍去
        if (temp_loc[0] + 5 < other_loc[0]) or (temp_loc[1] + 5 < other_loc[1]):
            numOfloc = numOfloc + 1
            temp_loc = other_loc
            cv2.rectangle(target, other_loc, (other_loc[0] + twidth, other_loc[1] + theight), (0, 0, 225), 2)
    str_numOfloc = str(numOfloc)
    print(str_numOfloc)
    # 显示结果,并将匹配值显示在标题栏上
    strText = "MatchResult----MatchingValue=" + strmin_val + "----NumberOfPosition=" + str_numOfloc
    cv2.imshow(strText, target)
    cv2.waitKey()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    genshin = GenshinWnd()
    fullscreen = genshin.getFullscreen()
    fullscreen = cv2.cvtColor(np.asarray(fullscreen),cv2.COLOR_RGB2BGR)

    # print(type(fullscreen))
    temp = cv2.imread('./icon/dailytask-l.png')
    targetMatch(fullscreen, temp)

    # fullscreen.show()
