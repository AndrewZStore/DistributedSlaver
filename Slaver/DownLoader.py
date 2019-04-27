from Slaver.Until.LogHandler import MyLogHandler
from Slaver.Until.tool import settings, redis_server
import requests
import threading
import time


LOG_NAME = 'downloader'
logger = MyLogHandler(LOG_NAME)


# TODO 错误状态码 302 303 403 404 502
class Request(object):

    def __init__(self, headers=None, proxies=None, timeout=10):
        self.headers = headers
        self.proxies = proxies
        self.timeout = timeout

    @classmethod
    def from_settings(cls, settings):
        return cls(headers=settings.get('DEFAULT_HEADERS'),
                   timeout=settings.get('TIMEOUT'))

    def headers_handler(self, header):
        if isinstance(header, dict):
            self.headers.update(header)
        else:
            logger.info("header must be dict type")

    def proxy_handler(self, proxy):
        # TODO 检测代理格式是否正确
        if isinstance(proxy, str):
            self.proxies = {'http': 'http://' + proxy,
                            'https': 'http://' + proxy}
        else:
            logger.info("proxy must be str type")

    def get(self, url, retry_flags=list(), retry_times=3, **kwargs):
        # TODO 完善重试机制，重定向机制
        while True:
            try:
                resp = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=self.timeout, **kwargs)
                resp.encoding = resp.apparent_encoding

                for flag in retry_flags:
                    if flag in resp.text:
                        raise Exception('retry flags is in response')

                print('status_code:', resp.status_code)
                if resp.status_code != 200:
                    # TODO 非200状态码处理
                    raise Exception('fail to get response')
            except Exception as e:
                logger.info(e)
                if retry_times <= 0:
                    raise Exception('Maximum number of retries exceeded!')
                retry_times -= 1
                continue

            return resp

    def get_html(self, url, **kwargs):
        resp = self.get(url, **kwargs)

        return resp


class DownLoader(object):

    def __init__(self, request_queue, max_concurrent_requests):
        self.server = redis_server()
        self.rq = request_queue
        self.max_concurrent_requests = max_concurrent_requests
        self.download_count = 0
        self.response_count = 0

    @classmethod
    def from_settings(cls, settings):
        return cls(request_queue=settings.get('LOCAL_REQUEST_QUEUE'),
                   max_concurrent_requests=settings.get('MAX_CONCURRENT_REQUESTS'),)

    def get_request(self):
        with self.server.pipeline(transaction=False) as pipe:
            pipe.zrange(self.rq, 0, 0).zremrangebyrank(self.rq, 0, 0)
            results, count = pipe.execute()
        if results:
            url = str(results[0], encoding='utf-8')

            return url

    def single_download_from_list(self, response_list):
        WebRequest = Request.from_settings(settings)
        while True:
            print('single_download')
            # TODO 如果响应队列超过一定的数量则sleep等待解析器解析
            if len(response_list) > 50:
                logger.info('DownLoader: response list > 50')
                time.sleep(3)
            url = self.get_request()
            if url:
                resp = WebRequest.get_html(url)
                self.download_count += 1
                if resp:
                    self.response_count += 1
                    response_list.append(resp)
                    print('download succeed')
            else:
                # TODO 如果url不存在，则需要判断是爬虫结束了，还是暂时数据库没有数据
                logger.info('DownLoader: request queue is None')
                time.sleep(3)
                pass

    def multi_thread_download(self, response_list, thread_list):
        sd = self.single_download_from_list
        for i in range(self.max_concurrent_requests):
            t = threading.Thread(target=sd, args=(response_list, ))
            thread_list.append(t)
            t.start()


if __name__ == '__main__':
    import redis
    conn = redis.StrictRedis(host='localhost', port=6379)
    print(conn.lpop('hell'))


