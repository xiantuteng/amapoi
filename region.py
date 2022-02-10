# coding=utf-8

import json
import os.path

from shapely.geometry import shape, Polygon
from quadtree import QuadNode

CHINA_MAP_GEOJSON = '100000.geojson'


class Region:
    def __init__(self, name=None, code=None, properties={}, geometry_json=None):
        self.name = name
        self.code = code
        self.properties = {}
        self.geometry_json = geometry_json
        pass


def load_provinces():
    with open('geojson/' + CHINA_MAP_GEOJSON, 'r', encoding='UTF-8') as f:
        root = json.load(f)
    regions = []
    for feature in root['features']:
        region = Region()
        region.geometry_json = feature['geometry']
        region.properties = feature['properties']
        region.name = region.properties['name']
        region.code = region.properties['adcode']
        regions.append(region)
    return regions


def load_citys(province_code):
    regions = [Region(name='全部')]
    file_path = 'geojson/%s.geojson' % province_code
    if not os.path.exists(file_path):
        return regions
    with open(file_path, 'r', encoding='UTF-8') as f:
        root = json.load(f)
    for feature in root['features']:
        region = Region()
        region.geometry_json = feature['geometry']
        region.properties = feature['properties']
        region.name = region.properties['name']
        region.code = region.properties['adcode']
        regions.append(region)
    return regions


def load_districts(city_code):
    regions = [Region(name='全部')]
    file_path = 'geojson/%s.geojson' % city_code
    if os.path.exists(file_path):
        return regions
    with open(file_path, 'r', encoding='UTF-8') as f:
        root = json.load(f)
    for feature in root['features']:
        region = Region()
        region.geometry_json = feature['geometry']
        region.properties = feature['properties']
        region.name = region.properties['name']
        region.code = region.properties['adcode']
        regions.append(region)
    return regions


def intersects_json(geometry_json, quadNode: QuadNode):
    geometry = shape(geometry_json)
    return intersects(geometry, quadNode)


def intersects(geometry, quadNode: QuadNode):
    quad = Polygon([(quadNode.minx, quadNode.maxy),
                   (quadNode.maxx, quadNode.maxy),
                   (quadNode.maxx, quadNode.miny),
                   (quadNode.minx, quadNode.miny),
                   (quadNode.minx, quadNode.maxy)])
    return geometry.intersects(quad)


if __name__ == '__main__':
    provinces = load_provinces()
    for province in provinces:
        citys = load_citys(province.code)
        print(province.name)
        print(','.join([x.name for x in citys]))
