# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request


class LagouSpider(CrawlSpider):
    name = 'lagou'
    allowed_domains = ['www.lagou.com']
    start_urls = ['https://www.lagou.com/']

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0",
        "HOST": "www.lagou.com"
    }

    rules = (
        # 根据上面分析，可以写一些规则也圈定抓取的urls
        # 爬取urls中有 zhaopin/的urls，并却对这类页面中的所有的url进行跟进follow
        Rule(LinkExtractor(allow=('.*/zhaopin/.*',)), follow=True),
        # 也可以再加规则，如果发现公司页面也进行follow然后找到公司中的发布的职位,也可以爬取到
        Rule(LinkExtractor(allow=(r'.*/gongsi/.*',)), follow=True),
        # 对页面进行根据时，如果发现/jobs/.*.html的url则说明找到了要爬取的页面，那么调用parse_item进行解析
        Rule(LinkExtractor(allow=r'/jobs/.*.html'), callback='parse_item', follow=True),
    )

    def start_requests(self):
        yield scrapy.Request(url=self.start_urls[0],
                             # cookies=cookies,
                             headers=self.headers,
                             callback=self.parse,
                             dont_filter=True)

    def _build_request(self, rule, link):
        r = Request(url=link.url, headers=self.headers, callback=self._response_downloaded)
        r.meta.update(rule=rule, link_text=link.text)
        return r

    def parse_job(self, response):
        print(response)
        item = {}
        # item['domain_id'] = response.xpath('//input[@id="sid"]/@value').get()
        # item['name'] = response.xpath('//div[@id="name"]').get()
        # item['description'] = response.xpath('//div[@id="description"]').get()
        return item
