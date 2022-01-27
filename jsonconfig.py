#!usr/bin/env python
# -*- coding:utf-8 _*-

import os
import json


class JsonConfig(object):
    """配置文件封装类"""

    # 共享配置，同一个配置文件多个实例也可以共享配置
    __configs = {}

    def __init__(self, path=None, data=None, reload=True, root=None):
        """
        初始化类

        @:param path 配置文件路径
        @:param data 初始化JSON数据
        """
        self.root = root
        self.path = path
        # 从共享配置中获取配置信息
        if self.path is not None:
            if not reload and self.path in JsonConfig.__configs:
                self.data = JsonConfig.__configs[self.path]
            elif os.path.exists(self.path):
                with open(self.path, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                    JsonConfig.__configs[self.path] = self.data
            elif data is not None:
                self.data = data
            else:
                self.data = {}
        elif data is not None:
            self.data = data
        else:
            self.data = {}

    def getsection(self, k):
        if k not in self.data:
            self.data[k] = {}

        return JsonConfig(data=self.data[k], root=self)

    def getdata(self):
        return self.data

    def get(self, k, default=None):
        if k in self.data:
            return self.data[k]
        else:
            return default

    def getstring(self, k, default=''):
        if k in self.data:
            return str(self.data[k])
        else:
            return default

    def getint(self, k, default=None):
        """
        获取整型值，如果不是整形值，则强制转换，如果转换失败则返回Default
        :param k: 健名
        :param default: 默认值
        :return:
        """
        if k in self.data:
            vv = self.data[k]
            if isinstance(vv, int):
                return vv

            try:
                return int(str(vv))
            except:
                return default
        else:
            return default

    def getfloat(self, k, default=None):
        if k in self.data:
            vv = self.data[k]
            if isinstance(vv, float):
                return vv

            try:
                return float(str(vv))
            except:
                return default
        else:
            return default

    def getboolean(self, k, default=None):
        if k in self.data:
            vv = self.data[k]
            if isinstance(vv, bool):
                return vv

            try:
                return bool(str(vv))
            except:
                return default
        else:
            return default

    def getarray(self, k, default=None):
        if k not in self.data:
            return default

        vv = self.data[k]
        if not isinstance(vv, list):
            return default

        v = []
        for item in vv:
            if isinstance(item, (bool, str, int, float)):
                v.append(item)
        return v

    def getintarray(self, k):
        if k not in self.data:
            return None

        vv = self.data[k]
        if not isinstance(vv, list):
            return None

        v = []
        for item in vv:
            if isinstance(item, int):
                v.append(item)
            else:
                try:
                    v.append(int(str(item)))
                except:
                    pass
        return v

    def getbooleanarray(self, k):
        if k not in self.data:
            return None

        vv = self.data[k]
        if not isinstance(vv, list):
            return None

        v = []
        for item in vv:
            if isinstance(item, bool):
                v.append(item)
            else:
                try:
                    v.append(bool(str(item)))
                except:
                    pass
        return v

    def getfloatarray(self, k):
        if k not in self.data:
            return None

        vv = self.data[k]
        if not isinstance(vv, list):
            return None

        v = []
        for item in vv:
            if isinstance(item, float):
                v.append(item)
            else:
                try:
                    v.append(float(str(item)))
                except:
                    pass
        return v

    def getsectionarray(self, k):
        if k not in self.data:
            return None

        vv = self.data[k]
        if not isinstance(vv, list):
            return None

        v = []
        for item in vv:
            json_config = JsonConfig(data=item, root=self)
            v.append(json_config)

        return v

    def set(self, k, v, commit=False):
        """
        设置值
        :param k: 键名
        :param v: 键值
        :param commit: 是否提交写入本地配置文件
        :return:  返回self
        """
        try:
            if isinstance(v, list):
                self.__setarray(k, v)
            else:
                self.data[k] = v
            return self
        except:
            return self
        finally:
            if commit:
                self.commit()

    def commit(self):
        """
        提交所有修改并写入到本地配置文件
        :return:
        """
        if self.root is None:
            self.__flush()
        else:
            self.root.commit()

    def to_string(self):
        return json.dumps(self.data)

    def __setarray(self, k, v):
        if isinstance(v, (list, tuple)):
            self.data[k] = v
        else:
            self.data[k] = [str(v), ]

    def __flush(self):
        if self.path:
            with open(self.path, "w+", encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)

