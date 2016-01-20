# -*- coding: utf-8 -*-

import os
import shutil
import unicodedata
import webbrowser

import requests
from requests.exceptions import RequestException
from wox import Wox

NODE_ICO_PATH = r'img\node'
PLUGIN_ICO = r'img\v2ex.png'

LATEST = 'http://www.v2ex.com/api/topics/latest.json'
HOT = 'http://www.v2ex.com/api/topics/hot.json'

NEW_ISSUE = 'https://github.com/wenLiangcan/V2EX.wox/issues/new'


class Main(Wox):

    def query(self, param):
        endpoint = HOT if param.strip() == 'h' else LATEST
        result = []
        try:
            news = requests.get(endpoint).json()

            for i in news:
                avatar = i['node']['avatar_large']
                i['img'] = (
                    'http://www.v2ex.com' + avatar if avatar.startswith('/static') else 'http:' + avatar,
                    avatar.split('/')[-1].split('?')[0]
                )

            self.__get_node_img(set([i['img'] for i in news]))
            result = [{
                'Title': i['title'],
                'SubTitle': u'{node} • {author} • 回复 {replies}'.format(
                    node=i['node']['title'],
                    author=i['member']['username'],
                    replies=i['replies']
                ),
                'IcoPath': os.path.join(NODE_ICO_PATH, i['img'][1]),
                'JsonRPCAction': {
                    'method': 'open_url',
                    'parameters': [i['url']]
                }
            } for i in news]

        except RequestException:
            result = [{
                'Title': 'Failed to retrieve data, please check your network connection and try it later',
                'IcoPath': PLUGIN_ICO,
            }]
        except KeyError:
            result = [{
                'Title': 'Failed to parse data, possibly the plugin is broken',
                'SubTitle': 'Press enter to open browser and report this issue',
                'IcoPath': PLUGIN_ICO,
                'JsonRPCAction': {
                    'method': 'open_url',
                    'parameters': [NEW_ISSUE],
                },
            }]

        return result

    def open_url(self, url):
        webbrowser.open(url)

    def __get_node_img(self, imgs):
        url = 0
        name = 1

        plugin_path = os.path.dirname(os.path.realpath(__file__))
        d = os.path.join(plugin_path, NODE_ICO_PATH)
        if not os.path.exists(d):
            os.makedirs(d)

        existed = os.listdir(d)
        imgs = filter(lambda i: i[name] not in existed, imgs)

        def download(img):
            r = requests.get(img[url], stream=True)
            if r.status_code == 200:
                with open(os.path.join(d, img[name]), 'wb') as f:
                    r.raw.decode_content = True
                    shutil.copyfileobj(r.raw, f)

        try:
            map(download, imgs)
        except:
            pass


if __name__ == '__main__':
    Main()

