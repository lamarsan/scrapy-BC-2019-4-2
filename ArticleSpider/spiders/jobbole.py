# -*- coding: utf-8 -*-
import datetime
import re
from urllib import parse

import scrapy
from scrapy.http import Request
from w3lib.html import remove_tags

from ArticleSpider.items import JobBoleArticleItem, ArticleItemLoader
from ArticleSpider.utils.common import get_md5

from scrapy.loader import ItemLoader


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com/all-posts/']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        """
        1:解析获取到的url
        2:获取下一页的url交给scrapy
        """
        # 解析列表页的所有url
        post_nodes = response.css('#archive .floated-thumb .post-thumb a')
        for post_node in post_nodes:
            print(post_node)
            image_url = post_node.css("img::attr(src)").extract_first("")
            post_url = post_node.css("::attr(href)").extract_first("")
            yield Request(url=parse.urljoin(response.url, post_url), meta={"front_image_url": image_url},
                          callback=self.parse_detail, dont_filter=True)

        # 提取下一页url
        next_url = response.css('.next.page-numbers::attr(href)').extract_first("")
        if next_url:
            print(next_url)
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse, dont_filter=True)

    def parse_detail(self, response):
        # article_item = JobBoleArticleItem()
        # xpath
        # title = response.xpath('//*[@id="post-114641"]/div[1]/h1/text()').extract_first("")
        # create_data = response.xpath('//*[@id="post-114641"]/div[2]/p/text()').extract_first("").strip().replace("·",
        #                                                                                                     "").strip()
        # praise_nums = int(response.xpath('//*[@id="post-114641"]/div[3]/div[3]/span[1]/h10/text()').extract_first(""))
        # fav_nums = response.xpath('//*[@id="post-114641"]/div[3]/div[3]/span[2]/text()').extract_first("")
        # match_re = re.match(".*?(\d+).*", fav_nums)
        # if match_re:
        #     fav_nums = int(match_re.group(1))
        # comment_nums = response.xpath('//*[@id="post-114641"]/div[3]/div[3]/a/span/text()').extract_first("")
        # match_re = re.match(".*?(\d+).*", comment_nums)
        # if match_re:
        #     comment_nums = int(match_re.group(1))
        # content = response.xpath('//div[@class="entry"]').extract_first("")
        # tag_list = response.xpath('//*[@id="post-114641"]/div[2]/p/a/text()').extract()
        # tag_list = [element for element in tag_list if not element.strip().endswith("评论")]
        # tags = ",".join(tag_list)

        # css
        # 文章封面图
        # front_image_url = response.meta.get("front_image_url", "")
        # title = response.css('.entry-header h1::text').extract_first("")
        # create_date = response.css('p.entry-meta-hide-on-mobile::text').extract_first("").strip().replace("·",
        #                                                                                                   "").strip()
        # try:
        #     create_date = datetime.datetime.strptime(create_date, "%Y/%m/%d").date()
        # except Exception as e:
        #     create_date = datetime.datetime.now().date()
        # praise_nums = int(response.css('.vote-post-up h10::text').extract_first(""))
        # fav_nums = response.css('.bookmark-btn::text').extract_first("")
        # match_re = re.match(".*?(\d+).*", fav_nums)
        # if match_re:
        #     fav_nums = int(match_re.group(1))
        # else:
        #     fav_nums = 0
        # comment_nums = response.css('a[href="#article-comment"] span::text').extract_first("")
        # match_re = re.match(".*?(\d+).*", comment_nums)
        # if match_re:
        #     comment_nums = int(match_re.group(1))
        # else:
        #     comment_nums = 0
        # content = response.css('div.entry').extract_first("")
        # content = remove_tags(content)  # 去掉前端tag
        # content = re.sub(r'[\t\r\n\s]', '', content)  # 去掉转义字符
        # tag_list = response.css('p.entry-meta-hide-on-mobile a::text').extract()
        # tag_list = [element for element in tag_list if not element.strip().endswith("评论")]
        # tags = ",".join(tag_list)
        #
        # article_item["url_object_id"] = get_md5(response.url)
        # article_item["title"] = title
        # article_item["url"] = response.url
        # article_item["create_date"] = create_date
        # article_item["front_image_url"] = [front_image_url]
        # article_item["praise_nums"] = praise_nums
        # article_item["fav_nums"] = fav_nums
        # article_item["comment_nums"] = comment_nums
        # article_item["tags"] = tags
        # article_item["content"] = content
        # 到pipeline
        # 通过ItemLoader加载item
        front_image_url = response.meta.get("front_image_url", "")  # 文章封面图
        item_loader = ArticleItemLoader(item=JobBoleArticleItem(), response=response)
        item_loader.add_css("title", ".entry-header h1::text")
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", get_md5(response.url))
        item_loader.add_css("create_date", "p.entry-meta-hide-on-mobile::text")
        item_loader.add_value("front_image_url", [front_image_url])
        item_loader.add_css("praise_nums", ".vote-post-up h10::text")
        item_loader.add_css("comment_nums", "a[href='#article-comment'] span::text")
        item_loader.add_css("fav_nums", ".bookmark-btn::text")
        item_loader.add_css("tags", "p.entry-meta-hide-on-mobile a::text")
        item_loader.add_css("content", "div.entry")
        article_item = item_loader.load_item()
        yield article_item
