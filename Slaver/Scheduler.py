from Slaver.Until.tool import settings, redis_server
from Slaver.DownLoader import DownLoader
from Slaver.Spider import SinaSpider
from Slaver.Until.LogHandler import MyLogHandler
import pymysql
import time
import threading


LOG_NAME = 'SlaverScheduler'
logger = MyLogHandler(LOG_NAME)


class SlaverScheduler(object):

    def __init__(self, master_redis_host, master_redis_port, master_redis_password, master_request_queue, new_request_queue, mysql_host, mysql_port,
                 mysql_user, mysql_password, mysql_database, local_request_queue):
        self.mrs = redis_server(host=master_redis_host, port=master_redis_port, password=master_redis_password)
        self.lrs = redis_server()
        self.db = pymysql.connect(host=mysql_host, port=mysql_port, user=mysql_user, password=mysql_password,
                                  database=mysql_database)
        self.cursor = self.db.cursor()
        self.mrq = master_request_queue
        self.nrq = new_request_queue
        self.lrq = local_request_queue
        self.response_list = list()
        self.parse_list = list()
        self.thread_list = list()

    @classmethod
    def from_settings(cls, settings):
        return cls(master_redis_host=settings.get('MASTER_REDIS_HOST'),
                   master_redis_port=settings.get('MASTER_REDIS_PORT'),
                   master_redis_password=settings.get('MASTER_REDIS_PASSWORD'),
                   master_request_queue=settings.get('MASTER_REQUEST_QUEUE'),
                   new_request_queue=settings.get('MASTER_NEW_REQUEST_QUEUE'),
                   mysql_host=settings.get('MASTER_MYSQL_HOST'),
                   mysql_port=settings.get('MASTER_MYSQL_PORT'),
                   mysql_user=settings.get('MASTER_MYSQL_USER'),
                   mysql_password=settings.get('MASTER_MYSQL_PASSWORD'),
                   mysql_database=settings.get('MASTER_MYSQL_DATABASE'),
                   local_request_queue=settings.get('LOCAL_REQUEST_QUEUE'))

    def _local_request_queue_len(self):
        return self.lrs.zcard(self.lrq)

    def from_master_get_request(self):
        # TODO 测试使用多线程从主节点获得请求，并写入本地请求队列
        while True:
            # 不停的从请求队列获取请求，当本地请求队列有超过200个请求时就休息
            if self._local_request_queue_len() > 200:
                time.sleep(3)
                continue
            print('from_master_get_request')
            with self.mrs.pipeline(transaction=False) as pipe:
                pipe.zrange(self.mrq, 0, 0, withscores=True).zremrangebyrank(self.mrq, 0, 0)
                results, count = pipe.execute()
            if results:
                req = str(results[0][0], encoding='utf-8')
                priority = results[0][1]
                self.lrs.zadd(self.lrq, {req: priority})
            else:
                logger.info('DownLoader: can not get request from master request queue')
                time.sleep(3)

    def insert_new_request(self, request, priority=0):
        self.mrs.zadd(self.nrq, {request: -priority})

    def insert_item(self, item):
        if not isinstance(item, dict):
            raise Exception('Incoming data must be dict')

        table = item.pop('table')
        fields = []
        values = []
        for key, value in item.items():
            fields.append(key)
            values.append("'%s'" % value)
        fields = ','.join(fields)
        values = ','.join(values)
        try:
            self._push(table, fields, values)
            self.commit()
            logger.info('save succeed')
        except Exception as e:
            # TODO 处理插入mysql数据库错误的情况
            logger.debug(e)

    def _push(self, table, fields, values):
        sql = 'INSERT INTO {table} ({fields}) values({values})'.format(table=table, fields=fields, values=values)
        self.cursor.execute(sql)

    def commit(self):
        self.db.commit()

    def send_slaver_status(self):
        # TODO master_redis_server
        pass

    def deal_parse_data(self):
        while True:
            try:
                if self.parse_list:
                    print('deal_parse_data')
                    genarate = self.parse_list.pop()
                    for item in genarate:
                        if isinstance(item, dict):
                            # 存入数据库
                            self.insert_item(item)
                        else:
                            # 插入请求队列
                            priority = 0
                            if 'info' in item:
                                priority = 100
                            self.insert_new_request(item, priority)
                else:
                    logger.info('DownLoader: parse list is None')
                    time.sleep(3)
            except Exception as e:
                print('{"msg": "%s", "function":"deal_parse_data"}', e)

    def start_downloader(self):
        print('start_downloader')
        dl = DownLoader.from_settings(settings)
        dl.multi_thread_download(self.response_list, self.thread_list)
        print('finish start_downloader')

    def start_spider(self):
        print('start_spider')
        spider = SinaSpider.from_settings(settings)
        spider.multi_thread_parse(self.response_list, self.parse_list, self.thread_list)
        print('finish start_spider')

    def run(self):
        t1 = threading.Thread(target=self.from_master_get_request)
        t2 = threading.Thread(target=self.deal_parse_data)
        self.thread_list.append(t1)
        self.thread_list.append(t2)
        t1.start()
        t2.start()
        self.start_downloader()
        self.start_spider()

        for t in self.thread_list:
            t.join()


if __name__ == '__main__':
    s = SlaverScheduler.from_settings(settings)
    s.run()



