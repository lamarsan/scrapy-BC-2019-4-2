# -*- coding: utf-8 -*-
import scrapy
import re
from urllib import parse
from scrapy.http import Request
from scrapy.loader import ItemLoader
from ArticleSpider.items import WaiBaoItem


class WaibaoSpider(scrapy.Spider):
    name = 'waibao'
    allowed_domains = ['www.xianjichina.com/require.html']
    start_urls = ['https://www.xianjichina.com/require/page_81.html']
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36",
        "HOST": "www.xianjichina.com/require.html"
    }

    def parse(self, response):
        print("*" * 40)
        # 解析列表页的所有url
        post_nodes = response.css('.saloon .content-left .dtitle h2 a')
        for post_node in post_nodes:
            print(post_node)
            post_url = post_node.css("::attr(href)").extract_first("")
            print(post_url)
            url = parse.urljoin(response.url, post_url)
            print(url)
            yield Request(url=url,
                          callback=self.parse_detail, dont_filter=True)

        # 提取下一页url
        next_url = response.css('.page .next_page a::attr(href)').extract_first("")
        if next_url:
            print(next_url)
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse, dont_filter=True)

    def parse_detail(self, response):
        p = response.css('.number p::text').extract()
        match_re = re.match(".*('所在地.*')+", str(p))
        if match_re:
            location = match_re.group(1)
        else:
            location = 'null'
        type1 = response.css('.bread a::text').extract()[2]
        type2 = response.css('.number p a::text').extract_first("")
        type = type1 + "," + type2
        id = response.css('.number p::text').extract_first("")
        state = response.css('.number p::text').extract()[1]
        item_loader = ItemLoader(item=WaiBaoItem(), response=response)
        item_loader.add_css("title", ".number h2::text")
        item_loader.add_css("content", ".p10")
        item_loader.add_value("url", response.url)
        item_loader.add_value("id", id)
        item_loader.add_value("state", state)
        # response.css('.bread a::text').extract()[2]
        item_loader.add_value("type", type)
        item_loader.add_value("location", location)
        waibao_item = item_loader.load_item()
        yield waibao_item
