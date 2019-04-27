from .Until.LogHandler import MyLogHandler
import re
import threading
import time

LOG_NAME = 'SinaSpider'
logger = MyLogHandler(LOG_NAME)


class SinaSpider(object):

    def __init__(self, user_info_table, sina_artical_table, sina_comment_table, spiderThreadNum):
        self.user_info_table = user_info_table
        self.sina_artical_table = sina_artical_table
        self.sina_comment_table = sina_comment_table
        self.spiderThreadNum = spiderThreadNum

    @classmethod
    def from_settings(cls, settings):
        return cls(user_info_table=settings.get('MASTER_MYSQL_USER_TABLE'),
                   sina_artical_table=settings.get('MASTER_MYSQL_ARTICLA_TABLE'),
                   sina_comment_table=settings.get('MASTER_MYSQL_COMMIT_TABLE'),
                   spiderThreadNum=settings.get('SPIDER_THREAD_NUM'))

    def multi_thread_parse(self, response_list, parse_list, thread_list):
        single_spider = self.single_spider
        for i in range(self.spiderThreadNum):
            t = threading.Thread(target=single_spider, args=(response_list, parse_list))
            thread_list.append(t)
            t.start()

    def single_spider(self, response_list, parse_list):
        while True:
            print('single_spider')
            try:
                if response_list:
                    if len(parse_list) > 20:
                        logger.info('Spider: parse_list > 20')
                        time.sleep(3)
                    print('start parse')
                    response = response_list.pop()
                    self.parse_manager(response, parse_list)
                else:
                    # TODO 如果响应列表没有响应，则需要判断是爬虫结束还是，下载器过慢
                    logger.info('Spider: response_list is None')
                    time.sleep(3)
            except Exception as e:
                print('{"msg": "%s", "function":"single_spider"}', e)

    def parse_manager(self, response, parse_list):
        user_id_pattern = re.compile(r'https://m.weibo.cn/api/container/getIndex')
        user_info_pattern = re.compile(r'https://weibo.com/.*/info')
        sina_artical_pattern = re.compile(r'')
        commit_pattern = re.compile(r'')
        if user_info_pattern.search(response.url):
            genarate = self.parse_user_info(response)
        elif user_id_pattern.search(response.url):
            genarate = self.parse_user_id(response)
        else:
            msg = 'fail to get parser, url:' % response.url
            logger.debug(msg)
            return

        parse_list.append(genarate)
        print('parse succeed')

    def parse_user_id(self, response):
        print('parse_user_id')
        # 返回用户信息页面url
        cards = response.json().get('data').get('cards')

        if len(cards) == 0:
            logger.info('fail to get response')
            logger.info(response.json())
            return
        elif len(cards) == 1:
            card_group = cards[0].get('card_group')
        else:
            card_group = cards[-1].get('card_group')

        for card in card_group:
            id = card.get('user').get('id')
            if id:
                url = 'https://weibo.com/%s/info' % str(id)
                yield url

    def parse_user_info(self, response):
        print('start parse_user_info')
        # TODO 如果没有user_id，follow_count, followers_count 则该请求重试

        user_id = re.search(r"\$CONFIG\['oid'\]='(\d*)';", response.text).group(1)

        follow_count = re.search(r'<strong class=\\"W_f\d*\\">(\d*)<\\/strong><span class=\\"S_txt2\\">关注<\\/span>', response.text, re.M)
        follow_count = follow_count.group(1) if follow_count else None

        followers_count = re.search(r'<strong class=\\"W_f\d*\\">(\d*)<\\/strong><span class=\\"S_txt2\\">粉丝<\\/span>', response.text, re.M)
        followers_count = followers_count.group(1) if followers_count else None

        weibo_count = re.search(r'<strong class=\\"W_f\d*\\">(\d*)<\\/strong><span class=\\"S_txt2\\">微博<\\/span>', response.text, re.M)
        weibo_count = weibo_count.group(1) if weibo_count else None

        weibo_grade = re.search(r'<span>Lv\.(\d*)<\\/span>', response.text, re.M)
        weibo_grade = weibo_grade.group(1) if weibo_grade else None

        verified_type = re.search(r'<em title=.*? class=\\"(W_icon.*?)\\"', response.text, re.M|re.S)
        verified_type = verified_type.group(1) if verified_type else None

        verified = 1 if verified_type else 0

        screen_name = re.search(r"\$CONFIG\['onick'\]='(.*?)'", response.text, re.M | re.S)
        screen_name = screen_name.group(1) if screen_name else None

        profile_image_url = re.search(r'<p class=\\"photo_wrap\\">.*?<img src=\\"(.*?)\\".*?class=\\"photo\\">', response.text, re.M|re.S)
        profile_image_url = 'http:' + profile_image_url.group(1).replace('\\', '') if profile_image_url else None

        page_id = re.search(r"\$CONFIG\['page_id'\]='(\d*)'", response.text, re.M)
        page_id = page_id.group(1) if page_id else None

        place = re.search(r'<span class=\\"pt_title S_txt2\\">所在地[：:]<\\/span>.*?<span class=\\"pt_detail\\">(.*?)<\\/span>', response.text, re.M|re.S)
        place = place.group(1) if place else None

        gender = re.search(r'<span class=\\"pt_title S_txt2\\">性别[：:]<\\/span>.*?<span class=\\"pt_detail\\">(.*?)<\\/span>', response.text, re.M|re.S)
        gender = gender.group(1) if gender else None

        birth = re.search(r'<span class=\\"pt_title S_txt2\\">生日[:：]<\\/span>.*?<span class=\\"pt_detail\\">(.*?)<\\/span>', response.text, re.M|re.S)
        birth = birth.group(1) if birth else None

        intro = re.search(r'<div class=\\"pf_intro\\" title=\\"(.*?)\\">', response.text, re.M|re.S)
        intro = intro.group(1) if intro else None

        blood = re.search(r'<span class=\\"pt_title S_txt2\\">血型[:：]<\\/span>.*?<span class=\\"pt_detail\\">(.*?)<\\/span>', response.text, re.M|re.S)
        blood = blood.group(1) if blood else None

        blogs = re.search(r'<span class=\\"pt_title S_txt2\\">博客[:：]<\\/span>.*?<a.*?>(.*?)<\\/a>', response.text, re.M|re.S)  # None
        blogs = blogs.group(1) if blogs else None

        domainhacks = re.search(r'<span class=\\"pt_title S_txt2\\">个性域名[:：]<\\/span>.*?<span class=\\"pt_detail\\">.*?<a href=\\".*?\\">(.*?)<\\/a>', response.text, re.M|re.S)
        domainhacks = domainhacks.group(1).replace('\\', '') if domainhacks else None

        register_time = re.search(r'<span class=\\"pt_title S_txt2\\">注册时间[:：]<\\/span>.*?<span class=\\"pt_detail\\">(.*?)<\\/span>', response.text)
        register_time = register_time.group(1).replace('\\r\\n', '').replace(' ', '') if register_time else None

        college = re.search(r'<span class=\\"pt_title S_txt2\\">大学[:：]<\\/span>.*?<span class=\\"pt_detail\\">.*?<a href=\\".*?\\">(.*?)<\\/a>(.*?)<\\/span>', response.text)
        college = college.group(1) + ' ' + college.group(2).replace(' ', '').replace('\\r\\n', '').replace('<br\\/>', '') if college else None

        all_labels = ''
        labels = re.findall(r'<a.*?node-type=\\"tag\\".*?class=\\"W_btn_b W_btn_tag\\">.*?<\\/span>(.*?)<\\/a>', response.text)
        if labels:
            for label in labels:
                label = label.replace(' ', '').replace('\\r\\n', '')
                all_labels += label + '|'

        item = {
            'user_id': user_id,
            'follow_count': follow_count,
            'followers_count': followers_count,
            'weibo_count': weibo_count,
            'weibo_grade': weibo_grade,
            'verified': verified,
            'verified_type': verified_type,
            'screen_name': screen_name,
            'profile_image_url': profile_image_url,
            'page_id': page_id,
            'place': place,
            'gender': gender,
            'birth': birth,
            'intro': intro,
            'blood': blood,
            'blogs': blogs,
            'domainhacks': domainhacks,
            'register_time': register_time,
            'college': college,
            'label': all_labels,
            'table': self.user_info_table,
        }
        print(item)
        print('success parse')
        yield item

        # TODO 返回粉丝列表和关注列表的url
        base_url = 'https://m.weibo.cn/api/container/getIndex?'
        # 用户 关注列表 url
        followers_pages = int(follow_count) // 20 + 1
        if followers_pages > 250:
            followers_pages = 250
        for page in range(1, followers_pages+1):
            followers_url = base_url + 'containerid=231051_-_followers_-_{uid}&since_id={page}'.format(uid=user_id, page=page)   # 他关注的人的列表url
            yield followers_url

        # 用户 粉丝列表 url
        fans_pages = int(followers_count) // 20 +1
        if fans_pages > 250:
            fans_pages = 250
        for page in range(1, fans_pages+1):
            fans_url = base_url + 'containerid=231051_-_fans_-_{uid}&since_id={page}'.format(uid=user_id, page=page)        # 他粉丝的列表url
            yield fans_url

    def parse_sina_artical(self, response):
        pass

    def parse_commit(self, response):
        pass

    def get_etree(self, response):
        pass


if __name__ == '__main__':
    pass












