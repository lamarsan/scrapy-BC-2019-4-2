# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html
import datetime
import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst, Join
from scrapy.loader import ItemLoader
import re
from w3lib.html import remove_tags
from ArticleSpider.utils.common import extract_num
from ArticleSpider.settings import SQL_DATETIME_FORMAT, SQL_DATE_FORMAT


class ArticleSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


def date_convert(value):
    try:
        create_date = datetime.datetime.strptime(value, "%Y/%m/%d").date()
    except Exception as e:
        create_date = datetime.datetime.now().date()
    return create_date


class ArticleItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


def get_nums(value):
    match_re = re.match(".*(\d+).*", value)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0
    return nums


def remove_comment_tags(value):
    if ("评论" in value):
        return ""
    else:
        return value


def return_value(value):
    return value


def remove_content_tags(value):
    value = remove_tags(value)  # 去掉前端tag
    value = re.sub(r'[\t\r\n\s]', '', value)  # 去掉转义字符
    return value


class JobBoleArticleItem(scrapy.Item):
    title = scrapy.Field()
    create_date = scrapy.Field(
        input_processor=MapCompose(date_convert),

    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field(
        output_processor=MapCompose(return_value)
    )
    front_image_path = scrapy.Field()
    praise_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    fav_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    comment_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    tags = scrapy.Field(
        input_processor=MapCompose(remove_comment_tags),
        output_processor=Join(",")
    )
    content = scrapy.Field(
        input_processor=MapCompose(remove_content_tags)
    )

    def get_insert_sql(self):
        insert_sql = """
        insert into article(title, create_date, url, url_object_id, front_image_url, comment_nums, fav_nums, praise_nums, tags, content,front_image_path)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """

        params = (
            self["title"], self["create_date"], self["url"], self["url_object_id"], self["front_image_url"],
            self["comment_nums"], self["fav_nums"], self["praise_nums"], self["tags"], self["content"],
            self["front_image_path"])

        return insert_sql, params


class ZhihuQuestionItem(scrapy.Item):
    # 知乎的问题Item
    zhihu_id = scrapy.Field()
    topics = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    answer_num = scrapy.Field()
    comment_num = scrapy.Field()
    watch_user_num = scrapy.Field()
    click_num = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        # 插入知乎question表的insert语句
        insert_sql = """
        insert into zhihu_question(zhihu_id, topics, url, title, content, answer_num, comment_num, watch_user_num, click_num, crawl_time)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE content = VALUES(content), answer_num = VALUES(answer_num), comment_num = VALUES(comment_num), watch_user_num = VALUES(watch_user_num),click_num = VALUES(click_num)
        """

        zhihu_id = self["zhihu_id"][0]
        topics = ",".join(self["topics"])
        url = self["url"][0]
        title = "".join(self["title"])
        content = "".join(self["content"])
        answer_num = extract_num("".join(self["answer_num"]))
        comment_num = extract_num("".join(self["comment_num"]))
        watch_user_num = extract_num("".join(self["watch_user_num"][0]))
        click_num = extract_num("".join(self["watch_user_num"][1]))
        crawl_time = datetime.datetime.now().strftime(SQL_DATETIME_FORMAT)
        params = (zhihu_id, topics, url, title, content, answer_num, comment_num, watch_user_num, click_num, crawl_time)

        return insert_sql, params


class ZhihuAnswerItem(scrapy.Item):
    # 知乎的回答Item
    zhihu_id = scrapy.Field()
    url = scrapy.Field()
    question_id = scrapy.Field()
    author_id = scrapy.Field()
    content = scrapy.Field()
    praise_num = scrapy.Field()
    comment_num = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        # 插入知乎answer表的insert语句
        insert_sql = """
        insert into zhihu_answer(zhihu_id, url, question_id, author_id, content, praise_num, comment_num, create_time, update_time, crawl_time)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) 
        ON DUPLICATE KEY UPDATE content = VALUES(content),comment_num = VALUES(comment_num),praise_num = VALUES(praise_num),update_time = VALUES(update_time)
        """
        create_time = datetime.datetime.fromtimestamp(self["create_time"]).strftime(SQL_DATETIME_FORMAT)
        update_time = datetime.datetime.fromtimestamp(self["update_time"]).strftime(SQL_DATETIME_FORMAT)
        params = (
            self["zhihu_id"], self["url"], self["question_id"], self["author_id"], self["content"], self["praise_num"],
            self["comment_num"], create_time, update_time, self["crawl_time"].strftime(SQL_DATETIME_FORMAT))

        return insert_sql, params


class WaiBaoItem(scrapy.Item):
    title = scrapy.Field()
    content = scrapy.Field()
    url = scrapy.Field()
    id = scrapy.Field()
    state = scrapy.Field()
    type = scrapy.Field()
    location = scrapy.Field()

    def get_insert_sql(self):
        # 插入知乎answer表的insert语句
        insert_sql = """
        insert into demand(id, content, url, state, type, location, title)
        VALUES (%s,%s,%s,%s,%s,%s,%s) 
        ON DUPLICATE KEY UPDATE content = VALUES(content),state = VALUES(state),location = VALUES(location),title = VALUES(title)
        """

        id = str(self["id"][0])
        content = self["content"][0]
        url = self["url"][0]
        state = str(self["state"][0])
        type = self["type"][0]
        location = str(self["location"][0])
        location = location.replace("所在地：", "")
        location = location.replace("\\", "")
        location = "".join(location)
        state = state.replace("项目状态：", "")
        id = id.replace("项目编号：", "")
        title = "".join(self["title"])
        params = (id, content, url, state, type, location, title)

        return insert_sql, params
