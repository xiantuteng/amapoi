# coding=utf-8
import csv
import os.path
import time

import region
import amap_api
from quadtree import QuadNode
from jsonconfig import JsonConfig
from filecontentlist import FileContentList

from shapely.geometry import shape

AMAP_KEY = '57c3aec55ea015ef91d9fa92a965d2fe'
MAX_LEVEL = 150
SLEEP_SECOND = 1


def write_quadnode(quad_node: QuadNode, level, quadtree_file_path: str):
    print('[O] %d %s %f' % (level, quad_node.to_amap_polygon(), quad_node.width_meter()))
    with open(quadtree_file_path, 'a', encoding='utf-8') as f:
        f.write(quad_node.to_amap_polygon())
        f.write('\n')
    pass


def __generate_quadtree(geometry, quadtree_file_path: str, quad_node=None, level=1):
    """
    生成区域四叉树
    :param geometry: 选择的区域多边形
    :param quadtree_file_path: 四叉树信息保存路径
    :param quad_node: 当前级别的四叉树节点
    :param level: 当前四叉树级别
    :return: None
    """
    if level >= MAX_LEVEL:
        write_quadnode(quad_node, level)
        return

    (minx, miny, maxx, maxy) = geometry.bounds  # (minx, miny, maxx, maxy)
    if quad_node is None:
        quad_node = QuadNode(minx, miny, maxx, maxy)
    if not region.intersects(geometry, quad_node):
        print('[X] %d %s %f' % (level, quad_node.to_amap_polygon(), quad_node.width_meter()))
        return
    need_split = amap_api.judge_place_polygon(AMAP_KEY, quad_node.to_amap_polygon())
    time.sleep(SLEEP_SECOND)  # 线程休眠，防止高德接口被封
    if not need_split:
        write_quadnode(quad_node, level, quadtree_file_path)
        return

    print('[S] %d %s %f' % (level, quad_node.to_amap_polygon(), quad_node.width_meter()))
    sub_quadnodes = quad_node.split()
    for sub_quadnode in sub_quadnodes:
        __generate_quadtree(geometry, sub_quadnode, level + 1)


def data_path(selected_region: region.Region):
    """
    获取采集结果的保存路径
    :param selected_region: 选择的区域
    :return:
    """
    file_path = 'data/' + selected_region.name
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    return file_path


def generate_quadtree(selected_region: region.Region):
    """
    生成四叉树，会自动忽略边界外和不需要采集的四叉树节点
    :param selected_region: 当前选择的区域
    :return: None
    """
    file_path = data_path(selected_region)
    config_path = file_path + '/progress.json'
    config = JsonConfig(config_path)
    config.set('hasQuadtree', False)
    # 加载多边形，开始生成四叉树
    geometry = shape(selected_region.geometry_json)
    quadtree_path = file_path + '/quadtree.txt'
    __generate_quadtree(geometry, quadtree_path)
    # 更新生成四叉树标识
    config.set('hasQuadtree', True)


def write_pois(csv_writer, poi_list: list, first_write=False):
    # 写入CSV表头
    if first_write and len(poi_list) > 0:
        poi = poi_list[0]
        csv_writer.writerow(poi.keys())
    # 写入CSV内容
    start_i = 1 if first_write > 0 else 0
    for i in range(start_i, len(poi_list)):
        poi = poi_list[i]
        csv_writer.writerow(poi.values())
    pass


def download_poi(selected_region: region.Region):
    file_path = data_path(selected_region)
    config_path = file_path + '/progress.json'
    config = JsonConfig(config_path)

    # 生成POI采集四叉树
    has_quadtree = config.getboolean('hasQuadtree', False)  # 是否生成四叉树网格
    if not has_quadtree:
        try:
            generate_quadtree(selected_region)
        except amap_api.AmapException as e:
            return
        except Exception as e:
            return

    # 开始按四叉树网格采集POI
    fl = FileContentList(data_path(selected_region) + '/quadtree.txt')
    start_n = config.getint('currentNodeIndex', 0)      # 读取上次采集进度
    for n in range(start_n, len(fl)):
        line = fl[n].strip()
        quad_node = QuadNode.from_amap_polygon(line)
        try:
            poi_list = amap_api.place_polygon_all(AMAP_KEY, quad_node.to_amap_polygon())
            poi_path = data_path(selected_region) + '/poi.csv'
            file_exist = os.path.exists(poi_path)
            with open(poi_path, 'a', encoding='GB18030', newline='\n') as f:
                csv_writer = csv.writer(f)
                write_pois(csv_writer, poi_list, not file_exist)
            config.set('currentNodeIndex', n+1)
        except amap_api.AmapException as e:
            pass
        except Exception as e:
            pass


if __name__ == '__main__':
    provinces = region.load_provinces()
    province = provinces[0]
    download_poi(province)

    region_name = province.name
    geometry = shape(province.geometry_json)
    __generate_quadtree(geometry)
