from importlib import import_module
import redis

def get_project_settings():
    settings_dict = {}
    module = import_module('Slaver.settings')
    for key in dir(module):
        if key.isupper():
            settings_dict[key] = getattr(module, key)

    return settings_dict

settings = get_project_settings()


local_redis_host = settings.get('LOCAL_REDIS_HOST')
local_redis_port = settings.get('LOCAL_REDIS_PORT')
local_redis_password = settings.get('LOCAL_REDIS_PASSWORD')
def redis_server(host=local_redis_host, port=local_redis_port, password=local_redis_password):
    rdp = redis.BlockingConnectionPool(host=host, port=port, password=password)
    server = redis.StrictRedis(connection_pool=rdp)

    return server










