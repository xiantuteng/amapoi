# coding=utf-8
import time

import region
from quadtree import QuadNode
import amap_api

from shapely.geometry import shape

AMAP_KEY = '57c3aec55ea015ef91d9fa92a965d2fe'
MAX_LEVEL = 150
SLEEP_SECOND = 1


def write_quadnode(quadNode: QuadNode, level):
    print('[O] %d %s %f' % (level, quadNode.to_amap_polygon(), quadNode.width_meter()))
    with open('quadtree.txt', 'a', encoding='utf-8') as f:
        f.write(quadNode.to_amap_polygon())
        f.write('\n')
    pass


def generate_quadtree(geometry, quadNode=None, level=1):
    if level >= MAX_LEVEL:
        write_quadnode(quadNode, level)
        return

    (minx, miny, maxx, maxy) = geometry.bounds  # (minx, miny, maxx, maxy)
    if quadNode is None:
        quadNode = QuadNode(minx, miny, maxx, maxy)
    if not region.intersects(geometry, quadNode):
        print('[X] %d %s %f' % (level, quadNode.to_amap_polygon(), quadNode.width_meter()))
        return
    need_split = amap_api.judge_place_polygon(AMAP_KEY, quadNode.to_amap_polygon())
    time.sleep(SLEEP_SECOND)        # 线程休眠，防止高德接口被封
    if not need_split:
        write_quadnode(quadNode, level)
        return


    print('[S] %d %s %f' % (level, quadNode.to_amap_polygon(), quadNode.width_meter()))
    sub_quadnodes = quadNode.split()
    for sub_quadnode in sub_quadnodes:
        generate_quadtree(geometry, sub_quadnode, level + 1)


if __name__ == '__main__':
    provinces = region.load_provinces()
    province = provinces[0]
    region_name = province.name
    geometry = shape(province.geometry_json)
    generate_quadtree(geometry)
