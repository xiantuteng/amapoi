# coding=utf-8
import json

import requests

AmapErrorEnum = {
    '10001': 'key不正确或过期',
    '10002': '没有权限使用相应的服务或者请求接口的路径拼写错误',
    '10003': '访问已超出日访问量',
    '10004': '单位时间内访问过于频繁',
    '10005': 'IP白名单出错，发送请求的服务器IP不在IP白名单内',
    '10006': '绑定域名无效',
    '10007': '数字签名未通过验证',
    '10008': 'MD5安全码未通过验证',
    '10009': '请求key与绑定平台不符',
    '10010': 'IP访问超限',
    '10011': '服务不支持https请求',
    '10012': '权限不足，服务请求被拒绝',
    '10013': 'Key被删除',
    '10014': '云图服务QPS超限',
    '10015': '受单机QPS限流限制',
    '10016': '服务器负载过高',
    '10017': '所请求的资源不可用',
    '10019': '使用的某个服务总QPS超限',
    '10020': '某个Key使用某个服务接口QPS超出限制',
    '10021': '账号使用某个服务接口QPS超出限制',
    '10026': '账号处于被封禁状态',
    '10029': '某个Key的QPS超出限制',
    '10041': '请求的接口权限过期',
    '10044': '账号维度日调用量超出限制',
    '10045': '账号维度海外服务日调用量超出限制',
    '20000': '请求参数非法',
    '20001': '缺少必填参数',
    '20002': '请求协议非法',
    '20003': '其他未知错误',
    '20011': '查询坐标或规划点（包括起点、终点、途经点）在海外，但没有海外地图权限',
    '20012': '查询信息存在非法内容',
    '20800': '规划点（包括起点、终点、途经点）不在中国陆地范围内',
    '20801': '划点（起点、终点、途经点）附近搜不到路',
    '20802': '路线计算失败，通常是由于道路连通关系导致',
    '20803': '起点终点距离过长。',
    '30000': '服务响应失败。',
    '40000': '余额耗尽',
    '40001': '围栏个数达到上限',
    '40002': '购买服务到期',
    '40003': '海外服务余额耗尽'
}

DEFAULT_PAGE_NUM = 1
DEFAULT_PAGE_SIZE = 25


class AmapException(Exception):
    def __init__(self, code=10000):
        self.code = code
        self.error = '未知错误'
        if self.code in AmapErrorEnum:
            self.error = AmapErrorEnum[self.code]


def place_polygon(key, polygon, page_num=DEFAULT_PAGE_NUM, page_size=DEFAULT_PAGE_SIZE):
    """
    利用高德多边形POI查询接口，获取区域内所有类型的POI数据
    :param key: 高德KEY
    :param polygon: 多个坐标对集合，坐标对用"|"分割。多边形为矩形时，可传入左上右下两顶点坐标对；其他情况下首尾坐标对需相同。
    :param page_num: 当前页码
    :param page_size: 每页结果数
    :return: (total, [object,])
    """
    url = 'https://restapi.amap.com/v5/place/polygon?key=%s&polygon=%s&page_size=%d&page_num=%d' \
          '&types=10000|20000|30000|40000|50000|60000|70000|80000|90000|100000|110000|120000|130000|140000|150000|160000|170000|180000|190000|200000|220000|970000|990000'
    url = url % (key, polygon, page_size, page_num)
    resp = requests.get(url, proxies={
        "http": None,
        "https": None,
    })
    if resp.status_code != 200:
        raise Exception('服务器错误：%d %s' % (resp.status_code, url))
    resp_json = json.loads(resp.text)
    if resp_json['infocode'] != '10000':
        raise AmapException(resp_json['infocode'])
    total = int(resp_json['count'])
    pois = resp_json['pois']
    return total, pois


def place_polygon_all(key, polygon):
    """
    获取区域内所有的POI数据
    :param key: 高德APK Key
    :param polygon: 高德地图多边形坐标对，格式如： x1,y1|x2,y2|...
    :return:
    """
    poi_list = []
    has_error = False
    for i in range(40):  # 最多40页，超过40页就不会返回数据
        total, pois = place_polygon(key, polygon, i + 1)
        if total > 0:
            poi_list.extend(pois)
        else:
            if has_error:
                break
            else:
                has_error = True
    return poi_list


def judge_place_polygon(key, polygon):
    """
    判断是否需要拆分网格
    :param key: 高德Key
    :param polygon: 网格边界
    :return:
    """
    total, pois = place_polygon(key, polygon, 36, DEFAULT_PAGE_SIZE)
    return total > 0


if __name__ == '__main__':
    judge_place_polygon('57c3aec55ea015ef91d9fa92a965d2fe', '103|31|104|29')
