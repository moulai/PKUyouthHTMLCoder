#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# filename: elimage.py
# modified: 2019-03-30
"""
elimage api 类

缺点：上传速度较慢
"""
'''
__all__ = [

    "ElimageClient",

    ]


import os
import time
from io import BytesIO
from functools import partial
import requests

from utils import json_dump, json_load, MD5, SHA1, Logger, Config
from errors import JSONDecodeError, SMMSUploadError, SMMSGetListError, SMMSClearError


Root_Dir = os.path.join(os.path.dirname(__file__), '../') # 项目根目录
Cache_Dir = os.path.join(Root_Dir, "cache/") # 缓存文件目录

json_dump = partial(json_dump, Cache_Dir)
json_load = partial(json_load, Cache_Dir)


class ElimageClient(object):
    """ [elimage api 类] 为图片提供外链

        Attributes:
            class:
                logger                   Logger    日志实例
                config                   Config    配置文件实例
                Image_Links_Cache_JSON   str       图片外链 json 缓存文件名
                imgLinks                 dict      图片 sha1 与图片外链的映射
    """

    logger = Logger('elimage')
    config = Config('elimage.ini')

    Image_Links_Cache_JSON = config.get('cache', 'image_links_json')

    try:
        imgLinks = json_load(Image_Links_Cache_JSON)
    except (FileNotFoundError, JSONDecodeError): # 说明文件不存在或者为空，应当至少为 {}
        imgLinks = {}

    def upload(self, filename, imgBytes, log=True):
        """ 图片上传接口

            Args:
                filename    str     图片名
                imgBytes    bytes   图片的 bytes
                log         bool    是否输出日志
            Returns:
                links       dict    该文件的外链信息 {
                                        'url': 图片链接
                                        'md5': 图片 MD5
                                        'sha1': 图片 SHA1
                                    }
        """
        imgMD5 = MD5(imgBytes)
        imgSHA1 = SHA1(imgBytes)
        links = self.imgLinks.get(imgSHA1)
        if links is not None:
            if log:
                self.logger.info('get image %s from cache' % filename)
            return links
        else:
            if log:
                self.logger.info('uploading image %s' % filename)

            resp = requests.post('https://img.vim-cn.com/', files={
                    'image': (imgSHA1 + os.path.splitext(filename)[1], BytesIO(imgBytes))
                })

            links = {
                'url': resp.text.rstrip('\n'),
                'md5': imgMD5,
                'sha1': imgSHA1,
            }
            self.imgLinks[imgSHA1] = links
            json_dump(self.Image_Links_Cache_JSON, self.imgLinks) # 缓存
            return links

'''