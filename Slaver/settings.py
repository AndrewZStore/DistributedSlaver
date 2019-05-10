
DEFAULT_HEADERS = {
     'Accept': 'text/html,application/xhtml+xml,image/jxr,*/*',
     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36',
     # 'Cookie': 'SUB=_2AkMr767_f8NxqwJRmfoQyGvjZIt-zw3EieKds18kJRMxHRl-yT9jqnECtRB6AG-AEDRk_BERoibYAhf8bHFZA6SDMsxl;',
     'Cookie': 'SUB=_2AkMr5VIff8NxqwJRmP4RzWvgaIp1yQnEieKduaPEJRMxHRl-yj9jqn1etRB6AGV88DTVWXouiQuMTMXraIqjwaw9Tk3i;',
     # TODO 思考，因为cookies的不同，可能会导致有些人的有些数据拿不了，是不是一个cookie对应一个人的请求
     # TODO 验证cookie有效时间  start:2019.04.15  09:35    end:
     # TODO 维护cookie池
     # 'Cookie': 'SUB=_2A25xt666DeRhGeVG6FoT9yfIzzSIHXVSxIdyrDV8PUNbmtBeLVj3kW9NT7mmwZqWAvQLJ6c-W8DfSBib0lF3aSrR;'
}


MAX_CONCURRENT_REQUESTS = 1
MASTER_MYSQL_HOST = '127.0.0.1'
MASTER_MYSQL_PORT = 3306
MASTER_MYSQL_USER = 'root'
MASTER_MYSQL_PASSWORD = '123456'
MASTER_MYSQL_DATABASE = 'sina'
MASTER_MYSQL_USER_TABLE = 'userinfo'
MASTER_MYSQL_ARTICLA_TABLE = 'ArticalInfo'
MASTER_MYSQL_COMMIT_TABLE = 'CommitInfo'


MASTER_REDIS_HOST = '106.13.147.213'            #'155.138.229.23'
MASTER_REDIS_PORT = 6379
MASTER_REDIS_PASSWORD = None  #'123456'


MASTER_REQUEST_QUEUE = 'Sina_master:request_queue'
MASTER_NEW_REQUEST_QUEUE = 'Sina_master:new_request_queue'

LOCAL_REDIS_HOST = '127.0.0.1'            #'155.138.229.23'
LOCAL_REDIS_PORT = 6379
LOCAL_REDIS_PASSWORD = None  #'123456'
LOCAL_REQUEST_QUEUE = 'Sina:request_queue'


TIMEOUT = 10


SPIDER_THREAD_NUM = 4







