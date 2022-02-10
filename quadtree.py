# coding=utf-8

class QuadNode:
    def __init__(self, minx: float, miny: float, maxx: float, maxy: float):
        self.minx = minx
        self.maxx = maxx
        self.miny = miny
        self.maxy = maxy
        width = self.maxx - self.minx
        height = self.maxy - self.miny
        if width > height:
            self.miny = self.maxy - width
        else:
            self.maxx = self.minx + height

    def width(self):
        return self.maxx - self.minx

    def height(self):
        return self.maxy - self.miny

    def width_meter(self):
        return self.width() * 111111.111111

    def height_meter(self):
        return self.height() * 111111.111111

    def split(self):
        midlon = self.minx + (self.maxx - self.minx) / 2
        midlat = self.miny + (self.maxy - self.miny) / 2
        nodes = [
            QuadNode(self.minx, midlat, midlon, self.maxy),
            QuadNode(midlon, midlat, self.maxx, self.maxy),
            QuadNode(self.minx, self.miny, midlon, midlat),
            QuadNode(midlon, self.miny, self.maxx, midlat)
        ]
        return nodes

    def to_amap_polygon(self):
        return '%f,%f|%f,%f' % (self.minx, self.miny, self.maxx, self.maxy)

    @staticmethod
    def from_amap_polygon(polygon_str: str):
        pts = polygon_str.split('|')
        min_pt = pts[0].split(',')
        max_pt = pts[1].split(',')
        minx, miny, maxx, maxy = float(min_pt[0]), float(min_pt[1]), float(max_pt[0]), float(max_pt[1])
        return QuadNode(minx, miny, maxx, maxy)
