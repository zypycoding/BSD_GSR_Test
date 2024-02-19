#!/usr/bin/python
# -*- coding:utf-8 -*-

import logging
import math
import os

import numpy as np


class LogColor:
    """
    根据不同的日志级别，打印不颜色的日志
    info：绿色
    warning：黄色
    error：红色
    debug：灰色
    """
    # logging日志格式设置
    logging.basicConfig(level=logging.INFO,
                        format="line:%(lineno)s %(asctime)s  [%(levelname)s]  %(message)s",
                        datefmt="%Y-%d-%m %H:%M:%S")

    @staticmethod
    def info(message: str):
        # info级别的日志，绿色
        logging.info("\033[0;32m" + message + "\033[0m")

    @staticmethod
    def warning(message: str):
        # warning级别的日志，黄色
        logging.warning("\033[0;33m" + message + "\033[0m")

    @staticmethod
    def error(message: str):
        # error级别的日志，红色
        logging.error("\033[0;31m" + message + "\033[0m" + "\n" + "-" * 80)

    @staticmethod
    def debug(message: str):
        # debug级别的日志，灰色

        logging.debug("\033[0;37m" + message + "\033[0m")



class Func:
    """
        将BSD_testbed算法处理结果的txt路径加入以下三个文件，方便后续处理单框算法加持，或多框算法加持
        'front_fisheye_file_list.txt'
        'right_fisheye_file_list.txt'
        'right_back_file_list.txt'
    """

    def __init__(self):
        self.front_fisheye_file_list = []
        self.right_fisheye_file_list = []
        self.right_back_file_list = []
        self.data_list = []
        self.name = ''
        self.root_path = r''

    def rename_flie(self):
        for root, dirs, files in os.walk(self.root_path):
            for f in files:
                if f.endswith('.mp4'):
                    video_type_l = f.split('_')
                    if 'front' in video_type_l or 'Front' in video_type_l and not f.endswith('_B.mp4'):
                        old_path = os.path.join(root, f)
                        new_path = os.path.join(root, f.replace('.mp4', '_B.mp4'))
                        os.rename(old_path, new_path)
                    elif 'right' in video_type_l or 'Right' in video_type_l and not f.endswith('_C.mp4'):
                        old_path = os.path.join(root, f)
                        new_path = os.path.join(root, f.replace('.mp4', '_C.mp4'))
                        os.rename(old_path, new_path)
                    elif 'back' in video_type_l or 'Back' in video_type_l and not f.endswith('_A.mp4'):
                        old_path = os.path.join(root, f)
                        new_path = os.path.join(root, f.replace('.mp4', '_A.mp4'))
                        os.rename(old_path, new_path)

    def path_deal(self):
        for root, dirs, files in os.walk(self.root_path):
            for file in files:
                if file.endswith('A.mp4'):
                    src_path = os.path.join(root, file)
                    abs_path = os.path.abspath(src_path)
                    self.right_back_file_list.append(abs_path)
                if file.endswith('B.mp4'):
                    src_path = os.path.join(root, file)
                    abs_path = os.path.abspath(src_path)
                    self.front_fisheye_file_list.append(abs_path)
                if file.endswith('C.mp4'):
                    src_path = os.path.join(root, file)
                    abs_path = os.path.abspath(src_path)
                    self.right_fisheye_file_list.append(abs_path)

    def save_file(self, name, data_list):
        self.name = name
        self.data_list = data_list
        with open(self.name, 'w+') as f:
            for name in self.data_list:
                name_l = name.split('\\')[-4:]
                name = '\\'.join(name_l)
                txt = name + '\n'
                f.write(txt)

    def run_func(self,root_path):
        self.root_path = root_path
        print(self.root_path)
        if os.path.exists(self.root_path):
            if (not self.root_path.endswith('A.mp4') or not self.root_path.endswith('B.mp4')
                    or not self.root_path.endswith('C.mp4')):
                pass
                # self.rename_flie()
            self.path_deal()
            self.save_file(os.path.join(self.root_path, 'front_fisheye_file_list.txt'), self.front_fisheye_file_list)
            self.save_file(os.path.join(self.root_path, 'right_fisheye_file_list.txt'), self.right_fisheye_file_list)
            self.save_file(os.path.join(self.root_path, 'right_back_file_list.txt'), self.right_back_file_list)
            return True
        else:
            LogColor.info('-'*8 + f'输入的路径{self.root_path}不存在')
            # self.root_path = input("请重新输入需要操作的路径：").strip()


class ResultEnum(object):
    Wrong = 2  # 误检
    Success = 1  # 正检
    Miss = 0  # 漏检


class RectTypeEnum(object):
    Vehicle = 'vehicle'
    Person = 'person'


class RectData(object):
    """
    计算两个框的各种数据

    包含：
        cle: 两个框中心点距离计算
        iou: 两个框的交集 / 两个框的并集 （交并比）
        iog: 重叠区域面积 / 标记框面积
        ioc: 重叠区域面积 / 检测框面积
        distance: 根据像素判断距离

    Attributes:
        detect_rect: 标记框 -> （619,277,953,578）
        mark_rect: 结果框 -> （619,277,953,578）
    """

    def __init__(self, detect_rect, mark_rect):
        self.mark_rect = mark_rect
        self.detect_rect = detect_rect

        # 检测框坐标
        self.left_detect, self.top_detect, self.right_detect, self.bottom_detect = map(int, map(float, detect_rect))
        self.left_detect = self.left_detect if self.left_detect >= 0 else 0
        self.top_detect = self.top_detect if self.top_detect >= 0 else 0
        self.right_detect = self.right_detect if self.right_detect >= 0 else 0
        self.bottom_detect = self.bottom_detect if self.bottom_detect >= 0 else 0
        # 标记框坐标
        self.left_mark, self.top_mark, self.right_mark, self.bottom_mark = map(int, map(float, mark_rect))
        self.left_mark = self.left_mark if self.left_mark >= 0 else 0
        self.top_mark = self.top_mark if self.top_mark >= 0 else 0
        self.right_mark = self.right_mark if self.right_mark >= 0 else 0
        self.bottom_mark = self.bottom_mark if self.bottom_mark >= 0 else 0
        # 检测框面积
        self.detect_area = (self.right_detect - self.left_detect) * (self.bottom_detect - self.top_detect)
        # 标记框面积
        self.mark_area = (self.right_mark - self.left_mark) * (self.bottom_mark - self.top_mark)
        # 检测框与标记框相交面积
        self.left = max(self.left_detect, self.left_mark)
        self.top = max(self.top_detect, self.top_mark)
        self.right = min(self.right_detect, self.right_mark)
        self.bottom = min(self.bottom_detect, self.bottom_mark)
        self.intersection_area = (self.right - self.left) * (self.bottom - self.top)
        # 宽高比
        self.left_ = min(self.left_detect, self.left_mark)
        self.top_ = min(self.top_detect, self.top_mark)
        self.right_ = max(self.right_detect, self.right_mark)
        self.bottom_ = max(self.bottom_detect, self.bottom_mark)
        self.intersection_width = self.right - self.left
        self.intersection_height = self.bottom - self.top
        self.union_width = self.right_ - self.left_
        self.union_height = self.bottom_ - self.top_
        self.logger = None

        self.detect_middle_x = (self.right_detect + self.left_detect) / 2  # 检测框中心点横坐标
        self.mark_middle_x = (self.right_mark + self.left_mark) / 2  # 标记框中心点横坐标
        self.mark_quarter_x = (self.right_mark - self.left_mark) / 4  # 标记框长度的1/4（横坐标）

    def cle(self):
        """两个框中心点距离计算"""

        # box1的中心点坐标
        center_x1 = self.left_detect + (self.right_detect - self.left_detect) / 2
        center_y1 = self.top_detect + (self.bottom_detect - self.top_detect) / 2
        # box2的中心点坐标
        center_x2 = self.left_mark + (self.right_mark - self.left_mark) / 2
        center_y2 = self.top_mark + (self.bottom_mark - self.top_mark) / 2

        distances = math.sqrt((center_x1 - center_x2) ** 2 + (center_y1 - center_y2) ** 2)
        return round(distances, 2)

    def iou(self):
        """两个框的交集 / 两个框的并集 （交并比）"""

        # 两个矩形框的面积
        sum_area = self.detect_area + self.mark_area
        if self.left >= self.right or self.top >= self.bottom:
            return [0, 0, 0]  # 不相交
        else:
            iou_area = round(self.intersection_area / (sum_area - self.intersection_area), 2)
            iou_width = round(self.intersection_width / self.union_width, 2)
            iou_height = round(self.intersection_height / self.union_height, 2)
            return [iou_area, iou_width, iou_height]

    def iou_complex(self):
        """
        复杂计算方式，只用来计算车头车尾的IOU。如果标记文件是全框，算法输出只有车头车尾，则应该用这个方法
        Returns:
        iou(int)
        """
        iou = self.iou()[0]
        if iou > 1 or iou < 0:
            raise NameError('iou计算错误')
        elif iou == 0 or iou >= 0.5:
            return iou
        else:  # iou<0.5
            iou_vehicle = self.__vehicle_iou()
            if iou_vehicle == 0:
                return iou
            else:
                return iou_vehicle

    def __vehicle_iou(self):
        if (self.detect_middle_x - self.mark_middle_x) <= (-self.mark_quarter_x):  # 检测框在左侧
            iou = self.__vehicle_iou_left()

        elif (self.detect_middle_x - self.mark_middle_x) >= self.mark_quarter_x:  # 检测框在右侧
            iou = self.__vehicle_iou_right()

        else:  # 检测框在中间
            if (self.detect_middle_x - self.mark_middle_x) < 0:  # 中间偏左
                if abs(self.left_mark - self.left_detect) >= 5:
                    iou = 0
                else:
                    iou = self.__vehicle_iou_left()

            else:  # 中间偏右
                if abs(self.left_mark - self.left_detect) >= 5:
                    iou = 0
                else:
                    iou = self.__vehicle_iou_right()

        return iou

    def __vehicle_iou_left(self):
        mark_rect_new_first = (
            self.left_mark, self.top_mark, self.left_mark + 2 * self.mark_quarter_x, self.bottom_mark)
        iou = RectData(self.detect_rect, mark_rect_new_first).iou()[0]
        if iou >= 0.5:
            return iou
        else:
            mark_rect_new_two = (
                self.left_mark, self.top_mark, 0.4 * self.right_mark + 0.6 * self.left_mark, self.bottom_detect)
            iou = RectData(self.detect_rect, mark_rect_new_two).iou()[0]
            iou = iou if iou >= 0.5 else 0
            return iou

    def __vehicle_iou_right(self):
        mark_rect_new_first = (
            self.left_mark + 2 * self.mark_quarter_x, self.top_mark, self.right_mark, self.bottom_mark)
        iou = RectData(self.detect_rect, mark_rect_new_first).iou()[0]
        if iou >= 0.5:
            return iou
        else:
            mark_rect_new_two = (
                0.6 * self.right_mark + 0.4 * self.left_mark, self.top_mark, self.right_mark, self.bottom_detect)
            iou = RectData(self.detect_rect, mark_rect_new_two).iou()[0]
            iou = iou if iou >= 0.5 else 0
            return iou

    def iog(self):
        """重叠区域面积 / 标记框面积"""

        if self.left >= self.right or self.top >= self.bottom:
            return [0, 0, 0]  # 不相交
        else:
            iog_area = round(self.intersection_area / self.mark_area, 2)
            iog_width = round(self.intersection_width / (self.right_detect - self.left_detect), 2)
            iog_height = round(self.intersection_height / (self.bottom_detect - self.top_detect), 2)
            return [iog_area, iog_width, iog_height]

    def ioc(self):
        """ 重叠区域面积 / 检测框面积"""

        if self.left >= self.right or self.top >= self.bottom:
            return [0, 0, 0]  # 不相交
        else:
            ioc_area = round(self.intersection_area / self.detect_area, 2)
            ioc_width = round(self.intersection_width / (self.right_mark - self.left_mark), 2)
            ioc_height = round(self.intersection_height / (self.bottom_mark - self.top_mark), 2)
            return [ioc_area, ioc_width, ioc_height]


def distance(rect, object_type, k_car=None, k_person=None):
    """
    计算标记框的距离
    :return:
    """
    left_detect, top_detect, right_detect, bottom_detect = map(int, map(float, rect))
    d = 0
    tmp = 0
    k = min(int(right_detect) - int(left_detect), int(bottom_detect) - int(top_detect))
    if object_type == RectTypeEnum.Vehicle:
        if k_car:
            _k = k_car
        else:
            _k = K_CAR
    elif object_type == RectTypeEnum.Person:
        if k_person:
            _k = k_person
        else:
            _k = K_PERSON
    else:
        logger.error(f'{object_type}填写不正确，请填"vehicle"或者"person"')
        return 0

    key = sorted([int(x) for x in _k.keys() if x != ''])

    for k_k in key:
        if k < key[0]:
            d = '设定距离外'
            break
        if k < k_k:
            d = _k[str(tmp)]
            break
        tmp = k_k

    if d == 0:
        d = _k[str(key[-1])]

    return d


def pixel(rect):
    """
    计算框的短边像素值
    :param rect:
    :return:
    """
    left_detect, top_detect, right_detect, bottom_detect = map(int, map(float, rect))
    return min(int(right_detect) - int(left_detect), int(bottom_detect) - int(top_detect))


def count_mse(m_array, d_array):
    if type(m_array) is np.ndarray and type(d_array) is np.ndarray and m_array.size == d_array.size:
        if m_array.size == 0 and d_array.size == 0:
            mse = float(9999)
        else:
            mse = ((m_array - d_array) ** 2).mean()
        return mse
    else:
        raise TypeError("入参必须为np.ndarray类型，且矩阵大小必须相等")


def count_re(mark_points_list, low, high):
    v_list = []
    tmp_list = []
    for point in mark_points_list:
        v_list.append(float(point[1]))
    v_max = max(v_list)
    v_min = min(v_list)
    tmp_list.append(v_max)
    tmp_list.append(v_min)
    tmp_list.append(low)
    tmp_list.append(high)
    tmp_list.sort()

    union = tmp_list[3] - tmp_list[0]
    intersection = tmp_list[2] - tmp_list[1]
    re = 1 - (intersection / union)
    return re


def count_r_square(m_array, d_array):
    r_square = 1 - ((sum((m_array - d_array) ** 2)) / sum((d_array - d_array.mean()) ** 2))
    if r_square == float("-inf") or np.isnan(r_square):
        r_square = -999999
    return r_square


def get_min_or_max_index(array, get_max=False):
    mark_index_list = []
    detect_index_list = []
    narry_size = array.size
    while narry_size != 0:
        if get_max:
            index = np.unravel_index(array.argmax(), array.shape)
            mark_row, detect_row = index
            if array[mark_row][detect_row] == 0.0:
                narry_size -= 1
                continue
        else:
            index = np.unravel_index(array.argmin(), array.shape)
        mark_row, detect_row = index
        # 判断索引是否在
        if mark_row not in mark_index_list and detect_row not in detect_index_list:
            mark_index_list.append(mark_row)
            detect_index_list.append(detect_row)
        if get_max:
            array[mark_row][detect_row] = 0.0
        else:
            array[mark_row][detect_row] = float('inf')
        narry_size -= 1
    return [mark_index_list, detect_index_list]



if __name__ == '__main__':
    # 测试代码
    LogColor.info("info日志")
    LogColor.warning("warning日志")
    LogColor.error("error日志")
    LogColor.debug("debug日志")
