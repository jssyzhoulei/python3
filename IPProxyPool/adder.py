from db import MongodbClient
from errors import ResourceDepletionError
from get_proxy import ProxyGetter
from tester import ProxyTester
from utils import QQMailClient


class PoolAdder(object):
    """
    启动爬虫，添加代理到数据库中
    """
    def __init__(self, threshold):
        self._threshold = threshold
        self._conn = MongodbClient()
        self._tester = ProxyTester()
        self._crawler = ProxyGetter()

    def is_over_threshold(self):
        """
        判断数据库中代理数量是否达到设定阈值
        """
        return True if max(self._conn.get_count) >= self._threshold else False

    def add_to_pool(self):
        """
        补充代理
        """
        print('PoolAdder is working...')
        proxy_count = 0
        while not self.is_over_threshold():
            # 迭代所有的爬虫，元类给ProxyGetter的两个方法
            # __CrawlFuncCount__是爬虫数量，__CrawlFunc__是爬虫方法
            for callback_label in range(self._crawler.__CrawlFuncCount__):
                callback = self._crawler.__CrawlFunc__[callback_label]
                raw_proxies = self._crawler.get_raw_proxies(callback)
                # 测试爬取到的代理
                self._tester.set_raw_proxies(raw_proxies)
                self._tester.test()
                proxy_count += len(raw_proxies)
                if self.is_over_threshold():
                    print('Proxy is enough, waiting to be used...')
                    break
            if proxy_count == 0:

                try:
                    qqm = QQMailClient()
                    qqm.send_mail('代理池预警', '芝麻代理云端池已空,联系供应商解决后,本服务需要重启...')
                    print('邮件发送成功...')
                except:
                    print('邮件发送异常')
                raise ResourceDepletionError

